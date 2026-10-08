# -*- coding: utf-8 -*-
"""Окно настройки кассы.

    python -m cfgtool web                на 127.0.0.1:8920

Три вкладки. **Настройки** — сам файл: каждый параметр рядом с тем, что о нём
известно из кода, и правится тут же. **Проверка** — то, что в файле не так:
строки, которые касса не читает, и параметры, которых в кассе нет. **Кнопки
тачскрина** — визуальная раскладка: сетка панели как её видит кассир, кнопки
перетаскиваются мышью, подпись и команда правятся на месте.

Разделение, важное для безопасности: правка файла ничего не знает про Oracle и
работает всегда; вкладка кнопок подключается к базе только когда её открыли, и
без базы просто говорит об этом, а не роняет всё окно.

Правки файла записываются сразу, рядом остаётся копия `.bak`. Правки кнопок
живут в незавершённой транзакции, пока не нажата «Применить»: до этого их
видит только тот, кто правит, а «Отменить» возвращает всё как было.
"""

from __future__ import unicode_literals

import base64
import os
import sys

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, Response

HERE = os.path.dirname(os.path.abspath(__file__))
UAMENU = os.path.dirname(HERE)
if UAMENU not in sys.path:
    sys.path.insert(0, UAMENU)

from cfgtool.catalog import Catalog                              # noqa: E402
from cfgtool import descriptions                                 # noqa: E402
from cfgtool.inifile import printable                            # noqa: E402
from cfgtool.pictures import Pictures, kind_of, prepare           # noqa: E402
from cfgtool.tsbuttons import (                                   # noqa: E402
    TSLayout, apply_edits, commands_the_till_knows)

app = FastAPI(title="Настройка кассы UAMenu", docs_url="/docs")

_ini_path = None
_catalog = None
_layout = None
_connection = None
_pending = []          # что изменено в кнопках и ещё не применено, словами
_edits = {}            # то же для показа: (панель, слой) -> {строка: правки}
# Загруженные картинки, ещё не применённые. Прочитать их обратно из мастера
# нельзя: Oracle не отдаёт LOB через связь баз. Поэтому до применения
# показываем то, что было загружено, прямо отсюда.
_pictures = {}         # (панель, слой, строка) -> байты либо None, если снята


def catalog(reload=False):
    global _catalog
    if _catalog is None or reload:
        _catalog = Catalog(_ini_path)
    return _catalog


def layout():
    """Подключение к Oracle появляется только когда оно понадобилось."""
    global _layout, _connection
    if _layout is not None:
        return _layout
    try:
        import oracledb
        from pypos.db import init_client
        from pypos.credentials import get_password
        init_client()
        _connection = oracledb.connect(
            user=os.environ.get("PYPOS_USER", "bonuspos_self24"),
            password=get_password(
                os.environ.get("PYPOS_USER", "bonuspos_self24"),
                os.environ.get("PYPOS_DB_ALIAS", "clouddev")),
            dsn=os.environ.get("PYPOS_DSN",
                               "localhost:1522/FREEPDB1"))
        _layout = TSLayout(_connection)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Нет связи с базой, поэтому кнопки недоступны: "
                   "{}".format(exc))
    return _layout


def edits_for(interface_id, layer_id):
    """Несохранённые правки этого слоя, по номеру строки кнопки."""
    return _edits.get((int(interface_id), int(layer_id)), {})


def remember(interface_id, layer_id, order_id, **changes):
    """Запомнить правку, чтобы показывать её до применения."""
    key = (int(interface_id), int(layer_id))
    slot = _edits.setdefault(key, {}).setdefault(int(order_id), {})
    slot.update(changes)


# --- страница ---------------------------------------------------------------

@app.get("/")
def index():
    return FileResponse(os.path.join(HERE, "ui", "index.html"))


@app.get("/ui/{name}")
def ui_file(name):
    path = os.path.join(HERE, "ui", os.path.basename(name))
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="нет такого файла")
    return FileResponse(path)


# --- настройки --------------------------------------------------------------

