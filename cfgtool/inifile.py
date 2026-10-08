# -*- coding: utf-8 -*-
"""Файл настроек кассы: чтение и запись без потери того, что в нём есть.

Правка настроек — операция, после которой касса должна запуститься. Поэтому
правило здесь одно: всё, чего мы не трогали, обязано остаться байт в байт.
Комментарии, порядок строк, разделители из минусов, отступы, пустые строки,
кодировка, вид переводов строк — всё сохраняется.

Семантика чтения повторяет `TIniFile` из C++Builder, то есть функцию Windows
`GetPrivateProfileString`. Она проверена на живой системе, и три её свойства
важны настолько, что их стоит назвать прямо:

* при двух строках с одним именем **побеждает первая сверху**, а не последняя;
* строка, начинающаяся с `#`, комментарием не является — решётка становится
  частью имени, и параметр просто перестаёт читаться под своим именем;
  комментарий — только `;`;
* имя параметра нечувствительно к регистру, значение очищается от пробелов по
  краям и от обрамляющих двойных кавычек.

Кодировка определяется, а не назначается, и определяется не порядком проб, а
по результату. Порядок проб здесь не работает: однобайтовые кодировки
принимают почти любые байты, поэтому «успешно» прочитанный файл ещё ничего не
доказывает. Настоящий `cantina.ini` этому и научил: он записан в CP1251, но
внутри значения `APIKey=ENC:…` лежат байты, которых в CP1251 нет. Строгое
чтение в CP1251 падает, строгое чтение в CP866 проходит — и выдаёт вместо
русских комментариев псевдографику. Выбор по первой удавшейся пробе дал бы
CP866 и испортил бы файл при первой же записи.

Поэтому кодировка выбирается по содержимому: считаем, сколько получилось
кириллицы и сколько символов, которых в файле настроек взяться неоткуда
(псевдографика, редкие блоки). Выигрывает вариант с осмысленным текстом.
Байты, не отображаемые выбранной кодировкой, сохраняются суррогатами и при
записи возвращаются как были.
"""

from __future__ import unicode_literals

import io
import os
import re


ENCODINGS = ("cp1251", "cp866")

_KEY_LINE = re.compile(r"^(\s*)([^;\[=][^=]*?)(\s*)=(\s*)(.*?)(\s*)$")

# Имя настоящего параметра: буква или подчёркивание в начале, дальше буквы,
# цифры, подчёркивание, точка, дефис. Всё остальное, отключённое решёткой, —
# это комментарий, написанный через `#`, а не выключенный параметр.
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]*$")


def _score(text):
    """Насколько прочитанное похоже на текст файла настроек.

    Кириллица — в плюс. Псевдографика и прочие редкие блоки — в минус: в
    настройках кассы им взяться неоткуда, зато именно они появляются, когда
    русский текст прочитан не в той однобайтовой кодировке.
    """
    good = bad = 0
    for c in text:
        if "Ѐ" <= c <= "ӿ":
            good += 1
        elif "─" <= c <= "▟" or "←" <= c <= "⋿":
            bad += 1
    return good - 3 * bad


def detect_encoding(raw):
    """Кодировка содержимого и число байт, которые в неё не уложились."""
    try:
        raw.decode("utf-8")
        return "utf-8", 0
    except UnicodeDecodeError:
        pass

    best, best_score, best_bad = None, None, 0
    for enc in ENCODINGS:
        text = raw.decode(enc, "surrogateescape")
        bad = sum(1 for c in text if "\udc80" <= c <= "\udcff")
        score = _score(text) - bad
        if best_score is None or score > best_score:
            best, best_score, best_bad = enc, score, bad
    return best, best_bad


def decode(raw):
    """Текст, кодировка и признак того, что часть байт не уложилась в неё."""
    enc, bad = detect_encoding(raw)
    if enc == "utf-8":
        return raw.decode("utf-8"), "utf-8", False
    return raw.decode(enc, "surrogateescape"), enc, bad > 0


