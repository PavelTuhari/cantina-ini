# -*- coding: utf-8 -*-
"""Секреты кассы: из ini - в реестр пользователя под защитой DPAPI.

Значение в ini заменяется пометкой, само значение уходит в
HKCU\\Software\\Unisim\\Secrets, зашифрованное CryptProtectData:

    PosApiKey=@secret:cantina.ini/General/PosApiKey

Расшифровать его может только тот же пользователь Windows на той же
машине (с ключом --machine - любой пользователь этой машины: для касс под
служебной учётной записью). Касса читает пометки сама, через
TSecureIniFile (uSecrets.cpp); путь в реестре и соль здесь и там - одни.

    python -m pypos secrets migrate cantina.ini            что бы перенеслось
    python -m pypos secrets migrate cantina.ini --yes      перенести
    python -m pypos secrets list                           что лежит в хранилище
    python -m pypos secrets check cantina.ini              все ли пометки читаются
    python -m pypos secrets set <имя> --file p.txt         положить значение из файла
    python -m pypos secrets delete <имя>

Значения секретов не печатаются никогда - только имена и длины. Файл,
из которого читается значение (--file), после чтения затирается.
"""
from __future__ import unicode_literals
import sys, io, os, re, ctypes, ctypes.wintypes as wt

REG_ROOT = "Software\\Unisim\\Secrets"
ENTROPY = b"Unisim.Secrets.v1"      # знак в знак как в uSecrets.cpp
MARKER = "@secret"

# Имена ключей, которые считаются секретами и без подсказок по названию.
# Список - из cfgtool, там же он используется для маскировки в отчётах.
try:
    from cfgtool.descriptions import SECRETS as KNOWN_SECRETS
except Exception:
    KNOWN_SECRETS = {"PosApiKey", "MIAClientSecret", "MIAApiSecrect", "MIAApiKey",
                     "licenseKey", "License26Key", "AutorizationCod", "APIKey",
                     "APISecret", "Password"}
# И всё, что похоже на секрет по имени
SECRET_NAME = re.compile(r"(pass|secret|apikey|api_key|token|licen[cs]e.?key|"
                         r"autorizationcod|clientsecret)", re.I)
# Ключи, где слово "pass" не про пароль
NOT_SECRET = {"WalletPassTitle", "WalletPass", "PassCount"}

# ---------------------------------------------------------------- DPAPI ---

class _Blob(ctypes.Structure):
    _fields_ = [("cbData", wt.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _blob(data):
    buf = ctypes.create_string_buffer(data, len(data))
    return _Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))


