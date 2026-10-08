# -*- coding: utf-8 -*-
"""Сборка справочника по файлу настроек в Markdown.

Документация не пишется руками и потому не расходится с кодом: всё, кроме
пояснений на русском, извлекается из исходников кассы и из самого файла.

Запуск: `python -m cfgtool.docgen` — собирает `docs/cantina-ini.md`.
"""

from __future__ import unicode_literals

import io
import os
import sys

from cfgtool.catalog import Catalog, STATE_LIVE, STATE_SHADOWED, STATE_DEAD

HERE = os.path.dirname(os.path.abspath(__file__))
UAMENU = os.path.dirname(HERE)
OUT = os.path.join(UAMENU, "docs", "cantina-ini.md")

HEAD = """# Файл настроек кассы `cantina.ini`

Полный справочник по файлу, которым настраивается UAMenu. Собран из самих
исходников кассы: каждый параметр найден по месту, где касса его читает,
вместе с типом, значением по умолчанию и порядком, в котором смотрятся файл
и база. Поэтому справочник не расходится с кодом и пересобирается командой

```bash
python -m cfgtool.scan     # пересобрать сведения из исходников
python -m cfgtool.docgen   # пересобрать этот документ
```

Настраивать файл удобнее не руками, а
[утилитой настройки](../cfgtool/README.md): она показывает те же сведения
рядом с каждым параметром и не даёт испортить файл.

---

## Что это за файл

| | |
|---|---|
| Где лежит | рядом с `UAMenu.exe`, имя задаётся при запуске |
| Секция | одна: `[General]` |
| Кодировка | %(encoding)s |
| Строк | %(lines)s, из них с параметрами %(entries)s |
| Различных имён | %(names)s |

Имя файла касса берёт из командной строки, поэтому рядом с exe лежат десятки
вариантов: `cantina_rogob.ini`, `POS_cantina.ini`, `cantina_LOCAL.ini` и
прочие. Справочник собран по `Win32/Debug/cantina.ini`; остальные устроены так
же.

## Как касса читает параметр

Значение берётся не только из файла. У кассы есть вторая кладовая —
таблица параметров в базе, и порядок обращения к ним зависит от того, каким
вызовом написано чтение в коде.

| Порядок | Когда так | Что это значит на практике |
|---|---|---|
| файл, затем база | `ReadStrParam(rpmIniFirst, …)` | строка в файле сильнее записи в базе |
| база, затем файл | `ReadStrParam(rpmDBFirst, …)` | запись в базе сильнее строки в файле |
| только файл | `ReadIniBoolean(…)`, прямое чтение | база не смотрится |
| только база | `UAParams.Read…(…)` | файл не смотрится, строка в нём бесполезна |

В справочнике порядок указан у каждого параметра. **Если написано «база,
затем файл», правка файла может не дать ничего** — сначала посмотрите, нет ли
записи в базе.

Пустое значение равносильно отсутствию строки: касса проверяет прочитанное на
пустоту и идёт дальше по цепочке, вплоть до значения по умолчанию из кода.

## Как устроены строки файла

Это обычный ini Windows, и читает его `TIniFile`, то есть функция
`GetPrivateProfileString`. Её поведение проверено на живой системе, и четыре
свойства стоит знать до того, как править файл.

**При двух строках с одним именем побеждает первая сверху, а не последняя.**
Дописать исправление в конец файла — обычная ошибка: оно не подействует.

**Комментарий — только точка с запятой.** Строка, начинающаяся с `#`, не
комментарий: решётка становится частью имени, и параметр просто перестаёт
читаться под своим именем. Работает это как выключатель и потому встречается в
файле часто, но понимать это надо правильно.

**Точка с запятой внутри значения хвостом не отрезается.** `Path=C:\\a ; note`
даст значение `C:\\a ; note` целиком.

**Регистр имени не важен**, пробелы вокруг знака равенства и по краям значения
отбрасываются, обрамляющие двойные кавычки снимаются.

## Состояния параметров в этом файле

| Состояние | Сколько | Что значит |
|---|---|---|
| действует | %(live)s | строка есть, касса её читает |
| не читается | %(shadowed)s | строка есть, но перебита дублем выше или отключена решёткой |
| мёртвая | %(dead)s | имени нет ни в одном исходнике: строка не делает ничего |

Касса знает %(known)s параметров всего; %(absent)s из них в этом файле не
записаны и работают со значениями по умолчанию.

"""


def esc(text):
    """Экранирование для ячейки таблицы.

    Значения могут содержать байты, не уложившиеся в кодировку файла: в
    `cantina.ini` так записан зашифрованный `APIKey`. Они приходят сюда
    суррогатами, которые нельзя записать в UTF-8, поэтому заменяются точкой.
    """
    if text is None:
        return ""
    s = "{}".format(text)
    if any("\ud800" <= c <= "\udfff" for c in s):
        s = "".join("·" if "\ud800" <= c <= "\udfff" else c for c in s)
    return s.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def short(text, n=60):
    t = "{}".format(text)
    return t if len(t) <= n else t[:n - 1] + "…"


def value_cell(opt):
    if opt.secret:
        return "*(секрет, не показывается)*"
    v = opt.value
    if v is None:
        return ""
    if v == "":
        return "*(пусто — значит не задан)*"
    return "`{}`".format(esc(short(v, 48)))


def places_cell(opt):
    seen, out = set(), []
    for p in opt.places:
        key = p["file"]
        if key in seen:
            continue
        seen.add(key)
        out.append("{}:{}".format(p["file"].split("/")[-1], p["line"]))
        if len(out) >= 2:
            break
    extra = len(set(p["file"] for p in opt.places)) - len(out)
    if extra > 0:
        out.append("и ещё {}".format(extra))
    return ", ".join(out)


