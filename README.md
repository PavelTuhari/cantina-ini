# cantina.ini — файл настроек кассы UAMenu

> **In English, briefly.** Everything about `cantina.ini`, the single
> configuration file of the UAMenu point-of-sale (C++Builder + Oracle):
> a reference of ~450 keys generated from the till's own sources, the
> rules of how the till reads them (file vs. database precedence, CP1251,
> first duplicate wins), where the till looks for the file, the secrets
> store that keeps passwords out of it, a configuration tool, and 65 real
> example files from different shops with all secrets and addresses
> scrubbed.

Касса UAMenu не имеет установщика и базы настроек: всё её поведение —
от адреса базы и номера кассы до драйвера фискального принтера и ключей
платёжных служб — задаётся одним файлом `cantina.ini` рядом с `UAMenu.exe`.
Этот репозиторий собирает всё, что про него известно.

## С чего начать

| Вопрос | Где ответ |
|---|---|
| Что значит ключ, откуда касса берёт значение, что по умолчанию | [docs/cantina-ini.md](docs/cantina-ini.md) — справочник по ~450 ключам, собран из исходников кассы утилитой `cfgtool` |
| Куда положить кассу, как она ищет файл, почему файл нельзя брать чужой | [docs/install.md](docs/install.md) |
| Как держать пароли и ключи вне файла | [docs/secrets.md](docs/secrets.md) — пометки `@secret:`, реестр Windows под DPAPI, `tools/secrets.py` |
| Как настроить кассу на стенд и прогнать сценарий без рук | [docs/bench-config.md](docs/bench-config.md), [docs/selftest.md](docs/selftest.md), шаблоны в [templates/](templates/) |
| Как выглядят настоящие файлы разных точек | [examples/](examples/README.md) — 65 файлов с таблицей «что где» |
| Править файл не блокнотом | [cfgtool/](cfgtool/README.md) — окно настроек, проверки, редактор кнопок, генератор справочника |
| Где хранить файл и как вести историю его версий в бэк-офисе | [docs/history-backoffice.md](docs/history-backoffice.md) — три места и их роли, таблицы `CANTINA_INI_VER*` и пакет через DB link, [sql/cantina_ini_hist.sql](sql/cantina_ini_hist.sql) |
| На Windows Server вместо русских букв `Êîä` и `????????` | [docs/encoding.md](docs/encoding.md) — системная локаль, `NLS_LANG`, проверка; правило кодировки исходников |
| Старая вики по установке кассы | [docs/wiki-install-cassa.html](docs/wiki-install-cassa.html) |

## Пять фактов, без которых файл правят неправильно

1. **Побеждает первая строка сверху**, не последняя. Дописать ключ в конец —
   значит ничего не изменить, если он уже есть выше.
2. **У каждого ключа своё старшинство относительно базы.** Часть читается
   «файл, затем база», часть «база, затем файл», часть только из таблицы
   `TMS_INIT_PARAMS`. Старшинство указано в справочнике у каждого ключа.
3. **Кодировка CP1251.** Редактор, сохранивший файл в UTF-8, портит все
   русские значения. Исключение — файлы, у которых уже стоит BOM.
4. **Пустое значение равно отсутствию строки**: `Key=` не выключает
   параметр, а отдаёт его базе и значению по умолчанию из кода.
5. **Касса ищет файл в трёх местах по порядку**: переменная `UAMENU_INI`,
   каталог `UAMenu.exe`, `C:\Windows`. Забытый файл в Windows — касса
   входит не в ту базу.

## Про примеры

Файлы в `examples/` — настоящие настройки касс владельца за несколько
лет: разные магазины, фискальные принтеры (Datecs, Elicom, RTI, IKC,
виртуальный), платёжные интеграции (MIA, BPAY, POS API лояльности,
банковские терминалы), режимы столовой и самообслуживания. Перед
публикацией каждый прошёл [tools/scrub_examples.py](tools/scrub_examples.py):

* пароли, ключи, токены → `@secret:<файл>/<секция>/<ключ>` — в таком виде
  касса и читает их из реестра (см. `docs/secrets.md`);
* закомментированные секреты → `@removed`;
* IP-адреса → `<ip>`, почта → `<email>`;
* всё остальное байт в байт: кодировка, дубли строк, комментарии.

Сравнить два файла, не вчитываясь: `python -m frontarchive settings diff
a.ini b.ini --ini` (FrontArchive — в приватном репозитории владельца) или
вкладка проверки `cfgtool`.

## Инструменты

```bash
pip install flask
python -m cfgtool web                        # окно настроек на 127.0.0.1:8920
python -m cfgtool scan && python -m cfgtool docgen   # пересобрать справочник из исходников (нужны исходники кассы)
python tools/secrets.py migrate cantina.ini  # показать, что перенести в реестр; --yes перенести
python tools/secrets.py check cantina.ini    # все пометки читаются, открытых паролей нет
```

`tools/secrets.py` — копия модуля `pypos.secrets` из кассы; работает
только на Windows (DPAPI, реестр).

## Связанные репозитории

* [uamenu-ai-testbench](https://github.com/PavelTuhari/uamenu-ai-testbench) —
  развернуть кассу на пустой машине с локальной Oracle Free и снять акт;
  там же [программа полного тестирования](https://github.com/PavelTuhari/uamenu-ai-testbench/blob/main/docs/testing-program/)
  всех режимов кассы (страница `docs/testing-program.html` с флажками и выгрузкой акта).
* `uamenu_experimental_ai` (приватный) — исходники кассы, `pypos`, полный `docs/`.