def option_json(o):
    return {
        "name": o.name,
        "value": None if o.secret else printable(o.value),
        "secret": o.secret,
        "state": o.state,
        "kind": o.kind,
        "source": o.source,
        "default": o.code_default,
        "note": o.note,
        "choices": o.choices,
        "group": o.group,
        "line": o.line,
        "shadowedBy": o.shadowed_by,
        "places": [{"file": p["file"], "line": p["line"]}
                   for p in o.places[:4]],
        "lines": [{"index": e.index, "value": printable(e.clean),
                   "disabled": e.disabled, "shadowed": e.shadowed}
                  for e in o.entries],
    }


@app.get("/api/summary")
def api_summary():
    c = catalog()
    s = c.summary()
    return {
        "summary": s,
        "groups": [{"title": t, "about": a, "count": len(opts)}
                   for t, a, opts in c.groups()],
    }


@app.get("/api/options")
def api_options(group=Query(None), q=Query(None), state=Query(None),
                absent=Query(False)):
    c = catalog()
    pool = c.options if absent else c.in_file()
    out = []
    needle = (q or "").strip().lower()
    for o in pool:
        if group and o.group != group:
            continue
        if state and o.state != state:
            continue
        if needle:
            hay = "{} {} {}".format(o.name, o.note or "",
                                    "" if o.secret else (o.value or ""))
            if needle not in hay.lower():
                continue
        out.append(option_json(o))
    out.sort(key=lambda x: x["name"].lower())
    return {"options": out, "count": len(out)}


@app.post("/api/option")
def api_set_option(payload=Body(...)):
    name = (payload or {}).get("name")
    value = (payload or {}).get("value")
    if not name:
        raise HTTPException(status_code=400, detail="не указано имя параметра")
    c = catalog()
    opt = c.get(name)
    if opt is None:
        raise HTTPException(status_code=404, detail="нет такого параметра")
    if opt.secret:
        raise HTTPException(
            status_code=400,
            detail="это секрет, его не правят через окно настройки")
    try:
        c.ini.set(opt.name, value)
        written = c.ini.save()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="{}".format(exc))
    c = catalog(reload=True)
    return {"ok": True, "bytes": written, "option": option_json(c.get(name))}


@app.post("/api/option/line")
def api_toggle_line(payload=Body(...)):
    """Включить или отключить отдельную строку файла решёткой."""
    index = (payload or {}).get("index")
    enabled = bool((payload or {}).get("enabled"))
    if not index:
        raise HTTPException(status_code=400, detail="не указана строка")
    c = catalog()
    if enabled:
        c.ini.enable(int(index))
    else:
        c.ini.disable(int(index))
    written = c.ini.save()
    catalog(reload=True)
    return {"ok": True, "bytes": written}


@app.get("/api/checks")
def api_checks():
    c = catalog()
    dup = []
    for name, entries in sorted(c.ini.duplicates().items()):
        dup.append({
            "name": name,
            "lines": [{"index": e.index, "value": printable(e.clean),
                       "effective": e.effective} for e in entries],
        })
    return {
        "encoding": c.ini.encoding,
        "lossy": c.ini.lossy,
        "duplicates": dup,
        "shadowed": [option_json(o) for o in c.shadowed()],
        "dead": [{"name": o.name,
                  "line": o.entries[0].index if o.entries else None,
                  "value": None if o.secret else printable(
                      o.entries[0].clean if o.entries else None)}
                 for o in sorted(c.dead(), key=lambda x: x.name.lower())],
        "secrets": sorted(descriptions.SECRETS),
    }


# --- кнопки тачскрина -------------------------------------------------------

@app.get("/api/ts/panels")
def api_ts_panels():
    ts = layout()
    panels = []
    for p in ts.panels():
        d = p.as_dict()
        d["layers"] = ts.used_layers(p.id)
        panels.append(d)
    known = commands_the_till_knows()
    return {
        "panels": panels,
        "languages": ts.languages(),
        "unsupported": [{"cmd": c, "buttons": n}
                        for c, n in ts.unsupported_commands(known)],
        "knownCount": len(known),
        "pending": len(_pending),
    }


