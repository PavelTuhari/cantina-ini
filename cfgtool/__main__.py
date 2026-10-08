# -*- coding: utf-8 -*-
"""Утилита настройки кассы.

    python -m cfgtool web [файл]        окно настройки на 127.0.0.1:8920
    python -m cfgtool list [подстрока]  показать параметры
    python -m cfgtool get ИМЯ           значение и всё, что о нём известно
    python -m cfgtool set ИМЯ ЗНАЧЕНИЕ  записать значение
    python -m cfgtool check             что в файле не так
    python -m cfgtool buttons [панель]  кнопки тачскрина в виде сетки
    python -m cfgtool scan              пересобрать справочник из исходников
    python -m cfgtool doc               пересобрать docs/cantina-ini.md

Путь к файлу задаётся первым аргументом после команды либо переменной
`UAMENU_INI`; по умолчанию берётся `Win32/Debug/cantina.ini`.
"""

from __future__ import unicode_literals

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UAMENU = os.path.dirname(HERE)
if UAMENU not in sys.path:
    sys.path.insert(0, UAMENU)

from cfgtool.catalog import Catalog, STATE_LIVE                  # noqa: E402


def out(text=""):
    sys.stdout.write(text + "\n")


def ini_path(explicit=None):
    return explicit or os.environ.get("UAMENU_INI") or None


def cmd_list(args):
    cat = Catalog(ini_path(args[1] if len(args) > 1 and
                           os.path.exists(args[1]) else None))
    needle = (args[0] if args and not os.path.exists(args[0]) else "").lower()
    rows = []
    for o in cat.in_file():
        if needle and needle not in o.name.lower() and \
                needle not in (o.note or "").lower():
            continue
        rows.append(o)
    out("{:<38} {:<22} {:<14} {}".format(
        "ПАРАМЕТР", "ЗНАЧЕНИЕ", "СОСТОЯНИЕ", "ОТКУДА"))
    for o in sorted(rows, key=lambda x: x.name.lower()):
        value = "(секрет)" if o.secret else (o.value or "")
        out("{:<38} {:<22} {:<14} {}".format(
            o.name[:38], str(value)[:22], o.state, o.source))
    out()
    out("показано {} из {}".format(len(rows), len(cat.in_file())))
    return 0


def cmd_get(args):
    if not args:
        out("не указано имя параметра")
        return 2
    cat = Catalog(ini_path())
    o = cat.get(args[0])
    if o is None:
        out("такого параметра касса не знает и в файле его нет")
        return 1
    out("{}".format(o.name))
    out("  значение      {}".format(
        "(секрет)" if o.secret else
        (o.value if o.value is not None else "(не задано)")))
    out("  состояние     {}".format(o.state))
    out("  тип           {}".format(o.kind or "строка"))
    out("  откуда        {}".format(o.source or "не определено"))
    out("  умолчание     {}".format(o.code_default or "(нет)"))
    out("  подсистема    {}".format(o.group))
    if o.choices:
        out("  варианты      {}".format(", ".join(o.choices)))
    if o.note:
        out("  что это       {}".format(o.note))
    if o.entries:
        out("  строки файла:")
        for e in o.entries:
            mark = "читается" if e.effective else (
                "отключена решёткой" if e.disabled else "перебита дублем выше")
            out("    {:>4}  {:<30} {}".format(e.index, e.clean[:30], mark))
    if o.places:
        out("  читается в коде:")
        for p in o.places[:6]:
            out("    {}:{}".format(p["file"], p["line"]))
    return 0


def cmd_set(args):
    if len(args) < 2:
        out("нужно имя и значение")
        return 2
    cat = Catalog(ini_path())
    o = cat.get(args[0])
    if o is None:
        out("такого параметра касса не знает; чтобы всё же записать, "
            "правьте файл вручную")
        return 1
    if o.secret:
        out("это секрет, записывать его утилитой не будем")
        return 1
    before = o.value
    cat.ini.set(o.name, args[1])
    written = cat.ini.save()
    out("{}: {!r} -> {!r}".format(o.name, before, args[1]))
    out("записано {} байт, прежний файл рядом с расширением .bak".format(written))
    if o.source and o.source.startswith("база"):
        out("внимание: этот параметр сначала читается из базы, и строка в "
            "файле подействует только если в базе его нет")
    return 0


