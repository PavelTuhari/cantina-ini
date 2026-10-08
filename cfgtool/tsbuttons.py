# -*- coding: utf-8 -*-
"""Кнопки режима тачскрина: чтение раскладки и её правка.

Кнопок нет в коде кассы — они лежат в базе, и форма `TFTS` их только рисует.
Поэтому «настроить кнопки» означает «поправить строки в таблицах», и вся
сложность здесь не в интерфейсе, а в том, куда именно писать.

## Где что лежит

Касса читает три представления своей схемы: `VTS_INTERFACE` (сетка панели),
`VTS_LAYERSH` (дерево слоёв) и `VTS_BUTTONS` (сами кнопки). Но это
**материализованные представления над чужой схемой** `BONUS2019_07`: писать в
них нельзя, Oracle отвечает `ORA-01732`. Ровно та же граница, что у цен, см.
`docs/erp-price-boundary.md`.

Настоящие таблицы — `XTS_INTERFACE`, `XTS_LAYERS`, `XTS_BUTTONS` — живут в
мастере и доступны через связь баз. Запись туда проверена.

## Четыре правила, без которых правка не сработает

**Команда не пишется строкой.** Колонка `INTERNAL_CMD` заполняется триггером
`XTS_BUTTONS_BIU_TRG` из справочника: `CMD_ID` плюс `PRM1` и `PRM2`. Писать
надо их, а готовую строку триггер перезапишет.

**Позиция в сетке — вычисляемая.** `VTS_BUTTONS.ORD_ID` считается оконной
функцией: сначала кнопки с заполненным `MANUAL_ORDER_ID`, затем остальные по
алфавиту подписи. Чтобы кнопка встала в нужную ячейку и осталась там, надо
заполнить `MANUAL_ORDER_ID`, а не `ORDER_ID`.

**Подпись перезаписывается, пока кнопка «автоматическая».** Триггер заполняет
`TXT_RU/RO/EN` из справочника товаров, пока `IS_AUTO` не пуст. Ручная правка
должна этот признак снимать.

**Касса увидит правку не сразу.** Между мастером и кассой стоят
материализованные представления; пока их не обновить, касса рисует прежнее.
Обновление выполняется тут же, после записи.

Отсюда же следует, как редактор показывает несохранённое. Правка лежит в
незавершённой транзакции на мастере, и обновить представление ею нельзя:
обновление читает только завершённое. Читать вместо этого прямо из мастера
тоже нельзя — представление кассы не просто копия, оно ещё и отбирает кнопки
по подразделению и склеивает подписи из справочника.

Поэтому несохранённое накладывается на прочитанное уже здесь, в `apply_edits`,
по тому же правилу сортировки, по которому порядок считает сама база:
закреплённые позиции, затем подпись по алфавиту, затем `ORDER_ID`. Так
предпросмотр совпадает с тем, что получится после применения.

## Подпись кнопки

В этой базе подпись бывает двух видов. Обычный текст, где `|` означает перенос
строки. И JSON с иконкой шрифта значков:

    {"icon":{"font-family":"Material Symbols Outlined","icon-text":"E8B6"},
     "text":{"font-family":"Inter","text":"Поиск"}}

Читаются оба, и при правке вид сохраняется: у кнопки с иконкой меняется только
текст внутри JSON.
"""

from __future__ import unicode_literals

import json
import os
import re

MASTER = "@bonus2019_07.world"
MVIEWS = ("MVTS_BUTTONS", "MVTS_INTERFACE", "MVTS_LAYERS", "MVTS_CONTENTS",
          "MVTS_CSS_FORMATS")

LANGUAGES = ("RU", "RO", "EN")
TXT_COLUMN = {"RU": "TXT_RU", "RO": "TXT_RO", "EN": "TXT_EN"}


TS_CPP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "TS", "TS.cpp")


def commands_the_till_knows(path=TS_CPP):
    """Имена команд, которые разбирает сама касса.

    Берутся не из справочника базы, а из кода `TS.cpp`: там длинная цепочка
    сравнений `StrCmp(ACmd, "Имя")`, и что в неё не попало — кнопка, которая
    молча ничего не делает. Неизвестное имя касса не считает ошибкой, поэтому
    заметить такую кнопку иначе нельзя.
    """
    try:
        raw = open(path, "rb").read()
    except IOError:
        return set()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1251", "replace")
    names = set(re.findall(r'StrCmp\s*\(\s*\w+\s*,\s*"([^"]+)"', text))
    # эти две разбираются раньше цепочки сравнений
    names.update(("ExecuteNoParamSql", "ExecuteTwoParamsSql"))
    return names


