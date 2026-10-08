# -*- coding: utf-8 -*-
"""Справочник параметров, собранный из самих исходников кассы.

Документацию к настройкам легко написать один раз и получить устаревшую через
полгода. Поэтому здесь она не пишется, а **извлекается**: каждый параметр
находится по месту, где касса его читает, вместе со значением по умолчанию и
порядком, в котором смотрятся файл и база.

Касса читает настройки семью разными способами, и от способа зависит, что
победит — строка в файле или запись в `TMS_INIT_PARAMS`:

| Вызов в коде | Откуда берётся значение |
|---|---|
| `ReadStrParam(rpmIniFirst, …)` и его братья | сначала файл, потом база |
| `ReadStrParam(rpmDBFirst, …)` | сначала база, потом файл |
| `ReadIniBoolean(…)` | только файл |
| `UAParams.Read…(…)` | только база |
| `AppIniFile->ReadString("General", …)` | только файл, напрямую |
| `getButtonText(…)` | подпись интерфейса на трёх языках |
| `TSIntfID(…)` | номер набора кнопок тачскрина, обёртка над `rpmDBFirst` |

Пустое значение в файле равносильно отсутствию строки: `ReadStrParam`
проверяет результат на пустоту и идёт дальше по цепочке.

Запуск: `python -m cfgtool.scan` — пересобирает `cfgtool/catalog.json`.
"""

from __future__ import unicode_literals

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UAMENU = os.path.dirname(HERE)
SOURCES = os.path.dirname(UAMENU)
CATALOG = os.path.join(HERE, "catalog.json")

SKIP_DIRS = {
    "__history", "__astcache", "backup-20260827-161259", "__pycache__",
    ".git", ".svn", "Schemas", "docs", "erp", "pypos", "cfgtool", "Win32",
    "Old Scales Interfobos", "Img", "TS_img",
}
SKIP_FILES = {"dtmod_bad.cpp"}
EXTENSIONS = (".cpp", ".h", ".hpp")

# Как называется способ чтения и что он означает
READERS = [
    (re.compile(r"\b(ReadStrParam|ReadIntParam|ReadBoolParam|ReadFloatParam"
                r"|ReadDateParam)\s*\("), "param"),
    (re.compile(r"\b(TSIntfID)\s*\("), "tsintf"),
    (re.compile(r"\b(getButtonText)\s*\("), "caption"),
    (re.compile(r"\b(ReadIniBoolean|ReadIniString|ReadIniInteger)\s*\("), "ini"),
    (re.compile(r"\bUAParams\s*\.\s*(ReadString|ReadInteger|ReadBoolean)\s*\("),
     "db"),
    (re.compile(r"AppIniFile\s*->\s*(ReadString|ReadInteger|ReadBool"
                r"|ReadFloat)\s*\("), "appini"),
    (re.compile(r"\b(WriteStrParam)\s*\("), "write"),
]

KIND_BY_FUNC = {
    "ReadBoolParam": "булево", "ReadIniBoolean": "булево",
    "ReadBoolean": "булево", "ReadBool": "булево",
    "ReadIntParam": "целое", "ReadInteger": "целое",
    "ReadIniInteger": "целое", "TSIntfID": "целое",
    "ReadFloatParam": "дробное", "ReadFloat": "дробное",
    "ReadDateParam": "дата",
    "getButtonText": "подпись на трёх языках",
    "ReadStrParam": "строка", "ReadString": "строка",
    "ReadIniString": "строка", "WriteStrParam": "строка",
}

SOURCE_BY_MODE = {
    "rpmIniFirst": "файл, затем база",
    "rpmDBFirst": "база, затем файл",
    "ini": "только файл",
    "db": "только база",
    "appini": "только файл",
    "caption": "файл, затем база",
    "write": "записывается кассой",
}