@app.get("/api/ts/panel")
def api_ts_panel(id=Query(...), layer=Query(1), lng=Query("RU")):
    ts = layout()
    panel = ts.panel(int(id))
    if panel is None:
        raise HTTPException(status_code=404, detail="нет такой панели")
    edits = edits_for(id, layer)
    buttons = apply_edits(ts.buttons(int(id), int(layer), lng), edits)
    known = set(k.lower() for k in commands_the_till_knows())
    with_pic = ts.buttons_with_picture(int(id), int(layer), lng)
    out = []
    for b in buttons:
        d = b.as_dict()
        d["supported"] = (not b.command) or b.command.lower() in known
        key = (int(id), int(layer), b.order_id)
        d["hasPicture"] = ((_pictures[key] is not None) if key in _pictures
                           else (b.order_id in with_pic))
        out.append(d)
    return {
        "panel": panel.as_dict(),
        "layers": ts.layers(int(id)),
        "used": ts.used_layers(int(id)),
        "buttons": out,
        "language": lng,
        "languages": ts.languages(int(id)),
        "pending": len(_pending),
        "preview": bool(edits),
    }


@app.get("/api/ts/commands")
def api_ts_commands():
    ts = layout()
    known = set(k.lower() for k in commands_the_till_knows())
    cmds = ts.commands()
    for c in cmds:
        c["supported"] = c["cmd"].strip().lower() in known
    return {"commands": cmds}


@app.post("/api/ts/move")
def api_ts_move(payload=Body(...)):
    """Поставить кнопку в ячейку. Пишется MANUAL_ORDER_ID."""
    p = payload or {}
    ts = layout()
    n = ts.set_position(int(p["interface"]), int(p["layer"]),
                        int(p["orderId"]), int(p["cell"]))
    remember(p["interface"], p["layer"], p["orderId"], manual=int(p["cell"]))
    _pending.append("кнопка {} панели {} слоя {} встала в ячейку {}".format(
        p["orderId"], p["interface"], p["layer"], p["cell"]))
    return {"ok": True, "rows": n, "pending": len(_pending)}


@app.post("/api/ts/caption")
def api_ts_caption(payload=Body(...)):
    p = payload or {}
    ts = layout()
    n, new = ts.set_caption(int(p["interface"]), int(p["layer"]),
                            int(p["orderId"]), p.get("lng", "RU"),
                            p.get("text", ""))
    remember(p["interface"], p["layer"], p["orderId"],
             text=p.get("text", ""))
    _pending.append("подпись кнопки {} панели {}: {!r}".format(
        p["orderId"], p["interface"], p.get("text", "")))
    return {"ok": True, "rows": n, "stored": new, "pending": len(_pending)}


@app.post("/api/ts/command")
def api_ts_command(payload=Body(...)):
    p = payload or {}
    ts = layout()
    n = ts.set_command(int(p["interface"]), int(p["layer"]),
                       int(p["orderId"]), int(p["cmdId"]),
                       p.get("prm1") or None, p.get("prm2") or None)
    name = next((c["cmd"] for c in ts.commands()
                 if c["id"] == int(p["cmdId"])), "")
    remember(p["interface"], p["layer"], p["orderId"], command=name,
             params=[p.get("prm1") or "", p.get("prm2") or ""])
    _pending.append("команда кнопки {} панели {}".format(
        p["orderId"], p["interface"]))
    return {"ok": True, "rows": n, "pending": len(_pending)}


@app.post("/api/ts/apply")
def api_ts_apply():
    """Записать правки и довести их до кассы."""
    ts = layout()
    if not _pending:
        return {"ok": True, "applied": 0, "refreshed": []}
    ts.commit()
    refreshed = ts.refresh()
    done = len(_pending)
    del _pending[:]
    _edits.clear()
    _pictures.clear()
    return {"ok": True, "applied": done, "refreshed": refreshed}


@app.post("/api/ts/discard")
def api_ts_discard():
    ts = layout()
    ts.rollback()
    done = len(_pending)
    del _pending[:]
    _edits.clear()
    _pictures.clear()
    return {"ok": True, "discarded": done}