def color_to_css(value):
    """Цвет VCL (`BBGGRR` числом) в вид, понятный браузеру."""
    if value in (None, "", 0, "0"):
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        return "{}".format(value)
    if n < 0:
        return None
    return "#{:02X}{:02X}{:02X}".format(n & 0xFF, (n >> 8) & 0xFF,
                                        (n >> 16) & 0xFF)


def parse_caption(txt):
    """Подпись кнопки в виде (текст, значок, это ли JSON)."""
    if not txt:
        return "", None, False
    s = txt.strip()
    if s.startswith("{"):
        try:
            data = json.loads(s)
        except ValueError:
            return txt, None, False
        text = ""
        icon = None
        block = data.get("text")
        if isinstance(block, dict):
            text = block.get("text", "") or ""
        elif isinstance(block, str):
            text = block
        ib = data.get("icon")
        if isinstance(ib, dict):
            icon = ib.get("icon-text")
        return text, icon, True
    return txt, None, False


def render_caption(old_txt, new_text):
    """Новая подпись в том же виде, в каком была прежняя."""
    if not old_txt or not old_txt.strip().startswith("{"):
        return new_text
    try:
        data = json.loads(old_txt)
    except ValueError:
        return new_text
    block = data.get("text")
    if isinstance(block, dict):
        block["text"] = new_text
    else:
        data["text"] = {"text": new_text}
    return json.dumps(data, ensure_ascii=False)


class Button(object):
    __slots__ = ("interface_id", "layer_id", "ord_id", "order_id",
                 "manual_order_id", "command", "params", "text", "icon",
                 "is_json", "raw_text", "cod_univers", "ascii_code",
                 "content_id", "color", "font_color", "pl_sql")

    def __init__(self, row):
        self.interface_id = row["INTERFACE_ID"]
        self.layer_id = row["LAYER_ID"]
        self.ord_id = int(row["ORD_ID"]) if row.get("ORD_ID") else None
        self.order_id = row.get("ORDER_ID")
        self.manual_order_id = row.get("MANUAL_ORDER_ID")
        cmd = (row.get("INTERNAL_CMD") or "").strip()
        parts = [p.strip() for p in cmd.split(",")] if cmd else []
        self.command = parts[0] if parts else ""
        self.params = [p for p in parts[1:] if p]
        self.raw_text = row.get("TXT") or ""
        self.text, self.icon, self.is_json = parse_caption(self.raw_text)
        self.cod_univers = row.get("COD_UNIVERS")
        self.ascii_code = row.get("ASCII_CODE_STR")
        self.content_id = row.get("CONTENT_ID")
        self.color = color_to_css(row.get("BACKGR_COLOR"))
        self.font_color = color_to_css(row.get("FONT_COLOR"))
        self.pl_sql = row.get("PL_SQL_BLOCK")

    @property
    def internal_cmd(self):
        return ",".join([self.command] + self.params) if self.command else ""

    @property
    def pinned(self):
        """Позиция закреплена вручную, а не вычислена по алфавиту."""
        return self.manual_order_id is not None

    def as_dict(self):
        return {
            "ord": self.ord_id,
            "orderId": self.order_id,
            "manual": self.manual_order_id,
            "pinned": self.pinned,
            "cmd": self.command,
            "params": self.params,
            "internalCmd": self.internal_cmd,
            "text": self.text,
            "icon": self.icon,
            "isJson": self.is_json,
            "cod": self.cod_univers,
            "ascii": self.ascii_code,
            "color": self.color,
            "fontColor": self.font_color,
            "plSql": self.pl_sql,
        }