def _call(name, data, flags=0):
    crypt32 = ctypes.windll.crypt32
    fn = getattr(crypt32, name)
    out = _Blob()
    ok = fn(ctypes.byref(_blob(data)), None, ctypes.byref(_blob(ENTROPY)),
            None, None, flags, ctypes.byref(out))
    if not ok:
        raise OSError("%s: код %d" % (name, ctypes.GetLastError()))
    try:
        return ctypes.string_at(out.pbData, out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(out.pbData)


def protect(value, machine=False):
    """Строка -> зашифрованные байты. machine=True - расшифрует любой
    пользователь этой машины, иначе только текущий."""
    return _call("CryptProtectData", value.encode("utf-8"), 0x4 if machine else 0)


def unprotect(blob):
    return _call("CryptUnprotectData", bytes(blob)).decode("utf-8")

# -------------------------------------------------------------- реестр ---

def _roots(machine=False):
    import winreg
    return [(winreg.HKEY_LOCAL_MACHINE if machine else winreg.HKEY_CURRENT_USER)]


def set_secret(name, value, machine=False):
    import winreg
    root = winreg.HKEY_LOCAL_MACHINE if machine else winreg.HKEY_CURRENT_USER
    blob = protect(value, machine)
    key = winreg.CreateKeyEx(root, REG_ROOT, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
    try:
        winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, blob)
    finally:
        winreg.CloseKey(key)
    if get_secret(name) != value:
        raise RuntimeError("секрет записан, но читается не тем: " + name)


def get_secret(name):
    """Значение либо None. Сначала куст пользователя, потом машины -
    в том же порядке, что и касса."""
    import winreg
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            key = winreg.OpenKey(root, REG_ROOT)
        except OSError:
            continue
        try:
            blob, kind = winreg.QueryValueEx(key, name)
        except OSError:
            continue
        finally:
            winreg.CloseKey(key)
        if kind == winreg.REG_BINARY:
            return unprotect(blob)
    return None


def has_secret(name):
    try:
        return get_secret(name) is not None
    except OSError:
        return False


def delete_secret(name, machine=False):
    import winreg
    root = winreg.HKEY_LOCAL_MACHINE if machine else winreg.HKEY_CURRENT_USER
    key = winreg.OpenKey(root, REG_ROOT, 0, winreg.KEY_SET_VALUE)
    try:
        winreg.DeleteValue(key, name)
    finally:
        winreg.CloseKey(key)


def list_secrets():
    """Имена и в каком кусте лежат. Значений здесь нет."""
    import winreg
    found = []
    for label, root in (("пользователь", winreg.HKEY_CURRENT_USER),
                        ("машина", winreg.HKEY_LOCAL_MACHINE)):
        try:
            key = winreg.OpenKey(root, REG_ROOT)
        except OSError:
            continue
        i = 0
        while True:
            try:
                name, _, _ = winreg.EnumValue(key, i)
            except OSError:
                break
            found.append((name, label))
            i += 1
        winreg.CloseKey(key)
    return found

# ----------------------------------------------------------------- ini ---

def is_marker(value):
    v = value.strip()
    return v.lower().startswith(MARKER) and (len(v) == len(MARKER) or v[len(MARKER)] == ":")


def marker_name(value, path, section, key):
    v = value.strip()
    if len(v) > len(MARKER) + 1:
        return v[len(MARKER) + 1:].strip()
    return secret_name(path, section, key)


def secret_name(path, section, key):
    return "%s/%s/%s" % (os.path.basename(path), section, key)


def looks_secret(key):
    if key in NOT_SECRET:
        return False
    return key in KNOWN_SECRETS or bool(SECRET_NAME.search(key))


# Значения, которые секретом быть не могут: флаги. Имя вроде
# NrComandReportPass=true похоже на пароль, но это "нужен ли пароль"
TRIVIAL = {"true", "false", "yes", "no", "on", "off", "0", "1", ""}


def is_trivial(value):
    v = value.strip().lower() if isinstance(value, str) else value.strip().lower().decode("latin-1", "replace")
    return v in TRIVIAL


def guess_encoding(raw):
    """Строгий UTF-8, иначе cp1251 - так устроены ini кассы. В cantina.ini
    встречаются байты, которых нет ни в одной таблице (0x98), поэтому
    кодировка нужна только для чтения значений; сам файл правится по
    байтам и остаётся байт в байт, кроме заменённых строк."""
    body = raw[3:] if raw.startswith(b"\xef\xbb\xbf") else raw
    try:
        body.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "cp1251"


def _text(data, enc):
    return data.decode(enc, "replace")


def read_ini_bytes(path):
    """Для совместимости: текст (с подменой нечитаемых байтов), кодировка,
    BOM и перевод строки. Для правки файла не используется."""
    raw = open(path, "rb").read()
    enc = guess_encoding(raw)
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if bom else raw
    nl = "\r\n" if b"\r\n" in body else "\n"
    return _text(body, enc), enc, bom, nl


def scan_ini(path):
    """Все пары ключ=значение с секциями и номерами строк. Строки - байты:
    файл потом собирается из них же."""
    raw = open(path, "rb").read()
    enc = guess_encoding(raw)
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if bom else raw
    nl = "\r\n" if b"\r\n" in body else "\n"
    lines = body.split(b"\n")
    section = ""
    rows = []
    for no, line in enumerate(lines):
        s = line.strip()
        if s.startswith(b"[") and s.endswith(b"]"):
            section = _text(s[1:-1].strip(), enc)
        elif s and not s.startswith((b"#", b";")) and b"=" in s:
            key, _, value = line.partition(b"=")
            rows.append((no, section, _text(key.strip(), enc),
                         _text(value.rstrip(b"\r"), enc)))
    return lines, rows, enc, bom, nl


def resolve(path, section, key, default=""):
    """Значение из ini, с разбором пометки - для Python-инструментов,
    которым нужно то же, что видит касса."""
    _, rows, _, _, _ = scan_ini(path)
    for _, sec, k, value in rows:
        if sec.lower() == section.lower() and k.lower() == key.lower():
            if is_marker(value):
                got = get_secret(marker_name(value, path, section, key))
                return default if got is None else got
            return value.strip()
    return default


def migrate_ini(path, apply=False, machine=False, only=None):
    """Перенос секретов одного ini. apply=False - только показать.
    Возвращает список (секция, ключ, имя, что_сделано)."""
    lines, rows, enc, bom, nl = scan_ini(path)
    report = []
    changed = False

    # Закомментированные строки с секретами: старый ключ в комментарии
    # утекает так же, как действующий. В хранилище не кладём (это мусор),
    # значение заменяем на @removed.
    for no, line in enumerate(lines):
        s = line.strip()
        if not s.startswith((b"#", b";")) or b"=" not in s:
            continue
        key, _, value = s.lstrip(b"#;").partition(b"=")
        k = _text(key.strip(), enc)
        v = value.rstrip(b"\r").strip()
        if not looks_secret(k) or not v or v == b"@removed" or is_marker(_text(v, enc)) or is_trivial(v):
            continue
        if only and k not in only:
            continue
        if apply:
            head = line.split(b"=", 1)[0]
            tail = b"\r" if line.endswith(b"\r") else b""
            lines[no] = head + b"=@removed" + tail
            changed = True
            report.append(("#", k, "", "закомментированный секрет удалён"))
        else:
            report.append(("#", k, "", "закомментированный секрет будет удалён"))

    for no, section, key, value in rows:
        if only and key not in only:
            continue
        if not looks_secret(key):
            continue
        v = value.strip()
        if not v:
            report.append((section, key, "", "пусто, пропущено"))
            continue
        if is_trivial(v):
            report.append((section, key, "", "флаг, не секрет - оставлен"))
            continue
        if is_marker(v):
            report.append((section, key, marker_name(v, path, section, key), "уже в хранилище"))
            continue
        name = secret_name(path, section, key)
        if apply:
            set_secret(name, v, machine)
            # Меняем только хвост строки после "=": ключ и перевод строки
            # остаются теми же байтами, что были
            head = lines[no].split(b"=", 1)[0]
            tail = b"\r" if lines[no].endswith(b"\r") else b""
            lines[no] = head + b"=" + ("%s:%s" % (MARKER, name)).encode(enc) + tail
            changed = True
            report.append((section, key, name, "перенесён, %d знаков" % len(v)))
        else:
            report.append((section, key, name, "будет перенесён, %d знаков" % len(v)))

    if changed:
        data = b"\n".join(lines)
        if bom:
            data = b"\xef\xbb\xbf" + data
        # Переписываем на месте: резервной копии с открытыми паролями быть
        # не должно. Строки, где секретов не было, остаются байт в байт.
        with open(path, "wb") as f:
            f.write(data)
    return report


def check_ini(path):
    """Все ли пометки в ini читаются из хранилища."""
    _, rows, _, _, _ = scan_ini(path)
    out = []
    for _, section, key, value in rows:
        if is_marker(value):
            name = marker_name(value, path, section, key)
            try:
                got = get_secret(name)
                state = "нет в хранилище" if got is None else "читается, %d знаков" % len(got)
            except OSError as error:
                state = "не расшифровался: %s" % error
            out.append((section, key, name, state))
    return out


def read_secret_file(path):
    """Значение из файла: первая строка без перевода строки. Файл после
    чтения затирается - как в conn.py password --file."""
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1251")
    value = text.split("\n")[0].rstrip("\r")
    try:
        with open(path, "wb") as f:
            f.write(os.urandom(max(len(raw), 64)))
        os.remove(path)
    except OSError:
        pass
    return value

# ----------------------------------------------------------------- CLI ---

def main(argv=None):
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    machine = "--machine" in rest
    rest = [a for a in rest if a != "--machine"]

    if cmd == "migrate":
        if not rest:
            print("нужен путь к ini"); return 2
        apply = "--yes" in rest
        paths = [a for a in rest if a != "--yes"]
        for path in paths:
            if not os.path.isfile(path):
                print("нет файла:", path); return 2
            print(("перенос" if apply else "проверка (без --yes ничего не меняется)")
                  + ": " + path)
            report = migrate_ini(path, apply=apply, machine=machine)
            if not report:
                print("  секретов не найдено")
            for section, key, name, state in report:
                print("  [%s] %-22s %-45s %s" % (section, key, name, state))
        return 0

    if cmd == "check":
        if not rest:
            print("нужен путь к ini"); return 2
        bad = 0
        for path in rest:
            print("проверка пометок:", path)
            rows = check_ini(path)
            if not rows:
                print("  пометок нет")
            for section, key, name, state in rows:
                print("  [%s] %-22s %-45s %s" % (section, key, name, state))
                if not state.startswith("читается"):
                    bad += 1
        return 1 if bad else 0

    if cmd == "list":
        rows = list_secrets()
        if not rows:
            print("хранилище пусто")
        for name, where in rows:
            print("  %-60s %s" % (name, where))
        return 0

    if cmd == "set":
        if len(rest) < 3 or rest[1] != "--file":
            print("нужно: set <имя> --file <путь>"); return 2
        name, path = rest[0], rest[2]
        if not os.path.isfile(path):
            print("нет файла:", path); return 2
        value = read_secret_file(path)
        if not value:
            print("файл пуст, ничего не записано"); return 2
        set_secret(name, value, machine)
        print("записано: %s, %d знаков; файл затёрт" % (name, len(value)))
        return 0

    if cmd == "delete":
        if not rest:
            print("нужно имя"); return 2
        delete_secret(rest[0], machine)
        print("удалено:", rest[0])
        return 0

    print("неизвестная команда:", cmd)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
