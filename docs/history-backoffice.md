# История `cantina.ini` в бэк-офисе

## Где хранить файл настроек кассы: рекомендация

У файла три места, и у каждого своя роль. Ни одно не заменяет другие.

| Место | Что это | Зачем | Команда |
|---|---|---|---|
| **Рядом с `UAMenu.exe`** | рабочий файл | единственное, что читает касса | — |
| **В схеме фронта**, пакет `CANTINA_INI` | точная копия текущего файла внутри базы кассы | переезжает с архивом и клоном; `get_value('PosID')` из SQL; восстановить файл байт в байт на новой машине | `ini save`, `ini pull` |
| **В бэк-офисе**, таблицы `CANTINA_INI_VER*` | все версии файлов всех касс | кто, когда и что менял; сравнить две кассы или две даты; увидеть все кассы одним запросом | `ini push-history`, `ini history`, `ini hist-diff` |
| В репозитории, `schemas/<схема>/` | копия текущего файла в git | ревью правок, откат через git | `ini save` |

Правило: **источник правды — файл рядом с exe**, схема хранит его слепок,
бэк-офис хранит историю слепков. Правка делается в файле, затем
`ini save`, которая кладёт слепок в схему и, если у цели задан
`hist_link`, сразу пишет версию в бэк-офис. Обратный путь (из истории в
файл) — только осознанно, через `ini hist-pull` или `ini pull`.

Почему история именно в бэк-офисе, а не в схеме фронта:

* у фронта уже есть DB link в бэк-офис — ничего нового настраивать не надо;
* бэк-офис один, касс много: история всех касс видна одним запросом;
* фронт-схема может быть пересоздана из архива, и своя история в ней
  пропала бы; бэк-офис переживает любые пересоздания касс;
* в бэк-офисе уже есть резервное копирование и админ.

## Как устроено

Через DB link не передаётся LOB (`ORA-22992`), поэтому версия хранится
**построчно**: строка файла — строка таблицы, до 4000 байт. Версия =
заголовок в `CANTINA_INI_VER` + строки в `CANTINA_INI_VER_LINES`.

Объекты в схеме бэк-офиса (ставит `ini hist-install`, файл
`sql/cantina_ini_hist.sql`):

| Объект | Что |
|---|---|
| `CANTINA_INI_VER` | версия: схема фронта, PosID, имя файла, когда, откуда (хост:путь), SHA-256 байтов файла, число строк и байт, статус `OPEN`/`DONE` |
| `CANTINA_INI_VER_LINES` | строки версии |
| пакет `CANTINA_INI_HIST` | `begin_version` / `add_line` / `end_version` — их зовёт фронт через линк; `last_id`, `get_file` (CLOB), `get_value(id, key)`, `diff_text(a, b)`, `purge(schema, keep)` — для бэк-офиса |
| `V_CANTINA_INI_CURRENT` | последняя версия каждого файла каждой кассы, с `Server` и `FiscalPrinter` прямо в колонках |
| `V_CANTINA_INI_CHANGES` | лента версий с id предыдущей и разницей в числе строк |

На стороне фронта в пакет `CANTINA_INI` добавлена процедура
`push_history(p_link, p_pos_id)`: берёт файлы из самого пакета, считает
строки, вызывает `begin_version@линк`; если SHA-256 совпал с последней
версией — та отвечает `0`, и ничего не пишется. Иначе строки уходят
`add_line@линк`, и `end_version@линк` сверяет их число с заявленным. Имя
линка проверяется по символам, потому что подставляется в динамический
SQL. Незакрытые версии (оборванный push) удаляются при следующем push той
же схемы.

Транзакция одна и распределённая: `ini save` делает commit после push, и
либо версия записана целиком, либо нет.

## Как пользоваться

Один раз, в бэк-офисе. Два способа:

```bash
python -m frontarchive ini hist-install self24 --via-link BONUS2019_07.WORLD   # через линк фронта, пароль бэка не нужен
python -m frontarchive ini hist-install back                                   # напрямую, цель с role = back
```

Первый выполняет каждый DDL как `dbms_utility.exec_ddl_statement@линк`
под учётной записью линка (обычно это владелец схемы бэк-офиса); нужны
её права `create table, sequence, procedure, view` — у `BONUS2019_07`
они есть через роль `RESOURCE`. Так и поставлено в настоящем бэк-офисе
10.10.2026: 10 объектов, все `VALID`, Oracle 11.2.0.4.

У каждого фронта в `targets.ini`:

```ini
[self24]
...
hist_link = BONUS2019_07.WORLD        ; DB link из этой схемы в бэк-офис
```

Дальше история пишется сама при каждом `ini save`. Отдельно:

```bash
python -m frontarchive ini push-history self24          # дослать текущую версию из схемы
python -m frontarchive ini history self24 [--file cantina.ini] [--limit 20]
python -m frontarchive ini hist-diff self24 12 15       # unified diff двух версий
python -m frontarchive ini hist-pull self24 12 --out C:\restore
python -m frontarchive ini save self24 --no-history     # без записи в бэк-офис
```

В бэк-офисе напрямую:

```sql
select * from v_cantina_ini_current;                              -- что стоит на кассах
select * from v_cantina_ini_changes where schema_name = 'BONUSPOS_SELF24' order by hist_id desc;
select cantina_ini_hist.get_value(15, 'FiscalPrinter') from dual;
select cantina_ini_hist.diff_text(12, 15) from dual;              -- "- строка" / "+ строка"
begin cantina_ini_hist.purge('BONUSPOS_SELF24', 50); end;         -- оставить 50 последних
```

Права: фронту нужен `execute` на `CANTINA_INI_HIST` в схеме бэк-офиса под
той учётной записью, к которой подключён линк (обычно это сам владелец
схемы бэк-офиса — тогда ничего давать не надо).

## Что проверено

Стенд на местной Oracle Free, 10.10.2026: схема `FA_BACK` как бэк-офис,
линк `BONUS2019_07.WORLD` из клона `FA_SELF24`.

| Шаг | Результат |
|---|---|
| `ini hist-install free-back` | 8 объектов, пакет `VALID` |
| `ini save free-self24` | версии 1 (`cantina.ini`, 765 строк) и 2 (`selftest.ini`, 98 строк) |
| повторный `ini save` | «без изменений, версия 1 / 2», новых строк нет |
| изменённый файл (`VirtualFPCloseAfterSec` 30→45, добавлена строка) | версия 3, 767 строк |
| `ini hist-diff free-self24 1 3` | ровно две правки |
| `ini hist-pull free-self24 1` + `fc /b` с оригиналом | **no differences** |

Настоящий бэк-офис `BONUS2019_07@clouddev` (Oracle 11.2.0.4), 10.10.2026:
установка через линк из `bonuspos_self24`, `ini save self24` → версии 1
(`cantina.ini`, 765 строк) и 2 (`selftest.ini`, 98), повтор — «без
изменений»; `v_cantina_ini_current` показывает `PosID 101`, `Server
clouddev`, `FiscalPrinter VirtualFP`; `get_value(last_id(...), 'PosID')`
через линк = `101`.

Строки длиннее 4000 байт обрезаются (в `cantina.ini` таких нет —
максимум около 600).
