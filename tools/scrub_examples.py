# -*- coding: utf-8 -*-
"""Собирает публичный репозиторий cantina-ini из исходников кассы:
документация, cfgtool, примеры ini с вычищенными секретами и адресами."""
import os, re, sys, glob, json, shutil, io

SRC = r"D:\RAD_Tokyo\Sources\UAMenu"
DBG = os.path.join(SRC, r"Win32\Debug")
KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uamenu-ai-testbench")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cantina-ini")

sys.path.insert(0, SRC)
from pypos import secrets as S  # noqa: E402

IP_RE = re.compile(rb"(?<![\d.])(?!127\.0\.0\.1)(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
MAIL_RE = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TOKEN_RE = re.compile(r"^(eyJ[A-Za-z0-9_\-]+\.?.*|[A-Za-z0-9+/=_\-]{32,}|ENC:.*)$")
HOST_RE = re.compile(rb"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:md|ru|com|net|org|ua|ro|eu|local|world)\b", re.I)

report = {"files": [], "hosts": set(), "ips": 0, "mails": 0}


def scrub_ini(src, dst_name):
    lines, rows, enc, bom, nl = S.scan_ini(src)
    secrets = removed = 0
    out = []
    section = ""
    for line in lines:
        s = line.strip()
        if s.startswith(b"[") and s.endswith(b"]"):
            section = s[1:-1].strip().decode(enc, "replace")
            out.append(line); continue
        commented = s.startswith((b";", b"#"))
        body = s.lstrip(b";# ") if commented else s
        if b"=" in body and body:
            key_b, _, val_b = body.partition(b"=")
            key = key_b.strip().decode(enc, "replace")
            val = val_b.strip().rstrip(b"\r").decode(enc, "replace")
            is_sec = (S.looks_secret(key) and not S.is_trivial(val)) or bool(TOKEN_RE.match(val))
            if is_sec and not S.is_marker(val):
                if commented:
                    out.append(b"; " + key_b.strip() + b"=@removed" + (b"\r" if line.endswith(b"\r") else b""))
                    removed += 1
                else:
                    marker = "@secret:%s/%s/%s" % (dst_name, section or "General", key)
                    out.append(key_b.strip() + b"=" + marker.encode(enc, "replace") + (b"\r" if line.endswith(b"\r") else b""))
                    secrets += 1
                continue
        out.append(line)
    data = b"\n".join(out)
    data, n_ip = IP_RE.subn(b"<ip>", data); report["ips"] += n_ip
    data, n_m = MAIL_RE.subn(b"<email>", data); report["mails"] += n_m
    for h in HOST_RE.findall(data):
        report["hosts"].add(h.decode("ascii", "replace").lower())
    if bom:
        data = b"\xef\xbb\xbf" + data
    return data, enc, secrets, removed, n_ip


def ini_facts(data, enc):
    text = (data[3:] if data.startswith(b"\xef\xbb\xbf") else data).decode(enc, "replace")
    facts = {}
    for key in ("PosID", "Server", "Schema", "FiscalPrinter", "User"):
        m = re.search(r"(?im)^\s*%s\s*=\s*(.*?)\s*$" % key, text)
        facts[key] = m.group(1) if m else ""
    facts["lines"] = text.count("\n") + 1
    return facts


def safe_name(name):
    name = name.replace(".ini.before-selftest", ".before-selftest.ini")
    name = re.sub(r"[ ()]+", "_", name).replace("_.", ".")
    if re.search(r"[^\x00-\x7f]", name):          # кириллица в имени - латиницей
        name = re.sub(r"[^\x00-\x7f]+", "typo", name)
    return name


def copy_tree(src, dst, skip=("__pycache__",)):
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in skip]
        rel = os.path.relpath(root, src)
        tgt = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(tgt, exist_ok=True)
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                continue
            shutil.copy2(os.path.join(root, f), os.path.join(tgt, f))


def scrub_text(path, secret_table_rows=False):
    raw = open(path, "rb").read()
    text = raw.decode("utf-8-sig")
    if secret_table_rows:
        def fix(m):
            key, val = m.group(1), m.group(3)
            if S.looks_secret(key) or TOKEN_RE.match(val.rstrip("…")):
                return "| `%s` | %s | `@secret:cantina.ini/General/%s` |" % (key, m.group(2), key)
            return m.group(0)
        text = re.sub(r"^\| `([^`]+)` \| (\d+) \| `([^`]*)` \|$", fix, text, flags=re.M)
    data = text.encode("utf-8")
    data, n = IP_RE.subn(b"<ip>", data); report["ips"] += n
    open(path, "wb").write(data)