@app.get("/api/ts/pending")
def api_ts_pending():
    return {"pending": list(_pending)}


# --- картинки на кнопках ----------------------------------------------------

def pictures():
    layout()          # соединение и понятная ошибка, если базы нет
    return Pictures(_connection)


def picture_bytes(interface, layer, order, lng):
    """Картинка кнопки с учётом ещё не применённой загрузки."""
    key = (int(interface), int(layer), int(order))
    if key in _pictures:
        return _pictures[key]
    return pictures().button_picture(int(interface), int(layer), int(order), lng)


@app.get("/api/ts/picture")
def api_ts_picture(interface=Query(...), layer=Query(...), order=Query(...),
                   lng=Query("RU")):
    """Картинка кнопки так, как её увидит касса после применения."""
    data = picture_bytes(interface, layer, order, lng)
    if data is None:
        raise HTTPException(status_code=404, detail="у кнопки нет картинки")
    kind = kind_of(data) or "JPEG"
    media = {"JPEG": "image/jpeg", "PNG": "image/png",
             "BMP": "image/bmp", "GIF": "image/gif"}[kind]
    return Response(content=data, media_type=media,
                    headers={"Cache-Control": "no-store"})


@app.get("/api/ts/picture/info")
def api_ts_picture_info(interface=Query(...), layer=Query(...),
                        order=Query(...), lng=Query("RU")):
    """Есть ли картинка и сколько кнопок её делят."""
    p = pictures()
    content_id, shared = p.content_of(int(interface), int(layer), int(order))
    data = picture_bytes(interface, layer, order, lng)
    return {
        "contentId": content_id,
        "sharedWith": shared,
        "others": p.shared_with(content_id) if content_id and shared > 1 else [],
        "hasPicture": data is not None,
        "bytes": len(data) if data else 0,
        "kind": kind_of(data) if data else None,
    }


@app.post("/api/ts/picture")
def api_ts_picture_set(payload=Body(...)):
    """Положить картинку кнопке. Присылается в base64."""
    p = payload or {}
    try:
        data = base64.b64decode(p.get("data", ""), validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="файл не разобран")
    pics = pictures()
    content_id, shared = pics.content_of(
        int(p["interface"]), int(p["layer"]), int(p["orderId"]))
    if content_id is None:
        raise HTTPException(
            status_code=400,
            detail="у этой кнопки нет записи содержимого, положить картинку "
                   "некуда")
    try:
        prepared, note = prepare(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="{}".format(exc))
    n = pics.set_content_picture(content_id, prepared)
    _pictures[(int(p["interface"]), int(p["layer"]), int(p["orderId"]))] = prepared
    _pending.append("картинка кнопки {} панели {} ({})".format(
        p["orderId"], p["interface"], note))
    return {"ok": True, "rows": n, "note": note, "sharedWith": shared,
            "bytes": len(prepared), "pending": len(_pending)}


@app.post("/api/ts/picture/clear")
def api_ts_picture_clear(payload=Body(...)):
    p = payload or {}
    pics = pictures()
    content_id, shared = pics.content_of(
        int(p["interface"]), int(p["layer"]), int(p["orderId"]))
    if content_id is None:
        raise HTTPException(status_code=400, detail="у кнопки нет содержимого")
    n = pics.clear_content_picture(content_id)
    _pictures[(int(p["interface"]), int(p["layer"]), int(p["orderId"]))] = None
    _pending.append("снята картинка кнопки {} панели {}".format(
        p["orderId"], p["interface"]))
    return {"ok": True, "rows": n, "sharedWith": shared,
            "pending": len(_pending)}


@app.get("/api/pictures/overview")
def api_pictures_overview():
    pics = pictures()
    return {"overview": pics.overview(),
            "oversized": pics.oversized()[:40]}


def serve(ini_path=None, host="127.0.0.1", port=8920):
    global _ini_path
    _ini_path = ini_path
    import uvicorn
    sys.stdout.write("настройка кассы: http://{}:{}\n".format(host, port))
    sys.stdout.write("файл: {}\n".format(catalog().ini_path))
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    serve()