def clean_value(value):
    """Значение так, как его увидит касса: без пробелов по краям и без
    обрамляющих двойных кавычек."""
    v = value.strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        v = v[1:-1]
    return v


def printable(text):
    """Значение, пригодное для показа и для JSON.

    Байты, не уложившиеся в кодировку файла, живут в строке суррогатами: их
    нельзя ни записать в UTF-8, ни отдать в JSON. Для показа они заменяются
    точкой; в самом файле при записи остаются нетронутыми.
    """
    if text is None:
        return None
    if any("\ud800" <= c <= "\udfff" for c in text):
        return "".join("·" if "\ud800" <= c <= "\udfff" else c for c in text)
    return text


def as_bool(value, default=False):
    """Булево так, как его понимает C++Builder: 1/0, true/false, yes/no."""
    v = clean_value(value).lower()
    if v in ("1", "true", "yes", "y", "t"):
        return True
    if v in ("0", "false", "no", "n", "f"):
        return False
    return default


class Entry(object):
    """Одна строка вида `имя = значение`."""

    __slots__ = ("index", "key", "value", "lead", "before_eq", "after_eq",
                 "trail", "disabled", "shadowed")

    def __init__(self, index, key, value, lead="", before_eq="", after_eq="",
                 trail=""):
        self.index = index          # номер строки в файле, с единицы
        self.key = key
        self.value = value
        self.lead = lead            # отступ слева
        self.before_eq = before_eq  # пробелы перед знаком равенства
        self.after_eq = after_eq    # пробелы после знака равенства
        self.trail = trail          # пробелы в конце строки
        self.disabled = key.startswith("#")   # отключён решёткой
        self.shadowed = False       # выше есть строка с тем же именем

    @property
    def name(self):
        """Имя без решётки отключения и без пробелов вокруг неё.

        В файле отключают и так: `# FindTovarByArticol = false`. Пробел после
        решётки надо снять, иначе параметр не узнать по имени.
        """
        return self.key.lstrip("#").strip()

    @property
    def is_prose(self):
        """Это не выключенный параметр, а комментарий через решётку.

        Отличить просто: у настоящего параметра имя выглядит как имя.
        Строка `# Текст для печати в чеке (default=REDUCERE)` формально тоже
        «ключ со значением», но настройкой не является.
        """
        return self.disabled and not _NAME.match(self.name)

    @property
    def clean(self):
        return clean_value(self.value)

    @property
    def effective(self):
        """Читает ли кассa эту строку на самом деле."""
        return not self.disabled and not self.shadowed

    def render(self):
        return "{}{}{}={}{}{}".format(self.lead, self.key, self.before_eq,
                                      self.after_eq, self.value, self.trail)

    def __repr__(self):
        return "<Entry {}:{}={!r}>".format(self.index, self.key, self.value)


