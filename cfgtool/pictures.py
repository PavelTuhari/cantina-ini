# -*- coding: utf-8 -*-
"""Картинки на кнопках: загрузка, замена, удаление.

Касса умеет показывать картинку у любой кнопки — поле `PICTURE` приходит к ней
в `VTS_BUTTONS`. Но положить туда картинку раньше было нечем, поэтому ни у
одной кнопки её и не было.

## Где картинка живёт

Кнопка ссылается на запись содержимого (`CONTENT_ID`), и картинка лежит
именно там — в `XTS_CONTENTS.PICTURE`. Отсюда следует важное: **запись
содержимого бывает общей у нескольких кнопок**. В рабочей базе 47 таких
записей, одну из них делят 16 кнопок. Поставив картинку, легко изменить вид
сразу шестнадцати кнопок, поэтому здесь это всегда проверяется и говорится
вслух.

## Две особенности записи

**Писать надо в мастер.** В схеме кассы лежат материализованные представления,
они только для чтения. Настоящая таблица — в `BONUS2019_07`, доступ через
связь баз.

**Прочитать записанное через связь баз нельзя.** Oracle отвечает `ORA-22992`
на любую попытку взять указатель LOB из удалённой таблицы. Записать при этом
можно — прямой привязкой значения. Поэтому проверка «что получилось»
выполняется после обновления представлений, уже со стороны кассы.

## Размер имеет значение

Фотографии товаров в этой базе весят в среднем 500 КБ, самая большая — 22,9 МБ
на одну картинку, а всего их 69,5 МБ. Касса тянет их одним запросом целиком.
Для кнопки размером в пару сантиметров это бессмысленно, поэтому при загрузке
картинка ужимается: сторона не больше `MAX_SIDE`, вес — не больше
`MAX_BYTES`. Исходник не хранится: на кнопке он всё равно не виден.
"""

from __future__ import unicode_literals

import io
import os

MASTER = "@bonus2019_07.world"

MAX_SIDE = 256        # точек по большей стороне
MAX_BYTES = 120 * 1024
JPEG_QUALITY = 86

SIGNATURES = (
    (b"\xff\xd8", "JPEG"),
    (b"\x89PNG", "PNG"),
    (b"BM", "BMP"),
    (b"GIF8", "GIF"),
)


def kind_of(data):
    """Что это за картинка. Определяется по содержимому, а не по имени файла."""
    if not data:
        return None
    for sig, name in SIGNATURES:
        if data[:len(sig)] == sig:
            return name
    return None