def cmd_check(args):
    cat = Catalog(ini_path())
    s = cat.summary()
    out("файл       {}".format(s["файл"]))
    out("кодировка  {}{}".format(
        s["кодировка"].upper(),
        ", часть байт в неё не укладывается" if cat.ini.lossy else ""))
    out("параметров {} (действуют {}, не читаются {}, мёртвых {})".format(
        s["различных имён"], s["действуют"], s["не читаются"], s["мёртвые"]))
    dup = cat.ini.duplicates()
    if dup:
        out()
        out("Задвоенные параметры — читается первая строка сверху:")
        for name, entries in sorted(dup.items()):
            marks = ", ".join(
                "{}{}".format(e.index, "" if e.effective else " (не читается)")
                for e in entries)
            out("  {:<34} {}".format(name, marks))
    shadow = [o for o in cat.shadowed()]
    if shadow:
        out()
        out("Строки, которые касса не читает: {}".format(len(shadow)))
        for o in sorted(shadow, key=lambda x: x.name.lower())[:20]:
            why = ("перебита строкой {}".format(o.shadowed_by)
                   if o.shadowed_by else "отключена решёткой")
            out("  {:<34} {}".format(o.name, why))
        if len(shadow) > 20:
            out("  и ещё {}".format(len(shadow) - 20))
    dead = cat.dead()
    if dead:
        out()
        out("Мёртвые параметры (нет ни в одном исходнике): {}".format(len(dead)))
        out("  " + ", ".join(sorted(o.name for o in dead)))
    return 0


def cmd_buttons(args):
    """Раскладка кнопок в текстовом виде — то же, что показывает окно."""
    import oracledb
    from pypos.db import init_client
    from pypos.credentials import get_password
    from cfgtool.tsbuttons import TSLayout, commands_the_till_knows

    init_client()
    con = oracledb.connect(
        user=os.environ.get("PYPOS_USER", "bonuspos_self24"),
        password=get_password(os.environ.get("PYPOS_USER", "bonuspos_self24"),
                              os.environ.get("PYPOS_DB_ALIAS", "clouddev")),
        dsn=os.environ.get("PYPOS_DSN", "localhost:1522/FREEPDB1"))
    ts = TSLayout(con)
    known = set(k.lower() for k in commands_the_till_knows())

    if not args:
        out("{:<5} {:<8} {:<10} {}".format("ID", "СЕТКА", "ЯЧЕЕК", "СЛОИ С КНОПКАМИ"))
        for p in ts.panels():
            used = ts.used_layers(p.id)
            out("{:<5} {:<8} {:<10} {}".format(
                p.id, "{}x{}".format(p.cols, p.rows), p.capacity,
                ", ".join("{}({})".format(u["layer"], u["buttons"]) for u in used)))
        out()
        bad = ts.unsupported_commands(known)
        if bad:
            out("Кнопки с командами, которых касса не выполняет:")
            for name, n in bad:
                out("  {:<24} кнопок {}".format(name, n))
        con.close()
        return 0

    pid = int(args[0])
    layer = int(args[1]) if len(args) > 1 else 1
    lng = args[2] if len(args) > 2 else "RU"
    panel = ts.panel(pid)
    if panel is None:
        out("нет такой панели")
        con.close()
        return 1
    buttons = ts.buttons(pid, layer, lng)
    out("панель {} · сетка {}x{} · слой {} · язык {} · кнопок {}".format(
        pid, panel.cols, panel.rows, layer, lng, len(buttons)))
    out()
    by = {b.ord_id: b for b in buttons}
    width = 22
    for row in range(panel.rows or 1):
        cells = []
        for col in range(panel.cols or 1):
            ord_id = row * (panel.cols or 1) + col + 1
            b = by.get(ord_id)
            if b is None:
                cells.append(" " * width)
            else:
                mark = "!" if b.command and b.command.lower() not in known else " "
                text = (b.text or b.command or "").replace("\n", " ")
                cells.append("{}{:<{w}}".format(mark, text[:width - 1], w=width - 1))
        out("|".join(cells))
    con.close()
    return 0


def cmd_web(args):
    from cfgtool.web import serve
    path = args[0] if args and os.path.exists(args[0]) else None
    port = int(args[1]) if len(args) > 1 else 8920
    serve(path, port=port)
    return 0


def cmd_scan(args):
    from cfgtool.scan import main as scan_main
    return scan_main(args)


def cmd_doc(args):
    from cfgtool.docgen import main as doc_main
    return doc_main(args)


COMMANDS = {
    "web": cmd_web, "list": cmd_list, "get": cmd_get, "set": cmd_set,
    "check": cmd_check, "buttons": cmd_buttons, "scan": cmd_scan,
    "doc": cmd_doc,
}


def main(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    if not argv or argv[0] in ("-h", "--help", "help"):
        out(__doc__.strip())
        return 0
    cmd = argv[0]
    if cmd not in COMMANDS:
        out("неизвестная команда: {}".format(cmd))
        out(__doc__.strip())
        return 2
    return COMMANDS[cmd](argv[1:])


if __name__ == "__main__":
    sys.exit(main())