def decode(raw):
    """Строгий UTF-8 первым: однобайтовые кодировки прочитают что угодно."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1251", "replace")


def _split_args(s):
    """Аргументы вызова с учётом вложенных скобок и строк."""
    args, depth, cur, i, instr, q = [], 0, [], 0, False, ""
    while i < len(s):
        c = s[i]
        if instr:
            cur.append(c)
            if c == "\\" and i + 1 < len(s):
                cur.append(s[i + 1]); i += 2; continue
            if c == q:
                instr = False
        elif c in "\"'":
            instr, q = True, c
            cur.append(c)
        elif c in "([":
            depth += 1; cur.append(c)
        elif c in ")]":
            depth -= 1; cur.append(c)
        elif c == "," and depth == 0:
            args.append("".join(cur).strip()); cur = []
        else:
            cur.append(c)
        i += 1
    if cur:
        args.append("".join(cur).strip())
    return args


def _call_body(text, open_paren):
    """Текст между открывающей скобкой и парной ей закрывающей."""
    depth, i, instr, q = 0, open_paren, False, ""
    while i < len(text):
        c = text[i]
        if instr:
            if c == "\\":
                i += 2; continue
            if c == q:
                instr = False
        elif c in "\"'":
            instr, q = True, c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren + 1:i]
        i += 1
    return None


def _literal(arg):
    """Строковый литерал без кавычек и префикса L. Возвращает (текст, литерал ли)."""
    a = arg.strip()
    if a[:1] in ("L", "l") and a[1:2] == '"':
        a = a[1:]
    if len(a) >= 2 and a[0] == '"' and a[-1] == '"':
        return a[1:-1], True
    return a, False


def _tidy_default(raw):
    """Значение по умолчанию в читаемом виде."""
    d = (raw or "").strip()
    if not d:
        return ""
    text, is_lit = _literal(d)
    if is_lit:
        return text
    return d


def iter_sources(roots):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn in SKIP_FILES or not fn.lower().endswith(EXTENSIONS):
                    continue
                yield os.path.join(dirpath, fn)


def scan(roots=None):
    """Все обращения к параметрам во всех исходниках."""
    roots = roots or [UAMENU, os.path.join(SOURCES, "Cmp")]
    hits, files = [], 0
    for path in iter_sources(roots):
        text = decode(open(path, "rb").read())
        files += 1
        rel = os.path.relpath(path, SOURCES).replace("\\", "/")
        for rx, kind in READERS:
            for m in rx.finditer(text):
                op = text.index("(", m.start())
                body = _call_body(text, op)
                if body is None:
                    continue
                args = _split_args(body)
                if not args:
                    continue
                func = m.group(1)
                if kind == "param":
                    if len(args) < 2:
                        continue
                    mode = args[0].strip()
                    name, is_lit = _literal(args[1])
                    default = _tidy_default(args[2] if len(args) > 2 else "")
                elif kind == "appini":
                    if len(args) < 2:
                        continue
                    section, _ = _literal(args[0])
                    name, is_lit = _literal(args[1])
                    default = _tidy_default(args[2] if len(args) > 2 else "")
                    mode = "appini"
                    if section.lower() != "general":
                        name = section + "/" + name
                else:
                    name, is_lit = _literal(args[0])
                    default = _tidy_default(args[1] if len(args) > 1 else "")
                    mode = kind
                if not is_lit:
                    continue  # имя собирается в коде, разобрать нечем
                hits.append({
                    "name": name,
                    "func": func,
                    "mode": mode,
                    "default": default,
                    "file": rel,
                    "line": text.count("\n", 0, m.start()) + 1,
                })
    return hits, files


def build(hits):
    """Свести обращения в справочник: по одной записи на параметр."""
    by = {}
    for h in hits:
        rec = by.setdefault(h["name"], {
            "name": h["name"], "kind": "", "source": "", "default": "",
            "defaults": [], "places": [], "funcs": [], "modes": [],
        })
        rec["places"].append({"file": h["file"], "line": h["line"]})
        if h["func"] not in rec["funcs"]:
            rec["funcs"].append(h["func"])
        mode = h["mode"]
        if mode not in rec["modes"]:
            rec["modes"].append(mode)
        if h["default"] and h["default"] not in rec["defaults"]:
            rec["defaults"].append(h["default"])

    for rec in by.values():
        kinds = [KIND_BY_FUNC.get(f) for f in rec["funcs"]]
        kinds = [k for k in kinds if k]
        rec["kind"] = kinds[0] if kinds else "строка"
        sources = [SOURCE_BY_MODE.get(m) for m in rec["modes"]]
        sources = [s for s in sources if s]
        rec["source"] = sources[0] if sources else ""
        rec["default"] = rec["defaults"][0] if rec["defaults"] else ""
        rec["places"].sort(key=lambda p: (p["file"], p["line"]))
    return by


def main(argv=None):
    argv = list(argv or sys.argv[1:])
    hits, files = scan()
    by = build(hits)
    data = {
        "files_scanned": files,
        "hits": len(hits),
        "params": by,
    }
    with io.open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
    sys.stdout.write(
        "просмотрено файлов: {}\nобращений к параметрам: {}\n"
        "различных параметров: {}\nсправочник: {}\n".format(
            files, len(hits), len(by), CATALOG))
    return 0


if __name__ == "__main__":
    sys.exit(main())