def prepare(data, max_side=MAX_SIDE, max_bytes=MAX_BYTES):
    """Ужать картинку до размера, разумного для кнопки.

    Возвращает (байты, описание). Без Pillow картинка проходит как есть, но
    слишком большая отклоняется: класть в базу двадцатимегабайтный снимок,
    который будет показан размером с ноготь, незачем.
    """
    if kind_of(data) is None:
        raise ValueError("это не картинка: не опознан ни JPEG, ни PNG, "
                         "ни BMP, ни GIF")
    try:
        from PIL import Image
    except ImportError:
        if len(data) > max_bytes:
            raise ValueError(
                "картинка {} КБ, а без библиотеки Pillow ужать её нечем. "
                "Поставьте Pillow либо уменьшите картинку сами до {} КБ".format(
                    len(data) // 1024, max_bytes // 1024))
        return data, "без изменений, {} КБ".format(len(data) // 1024)

    src = Image.open(io.BytesIO(data))
    was = "{}x{}, {} КБ".format(src.width, src.height, max(1, len(data) // 1024))
    transparent = src.mode in ("RGBA", "LA", "P")

    if max(src.width, src.height) > max_side:
        k = float(max_side) / max(src.width, src.height)
        src = src.resize((max(1, int(src.width * k)), max(1, int(src.height * k))),
                         Image.LANCZOS)

    out = io.BytesIO()
    if transparent:
        # Прозрачность нужна значкам: на цветной кнопке белый угол заметен.
        src.convert("RGBA").save(out, format="PNG", optimize=True)
    else:
        src.convert("RGB").save(out, format="JPEG", quality=JPEG_QUALITY,
                                optimize=True)
    result = out.getvalue()

    if len(result) > max_bytes and not transparent:
        for q in (75, 65, 55):
            out = io.BytesIO()
            src.convert("RGB").save(out, format="JPEG", quality=q, optimize=True)
            result = out.getvalue()
            if len(result) <= max_bytes:
                break

    became = "{}x{}, {} КБ, {}".format(
        src.width, src.height, max(1, len(result) // 1024),
        "PNG с прозрачностью" if transparent else "JPEG")
    return result, "было {} — стало {}".format(was, became)


class Pictures(object):
    """Картинки кнопок: чтение со стороны кассы, запись в мастер."""

    def __init__(self, connection):
        self.con = connection

    # --- чтение -----------------------------------------------------------

    def button_picture(self, interface_id, layer_id, order_id, language="RU"):
        """Картинка кнопки так, как её видит касса."""
        cur = self.con.cursor()
        cur.execute("""select picture from vts_buttons
                        where interface_id = :i and layer_id = :l
                          and order_id = :o and lng = :g""",
                    i=interface_id, l=layer_id, o=order_id, g=language)
        row = cur.fetchone()
        if not row or row[0] is None:
            return None
        blob = row[0]
        return blob.read() if hasattr(blob, "read") else blob

    def content_of(self, interface_id, layer_id, order_id):
        """Запись содержимого кнопки и сколько кнопок её делят."""
        cur = self.con.cursor()
        cur.execute("""select content_id from bonus2019_07.xts_buttons{}
                        where interface_id = :i and layer_id = :l
                          and order_id = :o""".format(MASTER),
                    i=interface_id, l=layer_id, o=order_id)
        row = cur.fetchone()
        if not row or row[0] is None:
            return None, 0
        content_id = int(row[0])
        cur.execute("""select count(*) from bonus2019_07.xts_buttons{}
                        where content_id = :c""".format(MASTER), c=content_id)
        return content_id, int(cur.fetchone()[0])

    def shared_with(self, content_id):
        """Какие ещё кнопки покажут эту же картинку."""
        cur = self.con.cursor()
        cur.execute("""select interface_id, layer_id, order_id
                         from bonus2019_07.xts_buttons{}
                        where content_id = :c
                        order by interface_id, layer_id, order_id""".format(MASTER),
                    c=content_id)
        return [{"interface": int(a), "layer": int(b), "order": int(c)}
                for a, b, c in cur]

    def product_photo(self, cod):
        cur = self.con.cursor()
        cur.execute("select photo from vms_univ_photo where cod = :c", c=cod)
        row = cur.fetchone()
        if not row or row[0] is None:
            return None
        blob = row[0]
        return blob.read() if hasattr(blob, "read") else blob

    # --- запись -----------------------------------------------------------

    def set_content_picture(self, content_id, data):
        """Положить картинку в запись содержимого.

        Значение привязывается напрямую: читать LOB из удалённой таблицы
        нельзя, а записать — можно.
        """
        cur = self.con.cursor()
        cur.execute("""update bonus2019_07.xts_contents{}
                          set picture = :p where id = :i""".format(MASTER),
                    p=data, i=content_id)
        return cur.rowcount

    def clear_content_picture(self, content_id):
        cur = self.con.cursor()
        cur.execute("""update bonus2019_07.xts_contents{}
                          set picture = null where id = :i""".format(MASTER),
                    i=content_id)
        return cur.rowcount

    def set_product_photo(self, cod, data):
        """Заменить фотографию товара. Ею пользуются все кнопки этого товара."""
        cur = self.con.cursor()
        cur.execute("""update bonus2019_07.tms_univ_photo{}
                          set photo = :p where cod = :c""".format(MASTER),
                    p=data, c=cod)
        if cur.rowcount:
            return cur.rowcount
        cur.execute("""select nvl(max(id), 0) + 1
                         from bonus2019_07.tms_univ_photo{}""".format(MASTER))
        new_id = cur.fetchone()[0]
        cur.execute("""insert into bonus2019_07.tms_univ_photo{}
                         (id, cod, photo) values (:i, :c, :p)""".format(MASTER),
                    i=new_id, c=cod, p=data)
        return cur.rowcount

    # --- обзор ------------------------------------------------------------

    def overview(self):
        """Сколько картинок есть и сколько они весят."""
        cur = self.con.cursor()
        out = {}
        cur.execute("""select count(*),
                              count(case when picture is not null then 1 end)
                         from vts_buttons where lng = 'RU'""")
        total, withpic = cur.fetchone()
        out["кнопок"] = int(total)
        out["кнопок с картинкой"] = int(withpic or 0)
        cur.execute("""select count(*),
                              round(sum(dbms_lob.getlength(photo)) / 1048576, 1),
                              round(max(dbms_lob.getlength(photo)) / 1048576, 1)
                         from vms_univ_photo where photo is not null""")
        n, total_mb, max_mb = cur.fetchone()
        out["фотографий товаров"] = int(n or 0)
        out["их вес, МБ"] = float(total_mb or 0)
        out["самая большая, МБ"] = float(max_mb or 0)
        return out

    def oversized(self, limit_bytes=MAX_BYTES):
        """Фотографии, которые стоит ужать: касса тянет их целиком."""
        cur = self.con.cursor()
        cur.execute("""select cod, denumirea, dbms_lob.getlength(photo) sz
                         from vms_univ_photo
                        where dbms_lob.getlength(photo) > :n
                        order by sz desc""", n=limit_bytes)
        return [{"cod": int(a), "name": b, "bytes": int(c)} for a, b, c in cur]