def scrub_catalog(path):
    c = json.load(open(path, encoding="utf-8"))
    n = 0
    for name, p in c["params"].items():
        if S.looks_secret(name):
            for fld in ("default", "defaults", "values", "examples"):
                v = p.get(fld)
                if isinstance(v, str) and len(v) > 8 and "(" not in v:
                    p[fld] = "***"; n += 1
                elif isinstance(v, list):
                    p[fld] = ["***" if (isinstance(x, str) and len(x) > 8 and "(" not in x) else x for x in v]
    s = json.dumps(c, ensure_ascii=False, indent=1)
    s, m = IP_RE.subn(b"<ip>", s.encode("utf-8")); report["ips"] += m
    open(path, "wb").write(s)
    return n


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "docs"))
    os.makedirs(os.path.join(OUT, "examples"))
    os.makedirs(os.path.join(OUT, "templates"))
    os.makedirs(os.path.join(OUT, "tools"))

    # документация
    for f in ("cantina-ini.md", "secrets.md", "selftest.md", "wiki-install-cassa.html"):
        shutil.copy2(os.path.join(SRC, "docs", f), os.path.join(OUT, "docs", f))
    scrub_text(os.path.join(OUT, "docs", "cantina-ini.md"), secret_table_rows=True)
    for f in ("secrets.md", "selftest.md", "wiki-install-cassa.html"):
        scrub_text(os.path.join(OUT, "docs", f))
    shutil.copy2(os.path.join(KIT, "docs", "08-uamenu-install.md"), os.path.join(OUT, "docs", "install.md"))
    shutil.copy2(os.path.join(KIT, "docs", "03-till-config.md"), os.path.join(OUT, "docs", "bench-config.md"))
    # ссылки на документы, которых в этом репозитории нет, -> просто текст
    p = os.path.join(OUT, "docs", "bench-config.md")
    t = open(p, "rb").read().replace(b"](08-uamenu-install.md)", b"](install.md)")
    open(p, "wb").write(t)
    p = os.path.join(OUT, "docs", "selftest.md")
    t = open(p, encoding="utf-8-sig").read()
    t = re.sub(r"\[([^\]]+)\]\((?:\.\./[^)]+|bonus-algorithm\.md|loyalty-ledger\.md|fiscal-emulator\.md|"
               r"auto-close-dialogs\.md|customer-display\.md)(?:#[^)]*)?\)", r"\1", t)
    open(p, "w", encoding="utf-8", newline="\n").write(t)
    for f in ("cantina.bench.ini", "selftest.bench.ini"):
        shutil.copy2(os.path.join(KIT, "templates", f), os.path.join(OUT, "templates", f))

    # инструменты
    shutil.copytree(os.path.join(SRC, "cfgtool"), os.path.join(OUT, "cfgtool"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    n_cat = scrub_catalog(os.path.join(OUT, "cfgtool", "catalog.json"))
    for f in ("web.py", "__main__.py"):          # внутренний адрес базы владельца -> локальная Free
        p = os.path.join(OUT, "cfgtool", f)
        t = re.sub(rb"(?:\d{1,3}\.){3}\d{1,3}:1521/clouddev\.world", b"localhost:1522/FREEPDB1", open(p, "rb").read())
        open(p, "wb").write(t)
    p = os.path.join(OUT, "cfgtool", "README.md")
    t = open(p, encoding="utf-8-sig").read()
    t = re.sub(r"\[([^\]]+)\]\(\.\./docs/erp-price-boundary\.md(?:#[^)]*)?\)", r"\1", t)
    open(p, "w", encoding="utf-8", newline="\n").write(t)
    shutil.copytree(os.path.join(SRC, "docs", "shots", "cfgtool"), os.path.join(OUT, "docs", "shots", "cfgtool"))
    for f in ("README.md", ".gitignore"):
        shutil.copy2(os.path.join(os.path.dirname(OUT), "cantina-ini-" + f.lstrip(".")), os.path.join(OUT, f))
    shutil.copy2(os.path.join(SRC, "pypos", "secrets.py"), os.path.join(OUT, "tools", "secrets.py"))
    shutil.copy2(os.path.abspath(__file__), os.path.join(OUT, "tools", "scrub_examples.py"))

    # примеры
    files = sorted(set(glob.glob(os.path.join(DBG, "*cantina*.ini*")) + glob.glob(os.path.join(DBG, "selftest*.ini"))),
                   key=lambda p: os.path.basename(p).lower())
    rows = []
    for src in files:
        name = safe_name(os.path.basename(src))
        data, enc, sec, rem, n_ip = scrub_ini(src, name)
        open(os.path.join(OUT, "examples", name), "wb").write(data)
        f = ini_facts(data, enc)
        f.update(name=name, enc=enc, secrets=sec, removed=rem, ips=n_ip)
        rows.append(f)
        report["files"].append(f)

    # таблица примеров
    with io.open(os.path.join(OUT, "examples", "README.md"), "w", encoding="utf-8", newline="\n") as w:
        w.write("# Примеры `cantina.ini`\n\n")
        w.write("Все файлы — реальные настройки касс из рабочего каталога владельца, "
                "собранные за несколько лет для разных торговых точек и интеграций. "
                "Перед публикацией каждый файл прошёл через `tools/scrub_examples.py`: "
                "пароли, ключи и токены заменены пометками `@secret:<файл>/<секция>/<ключ>` "
                "(так их читает касса из реестра, см. `docs/secrets.md`), закомментированные "
                "секреты — на `@removed`, IP-адреса — на `<ip>`, почта — на `<email>`. "
                "Остальное — байт в байт, включая кодировку (CP1251 либо UTF-8 с BOM) и дубли строк.\n\n")
        w.write("Как касса выбирает файл и почему его нельзя копировать между точками — "
                "`docs/install.md`. Что значит каждый ключ — `docs/cantina-ini.md`.\n\n")
        w.write("| Файл | Строк | Кодировка | PosID | Server | Schema | FiscalPrinter | Секретов → пометки | Удалено комментариев |\n")
        w.write("|---|---:|---|---|---|---|---|---:|---:|\n")
        for f in rows:
            w.write("| [%s](%s) | %d | %s | %s | %s | %s | %s | %d | %d |\n" % (
                f["name"], f["name"], f["lines"], f["enc"], f["PosID"] or "—", f["Server"] or "—",
                f["Schema"] or "—", f["FiscalPrinter"] or "—", f["secrets"], f["removed"]))

    print("files:", len(rows), "secrets->markers:", sum(r["secrets"] for r in rows),
          "removed:", sum(r["removed"] for r in rows), "ips masked:", report["ips"],
          "mails:", report["mails"], "catalog masked:", n_cat)
    print("hosts seen:", ", ".join(sorted(report["hosts"])))


if __name__ == "__main__":
    main()
