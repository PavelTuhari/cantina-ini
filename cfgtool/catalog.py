# -*- coding: utf-8 -*-
"""Сведение трёх источников в одну картину по каждой настройке.

Источники:

* **исходники кассы** — откуда параметр читается, какой у него тип, какое
  значение по умолчанию и в каком порядке смотрятся файл и база
  (`cfgtool/catalog.json`, собирается `python -m cfgtool.scan`);
* **сам файл настроек** — что в нём написано сейчас, какая строка читается, а
  какая затенена дублем или отключена решёткой;
* **пояснения** — что параметр означает (`cfgtool/descriptions.py`).

Каждая настройка получает одно из трёх состояний, и это главное, ради чего
сведение делается:

| Состояние | Что значит |
|---|---|
| `действует` | строка есть в файле и касса её читает |
| `не читается` | строка есть, но касса её не видит: дубль выше или решётка |
| `мёртвая` | имени нет ни в одном исходнике — параметр не делает ничего |
| `по умолчанию` | в файле не указан, касса возьмёт значение из кода или базы |
"""

from __future__ import unicode_literals

import json
import os

from cfgtool import descriptions
from cfgtool.inifile import IniFile, as_bool

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG_JSON = os.path.join(HERE, "catalog.json")
DEFAULT_INI = os.path.join(os.path.dirname(HERE), "Win32", "Debug",
                           "cantina.ini")

STATE_LIVE = "действует"
STATE_SHADOWED = "не читается"
STATE_DEAD = "мёртвая"
STATE_ABSENT = "по умолчанию"


class Option(object):
    """Одна настройка со всем, что о ней известно."""

    def __init__(self, name, known=None, entries=None):
        self.name = name
        self.known = known or {}          # из исходников
        self.entries = entries or []      # строки файла с этим именем
        self.note = descriptions.note_for(name)
        self.choices = descriptions.choices_for(name)
        self.secret = descriptions.is_secret(name)

    # --- что известно из кода ---------------------------------------------

    @property
    def kind(self):
        return self.known.get("kind", "")

    @property
    def source(self):
        return self.known.get("source", "")

    @property
    def code_default(self):
        return self.known.get("default", "")

    @property
    def places(self):
        return self.known.get("places", [])

    @property
    def where(self):
        """Первое место чтения — по нему определяется подсистема."""
        p = self.places
        return p[0]["file"] if p else ""

    @property
    def group(self):
        title, _ = descriptions.group_for(self.where)
        return title or "Прочее"

    # --- что записано в файле ---------------------------------------------

    @property
    def entry(self):
        for e in self.entries:
            if e.effective:
                return e
        return None

    @property
    def value(self):
        e = self.entry
        return e.clean if e is not None else None

    @property
    def line(self):
        e = self.entry
        return e.index if e is not None else None

    @property
    def state(self):
        if not self.known:
            return STATE_DEAD if self.entries else STATE_ABSENT
        if self.entry is not None:
            return STATE_LIVE
        if self.entries:
            return STATE_SHADOWED
        return STATE_ABSENT

    @property
    def effective_value(self):
        """Что получит касса: значение из файла либо умолчание из кода."""
        v = self.value
        return v if v is not None else self.code_default

    @property
    def shadowed_by(self):
        """Строка, которая перебивает эту. Для дублей."""
        if self.state != STATE_SHADOWED:
            return None
        live = [e for e in self.entries if not e.disabled]
        return live[0].index if live else None

    def as_bool(self, default=False):
        v = self.effective_value
        return as_bool(v if v is not None else "", default)

    def __repr__(self):
        return "<Option {} {}={!r}>".format(self.state, self.name, self.value)


class Catalog(object):
    """Все настройки: и те, что записаны в файле, и те, что в нём не указаны."""

    def __init__(self, ini_path=None, catalog_json=None):
        self.ini_path = ini_path or DEFAULT_INI
        self.ini = IniFile(self.ini_path)
        with open(catalog_json or CATALOG_JSON, encoding="utf-8") as f:
            data = json.load(f)
        self.known = data["params"]
        self.files_scanned = data.get("files_scanned", 0)
        self._build()

    def _build(self):
        by_lower = {k.lower(): k for k in self.known}
        entries_by = {}
        for e in self.ini.entries:
            entries_by.setdefault(e.name.lower(), []).append(e)

        self.options = []
        seen = set()
        # сначала в порядке файла — так документация читается вместе с ним
        for name in self.ini.names():
            low = name.lower()
            seen.add(low)
            known_key = by_lower.get(low)
            self.options.append(Option(
                known_key or name,
                self.known.get(known_key) if known_key else None,
                entries_by.get(low, [])))
        # затем всё, что касса умеет, но в файле не записано
        for low, key in sorted(by_lower.items()):
            if low in seen:
                continue
            self.options.append(Option(key, self.known[key], []))

        self.by_name = {o.name.lower(): o for o in self.options}

    # --- выборки ----------------------------------------------------------

    def get(self, name):
        return self.by_name.get(name.lower())

    def in_file(self):
        return [o for o in self.options if o.entries]

    def live(self):
        return [o for o in self.options if o.state == STATE_LIVE]

    def shadowed(self):
        return [o for o in self.options if o.state == STATE_SHADOWED]

    def dead(self):
        return [o for o in self.options if o.state == STATE_DEAD]

    def absent(self):
        return [o for o in self.options if o.state == STATE_ABSENT]

    def groups(self):
        """Подсистемы в порядке, заданном в descriptions, с их настройками."""
        order = [t for _, t, _ in descriptions.GROUPS]
        buckets = {}
        for o in self.in_file():
            if o.state == STATE_DEAD:
                continue
            buckets.setdefault(o.group, []).append(o)
        out = []
        for title in order:
            if title in buckets:
                about = ""
                for path, t, a in descriptions.GROUPS:
                    if t == title:
                        about = a
                        break
                out.append((title, about, sorted(buckets.pop(title),
                                                 key=lambda x: x.name.lower())))
        for title in sorted(buckets):
            out.append((title, "", sorted(buckets[title],
                                          key=lambda x: x.name.lower())))
        return out

    def summary(self):
        return {
            "файл": self.ini_path,
            "кодировка": self.ini.encoding,
            "строк в файле": len(self.ini.lines),
            "строк с параметрами": len(self.ini.entries),
            "различных имён": len(self.in_file()),
            "действуют": len(self.live()),
            "не читаются": len(self.shadowed()),
            "мёртвые": len(self.dead()),
            "известно кассе всего": len(self.known),
            "не указано в файле": len(self.absent()),
            "просмотрено исходников": self.files_scanned,
        }