class IniFile(object):
    """Файл настроек: строки как есть плюс разбор параметров поверх них."""

    def __init__(self, path):
        self.path = path
        raw = open(path, "rb").read()
        text, self.encoding, self.lossy = decode(raw)
        self.bom = text.startswith("﻿")
        if self.bom:
            text = text[1:]
        self.newline = "\r\n" if "\r\n" in text else "\n"
        self.trailing_newline = text.endswith(("\n", "\r"))
        self.lines = text.replace("\r\n", "\n").split("\n")
        if self.trailing_newline and self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.size = len(raw)
        self._parse()

    # --- разбор -----------------------------------------------------------

    def _parse(self):
        self.entries = []
        self.section_of = {}
        section = ""
        for i, line in enumerate(self.lines, 1):
            s = line.strip()
            if not s:
                continue
            if s.startswith("["):
                section = s.strip("[]").strip()
                continue
            if s.startswith(";"):
                continue
            # строка-разделитель из минусов параметром не является
            if set(s) <= set("- \t"):
                continue
            m = _KEY_LINE.match(line)
            if not m:
                continue
            lead, key, before_eq, after_eq, value, trail = m.groups()
            key = key.strip()
            if not key:
                continue
            e = Entry(i, key, value, lead, before_eq, after_eq, trail)
            if e.is_prose:
                continue    # комментарий через решётку, а не параметр
            self.section_of[i] = section
            self.entries.append(e)

        # Побеждает первая строка сверху — остальные помечаем затенёнными.
        seen = set()
        for e in self.entries:
            if e.disabled:
                continue
            low = e.name.lower()
            if low in seen:
                e.shadowed = True
            else:
                seen.add(low)

    # --- чтение -----------------------------------------------------------

    def all_entries(self, name):
        low = name.lower()
        return [e for e in self.entries if e.name.lower() == low]

    def entry(self, name):
        """Строка, которую читает касса, либо None."""
        for e in self.entries:
            if e.effective and e.name.lower() == name.lower():
                return e
        return None

    def get(self, name, default=None):
        e = self.entry(name)
        return e.clean if e is not None else default

    def names(self):
        """Имена по порядку появления, без повторов."""
        out, seen = [], set()
        for e in self.entries:
            low = e.name.lower()
            if low not in seen:
                seen.add(low)
                out.append(e.name)
        return out

    def duplicates(self):
        """Имена, встречающиеся больше одного раза, с их строками."""
        by = {}
        for e in self.entries:
            if e.disabled:
                continue
            by.setdefault(e.name.lower(), []).append(e)
        return {self._display(v): v for k, v in by.items() if len(v) > 1}

    @staticmethod
    def _display(entries):
        return entries[0].name

    # --- правка -----------------------------------------------------------

    def set(self, name, value):
        """Заменить значение действующей строки. Если такой строки нет,
        параметр дописывается в конец файла."""
        value = "" if value is None else "{}".format(value)
        e = self.entry(name)
        if e is None:
            return self.add(name, value)
        e.value = value
        # Пустой «хвост» после значения: пробелы в конце строки только мешают.
        e.trail = ""
        self.lines[e.index - 1] = e.render()
        return e

    def add(self, name, value, comment=None):
        """Дописать параметр в конец файла."""
        if comment:
            self.lines.append("; " + comment)
        e = Entry(len(self.lines) + 1, name, "{}".format(value))
        self.lines.append(e.render())
        self._parse()
        return self.entry(name)

    def disable(self, index):
        """Отключить строку, поставив решётку — так это делают в самом файле."""
        line = self.lines[index - 1]
        if not line.lstrip().startswith("#"):
            lead = line[:len(line) - len(line.lstrip())]
            self.lines[index - 1] = lead + "#" + line.lstrip()
        self._parse()

    def enable(self, index):
        line = self.lines[index - 1]
        stripped = line.lstrip()
        if stripped.startswith("#"):
            lead = line[:len(line) - len(stripped)]
            self.lines[index - 1] = lead + stripped[1:]
        self._parse()

    # --- запись -----------------------------------------------------------

    def render(self):
        text = self.newline.join(self.lines)
        if self.trailing_newline:
            text += self.newline
        if self.bom:
            text = "﻿" + text
        return text

    def save(self, path=None, backup=True):
        """Записать файл. Перед записью рядом кладётся копия прежнего."""
        path = path or self.path
        text = self.render()
        errors = "surrogateescape" if self.lossy else "strict"
        try:
            data = text.encode(self.encoding, errors)
        except UnicodeEncodeError as exc:
            raise ValueError(
                "значение не записывается в кодировку файла ({}): {}".format(
                    self.encoding, exc))
        if backup and os.path.exists(path):
            with open(path, "rb") as src:
                old = src.read()
            with open(path + ".bak", "wb") as dst:
                dst.write(old)
        with open(path, "wb") as f:
            f.write(data)
        return len(data)