class Panel(object):
    def __init__(self, row):
        self.id = int(row["ID"])
        self.name = row.get("NAME")
        self.type = row.get("TYPE")
        self.cols = int(row.get("CNT_W") or 0)
        self.rows = int(row.get("CNT_H") or 0)
        self.btn_width = row.get("BTN_WIDTH")
        self.btn_height = row.get("BTN_HEIGHT")
        self.line_width = row.get("LINE_WIDTH")
        self.address_bar = row.get("ADDRESS_BAR")
        self.color = color_to_css(row.get("BACKGR_COLOR"))

    @property
    def capacity(self):
        return self.cols * self.rows

    def as_dict(self):
        return {
            "id": self.id, "name": self.name, "type": self.type,
            "cols": self.cols, "rows": self.rows, "capacity": self.capacity,
            "btnWidth": self.btn_width, "btnHeight": self.btn_height,
            "lineWidth": self.line_width, "addressBar": self.address_bar,
            "color": self.color,
        }


def _rows(cur):
    names = [d[0] for d in cur.description]
    out = []
    for row in cur.fetchall():
        rec = {}
        for n, v in zip(names, row):
            rec[n] = v.read() if hasattr(v, "read") else v
        out.append(rec)
    return out


def apply_edits(buttons, edits):
    """Показать кнопки с учётом ещё не применённых правок.

    Порядок пересчитывается по тому же правилу, по которому его считает база:
    сначала кнопки с закреплённой позицией, затем остальные по алфавиту
    подписи, и лишь потом по `ORDER_ID`. Поэтому предпросмотр совпадает с тем,
    что получится после применения, а не показывает желаемое.
    """
    if not edits:
        return buttons
    for b in buttons:
        e = edits.get(b.order_id)
        if not e:
            continue
        if "manual" in e:
            b.manual_order_id = e["manual"]
        if "text" in e:
            b.text = e["text"]
            b.raw_text = render_caption(b.raw_text, e["text"])
        if "command" in e:
            b.command = e["command"]
            b.params = [p for p in e.get("params", []) if p]

    def key(b):
        manual = b.manual_order_id
        return (
            0 if manual is not None else 1,
            manual if manual is not None else 0,
            (b.text or "").replace("|", " ").upper(),
            b.order_id if b.order_id is not None else 0,
        )

    ordered = sorted(buttons, key=key)
    for i, b in enumerate(ordered, 1):
        b.ord_id = i
    return ordered