def section_options(f, options):
    f.write("| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |\n")
    f.write("|---|---|---|---|---|---|\n")
    for o in options:
        mark = "" if o.state == STATE_LIVE else " ⚠"
        f.write("| `{}`{} | {} | {} | {} | {} | {} |\n".format(
            esc(o.name), mark, value_cell(o), esc(o.kind), esc(o.source),
            "`{}`".format(esc(short(o.code_default, 28))) if o.code_default else "",
            esc(places_cell(o))))
    f.write("\n")
    notes = [o for o in options if o.note]
    if notes:
        for o in notes:
            line = "**`{}`** — {}".format(o.name, o.note)
            if o.choices:
                line += " Возможные значения: {}.".format(
                    ", ".join("`{}`".format(c) for c in o.choices))
            f.write(line + "\n\n")


def write(cat, path=OUT):
    s = cat.summary()
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(HEAD % {
            "encoding": s["кодировка"].upper(),
            "lines": s["строк в файле"],
            "entries": s["строк с параметрами"],
            "names": s["различных имён"],
            "live": s["действуют"],
            "shadowed": s["не читаются"],
            "dead": s["мёртвые"],
            "known": s["известно кассе всего"],
            "absent": s["не указано в файле"],
        })

        shadowed = cat.shadowed()
        if shadowed:
            f.write("---\n\n## Строки, которые касса не читает\n\n")
            f.write("Их {} . Каждая из них выглядит как настройка, но ни на "
                    "что не влияет.\n\n".format(len(shadowed)))
            f.write("| Параметр | Строка | Значение | Почему не читается |\n")
            f.write("|---|---|---|---|\n")
            for o in sorted(shadowed, key=lambda x: x.name.lower()):
                last = o.entries[-1]
                why = ("перебита строкой {}".format(o.shadowed_by)
                       if o.shadowed_by else "отключена решёткой")
                f.write("| `{}` | {} | `{}` | {} |\n".format(
                    esc(o.name), last.index, esc(short(last.clean, 34)), why))
            f.write("\n")

        f.write("---\n\n## Справочник по подсистемам\n\n")
        f.write("Знаком ⚠ помечены строки, которые касса не читает.\n\n")
        for title, about, options in cat.groups():
            f.write("### {}\n\n".format(title))
            if about:
                f.write(about + "\n\n")
            section_options(f, options)

        dead = cat.dead()
        if dead:
            f.write("---\n\n## Мёртвые параметры\n\n")
            f.write(
                "Этих имён нет ни в одном исходнике кассы и ни в одном "
                "компоненте: ни как параметра, ни как строкового литерала. "
                "Строка в файле есть, смысла у неё нет. Проверено поиском по "
                "{} файлам исходников.\n\n"
                "Удалять их не обязательно, но и настраивать ими нечего. "
                "Скорее всего это следы прежних версий и чужих сборок: "
                "например семейство `Bank0_…`, `Bank1_…`, `Bank2_…` описывает "
                "выбор банка, которого в этой сборке нет.\n\n".format(
                    cat.files_scanned))
            f.write("| Параметр | Строка | Значение |\n|---|---|---|\n")
            for o in sorted(dead, key=lambda x: x.name.lower()):
                f.write("| `{}` | {} | `{}` |\n".format(
                    esc(o.name), o.line or o.entries[0].index,
                    esc(short(o.value if o.value is not None
                              else o.entries[0].clean, 40))))
            f.write("\n")

        absent = cat.absent()
        f.write("---\n\n## Что ещё умеет касса\n\n")
        f.write(
            "В файле не записано {} параметров, которые касса читать умеет. "
            "Они работают со значениями по умолчанию. Список нужен, когда "
            "поведение надо изменить, а подходящей строки в файле нет — "
            "её достаточно дописать.\n\n".format(len(absent)))
        f.write("| Параметр | Тип | Откуда берётся | По умолчанию | Где читается |\n")
        f.write("|---|---|---|---|---|\n")
        for o in sorted(absent, key=lambda x: x.name.lower()):
            f.write("| `{}` | {} | {} | {} | {} |\n".format(
                esc(o.name), esc(o.kind), esc(o.source),
                "`{}`".format(esc(short(o.code_default, 24))) if o.code_default else "",
                esc(places_cell(o))))
        f.write("\n")

        f.write("---\n\n## Как это собрано\n\n")
        f.write(
            "Просмотрено {} файлов исходников кассы и её компонентов. "
            "Каждое обращение к настройке найдено разбором вызова со счётом "
            "скобок, поэтому многострочные вызовы и вложенные выражения "
            "разобраны верно. Имя параметра берётся только из строкового "
            "литерала: там, где оно собирается в коде из кусков, параметр в "
            "справочник не попадает — выдумывать имя хуже, чем его не "
            "показать.\n\n".format(cat.files_scanned))
        f.write(
            "Поведение чтения ini проверено вызовом той самой функции "
            "Windows, которой пользуется касса, а не взято из общих "
            "соображений.\n\n"
            "Пояснения на русском живут отдельно, в "
            "`cfgtool/descriptions.py`, и при пересборке не теряются.\n")
    return path


def main(argv=None):
    cat = Catalog()
    path = write(cat)
    s = cat.summary()
    sys.stdout.write(
        "собрано: {}\nпараметров в файле: {} (действуют {}, "
        "не читаются {}, мёртвых {})\n".format(
            path, s["различных имён"], s["действуют"],
            s["не читаются"], s["мёртвые"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