class TSLayout(object):
    """Раскладка кнопок: чтение из схемы кассы, правка в мастере."""

    def __init__(self, connection):
        self.con = connection

    # --- чтение -----------------------------------------------------------

    def panels(self):
        cur = self.con.cursor()
        cur.execute("select * from vts_interface order by id")
        return [Panel(r) for r in _rows(cur)]

    def panel(self, interface_id):
        cur = self.con.cursor()
        cur.execute("select * from vts_interface where id = :i", i=interface_id)
        rows = _rows(cur)
        return Panel(rows[0]) if rows else None

    def layers(self, interface_id):
        cur = self.con.cursor()
        cur.execute("""select layer_id, name, level_id, path, parent_id, isleaf
                         from vts_layersh where interface_id = :i
                        order by level_id, path""", i=interface_id)
        out = []
        for r in _rows(cur):
            path = (r.get("PATH") or "").replace("\\", " / ").strip(" /")
            out.append({
                "layer": int(r["LAYER_ID"]),
                "name": r.get("NAME") or path or str(r["LAYER_ID"]),
                "level": r.get("LEVEL_ID"),
                "path": path,
                "leaf": r.get("ISLEAF"),
            })
        return out

    def used_layers(self, interface_id):
        """Слои, на которых действительно есть кнопки."""
        cur = self.con.cursor()
        cur.execute("""select layer_id, count(*) from vts_buttons
                        where interface_id = :i group by layer_id
                        order by layer_id""", i=interface_id)
        return [{"layer": int(a), "buttons": int(b)} for a, b in cur]

    def buttons(self, interface_id, layer_id, language="RU"):
        cur = self.con.cursor()
        cur.execute("""select * from vts_buttons
                        where interface_id = :i and layer_id = :l and lng = :g
                        order by ord_id""",
                    i=interface_id, l=layer_id, g=language)
        return [Button(r) for r in _rows(cur)]

    def buttons_with_picture(self, interface_id, layer_id, language="RU"):
        """Номера строк кнопок, у которых есть своя картинка.

        Одним запросом, а не по кнопке: картинки — это BLOB, и тянуть их ради
        одного «есть или нет» незачем.
        """
        cur = self.con.cursor()
        cur.execute("""select order_id from vts_buttons
                        where interface_id = :i and layer_id = :l and lng = :g
                          and picture is not null""",
                    i=interface_id, l=layer_id, g=language)
        return set(int(r[0]) for r in cur)

    def languages(self, interface_id=None):
        cur = self.con.cursor()
        if interface_id is None:
            cur.execute("select distinct lng from vts_buttons order by lng")
        else:
            cur.execute("""select distinct lng from vts_buttons
                            where interface_id = :i order by lng""",
                        i=interface_id)
        return [r[0] for r in cur if r[0]]

    def commands(self):
        """Справочник команд. Живёт только в мастере."""
        cur = self.con.cursor()
        cur.execute("""select id, cmd, min_params, max_params, format,
                              commentary
                         from bonus2019_07.xts_commands{}
                        order by cmd""".format(MASTER))
        out = []
        for r in _rows(cur):
            out.append({
                "id": int(r["ID"]),
                "cmd": r["CMD"],
                "min": int(r["MIN_PARAMS"] or 0),
                "max": int(r["MAX_PARAMS"] or 0),
                "format": r.get("FORMAT"),
                "note": r.get("COMMENTARY"),
            })
        return out

    def unsupported_commands(self, known_by_till):
        """Команды, которые есть в базе, но касса их не выполняет."""
        cur = self.con.cursor()
        cur.execute("""select internal_cmd, count(*) from vts_buttons
                        where internal_cmd is not null
                        group by internal_cmd""")
        seen = {}
        for cmd, n in cur:
            name = re.split(r"[,\s]", cmd.strip())[0]
            seen[name] = seen.get(name, 0) + int(n)
        lower = set(k.lower() for k in known_by_till)
        return sorted(((k, v) for k, v in seen.items()
                       if k.lower() not in lower), key=lambda x: -x[1])

    # --- правка -----------------------------------------------------------

    def set_position(self, interface_id, layer_id, order_id, manual_order_id):
        """Закрепить кнопку за ячейкой. Пишется MANUAL_ORDER_ID."""
        cur = self.con.cursor()
        cur.execute("""update bonus2019_07.xts_buttons{}
                          set manual_order_id = :m
                        where interface_id = :i and layer_id = :l
                          and order_id = :o""".format(MASTER),
                    m=manual_order_id, i=interface_id, l=layer_id, o=order_id)
        return cur.rowcount

    def set_caption(self, interface_id, layer_id, order_id, language, text):
        """Сменить подпись, сохранив её вид, и снять признак автозаполнения."""
        col = TXT_COLUMN.get(language.upper())
        if col is None:
            raise ValueError("неизвестный язык: {}".format(language))
        cur = self.con.cursor()
        cur.execute("""select {} from bonus2019_07.xts_buttons{}
                        where interface_id = :i and layer_id = :l
                          and order_id = :o""".format(col, MASTER),
                    i=interface_id, l=layer_id, o=order_id)
        row = cur.fetchone()
        old = (row[0] if row else "") or ""
        new = render_caption(old, text)
        cur.execute("""update bonus2019_07.xts_buttons{}
                          set {} = :t, is_auto = null
                        where interface_id = :i and layer_id = :l
                          and order_id = :o""".format(MASTER, col),
                    t=new, i=interface_id, l=layer_id, o=order_id)
        return cur.rowcount, new

    def set_command(self, interface_id, layer_id, order_id, cmd_id,
                    prm1=None, prm2=None):
        """Сменить команду. INTERNAL_CMD соберёт триггер."""
        cur = self.con.cursor()
        cur.execute("""update bonus2019_07.xts_buttons{}
                          set cmd_id = :c, prm1 = :p1, prm2 = :p2
                        where interface_id = :i and layer_id = :l
                          and order_id = :o""".format(MASTER),
                    c=cmd_id, p1=prm1, p2=prm2,
                    i=interface_id, l=layer_id, o=order_id)
        return cur.rowcount

    def refresh(self, views=MVIEWS):
        """Довести изменения из мастера до кассы."""
        cur = self.con.cursor()
        done = []
        for v in views:
            cur.callproc("dbms_mview.refresh", [v, "?"])
            done.append(v)
        return done

    def commit(self):
        self.con.commit()

    def rollback(self):
        self.con.rollback()
