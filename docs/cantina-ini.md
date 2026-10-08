# Файл настроек кассы `cantina.ini`

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
| Кодировка | CP1251 |
| Строк | 764, из них с параметрами 453 |
| Различных имён | 356 |

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

**Точка с запятой внутри значения хвостом не отрезается.** `Path=C:\a ; note`
даст значение `C:\a ; note` целиком.

**Регистр имени не важен**, пробелы вокруг знака равенства и по краям значения
отбрасываются, обрамляющие двойные кавычки снимаются.

## Состояния параметров в этом файле

| Состояние | Сколько | Что значит |
|---|---|---|
| действует | 261 | строка есть, касса её читает |
| не читается | 43 | строка есть, но перебита дублем выше или отключена решёткой |
| мёртвая | 52 | имени нет ни в одном исходнике: строка не делает ничего |

Касса знает 863 параметров всего; 558 из них в этом файле не
записаны и работают со значениями по умолчанию.

---

## Строки, которые касса не читает

Их 43 . Каждая из них выглядит как настройка, но ни на что не влияет.

| Параметр | Строка | Значение | Почему не читается |
|---|---|---|---|
| `APIScanerCOMPort` | 749 | `46` | отключена решёткой |
| `AutorizationCod` | 217 | `300183` | отключена решёткой |
| `BarcodePrefixCode` | 560 | `2` | отключена решёткой |
| `BringToFrontAtStartup` | 489 | `true` | отключена решёткой |
| `BusyWaitTimeoutPOSTermLine` | 616 | `50` | отключена решёткой |
| `CekVisisble` | 357 | `false` | отключена решёткой |
| `CheckDateTimeEnabled` | 541 | `true` | отключена решёткой |
| `CheckScalesOnStart` | 627 | `true` | отключена решёткой |
| `CopyErrTable` | 245 | `true` | отключена решёткой |
| `FP550BreakAfterOpenFiscal` | 564 | `false` | отключена решёткой |
| `FP550Display` | 690 | `true` | отключена решёткой |
| `FullPosCardPayment` | 584 | `false` | отключена решёткой |
| `GlobalDep` | 400 | `133` | отключена решёткой |
| `LoadDBUnivPhoto` | 675 | `true` | отключена решёткой |
| `LogOffEnable` | 628 | `true` | отключена решёткой |
| `LogoFromDB` | 558 | `true` | отключена решёткой |
| `LogTCPWrp` | 654 | `true` | отключена решёткой |
| `NrComandReportPass` | 421 | `true` | отключена решёткой |
| `OraHome` | 131 | `0` | отключена решёткой |
| `PersJurWithCardIsOutFN` | 638 | `true` | отключена решёткой |
| `PinOnTimer` | 377 | `true` | отключена решёткой |
| `POSTermPort` | 533 | `9999` | отключена решёткой |
| `RefreshUnirest` | 153 | `true` | отключена решёткой |
| `SelectPersonType` | 547 | `true` | отключена решёткой |
| `ShowCertifcatesLbls` | 578 | `true` | отключена решёткой |
| `SQLAllInOneBeg` | 346 | `begin yunirest.prepare_report_beg…` | отключена решёткой |
| `SQLHeader` | 351 | `SELECT nr_comand,NR_zaiavca,DATA_…` | отключена решёткой |
| `SQLMaster` | 352 | `SELECT ROWNUM rowno,bliuda,clcbli…` | отключена решёткой |
| `SSAddDisplayOnTop` | 599 | `true` | отключена решёткой |
| `SSSelectPackageOnStart` | 636 | `true` | отключена решёткой |
| `SyncFPDateTime` | 568 | `true` | отключена решёткой |
| `TCPSocketFPCardLetter` | 684 | `P` | отключена решёткой |
| `TCPSocketFPCashLetter` | 683 | `N` | отключена решёткой |
| `TCPSocketFPName` | 682 | `DATECS` | отключена решёткой |
| `TCPSocketFPPort` | 685 | `8880` | отключена решёткой |
| `TMEPOSIngenicoEnabled` | 593 | `true` | отключена решёткой |
| `TMEPOSVerifoneEnabled` | 594 | `true` | отключена решёткой |
| `TSSelfMenuID` | 674 | `15` | отключена решёткой |
| `UseED2500` | 437 | `true` | отключена решёткой |
| `UseNewScalesForm` | 554 | `true` | отключена решёткой |
| `UseTranslations` | 557 | `true` | отключена решёткой |
| `WriteLogDB` | 657 | `true` | отключена решёткой |
| `ZReminderEnabled` | 512 | `true` | отключена решёткой |

---

## Справочник по подсистемам

Знаком ⚠ помечены строки, которые касса не читает.

### Подключение и запуск

Схема Oracle, вид кассы, режим интерфейса. Читается раньше всего остального: пока эти параметры не разобраны, касса не знает, к чему подключаться и что показывать.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `BringToFrontAtStartup` ⚠ |  | булево | только файл | `true` | ucLogin.cpp:256 |
| `ForceSchemaParam` | `true` | булево | только файл | `false` | ucLogin.cpp:892 |
| `GlobalType` | `Cassa` | строка | только файл |  | ucLogin.cpp:333 |
| `OraHome` ⚠ |  | строка | только файл |  | ucLogin.cpp:242 |
| `Schema` | `bonuspos_self24` | строка | только файл | `pos` | ucLogin.cpp:418 |
| `Server` | `clouddev` | строка | только файл | `edServer->Text` | ucLogin.cpp:324 |
| `ShimbulNouVisible` | `true` | булево | только файл | `false` | ucLogin.cpp:876 |
| `Style` | `TS` | строка | только файл |  | ucLogin.cpp:334 |
| `UseTranslations` ⚠ |  | булево | база, затем файл | `false` | ucLogin.cpp:434 |

**`BringToFrontAtStartup`** — Выводить окно кассы поверх других при запуске.

**`ForceSchemaParam`** — Не давать кассиру менять схему в окне входа.

**`GlobalType`** — Вид установки: `Cassa` — магазин, `Unirest` — ресторан. От него зависит набор окон. Возможные значения: `Cassa`, `Unirest`.

**`OraHome`** — Каталог клиента Oracle, если их на машине несколько.

**`Schema`** — Имя схемы Oracle. Подставляется в окно входа.

**`Server`** — Псевдоним базы Oracle, к которой подключается касса.

**`ShimbulNouVisible`** — Показывать кнопку открытия новой смены.

**`Style`** — Вид интерфейса кассира. `TS` — тачскрин, `RESTH` — ресторанный. Самый заметный параметр файла: меняет кассу целиком. Возможные значения: `TS`, `RESTH`, `DG1`.

**`UseTranslations`** — Брать подписи из таблицы переводов, а не из кода.

### Ядро кассы и оборудование

Самая большая группа. Здесь фискальный принтер, банковский терминал, экран покупателя, весы, журналы и десятки правил поведения чека. Модуль данных читает их при старте и держит в полях до конца работы.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `ActivateFiscNoteOnClientSelect` | `true` | булево | база, затем файл | `false` | dtmod.cpp:10942 |
| `AddDisplayEnabled` | `false` | булево | файл, затем база | `false` | dtmod.cpp:509 |
| `AddLogMsg` | `true` | булево | только база | `false` | dtmod.cpp:4630, uErrDialog.cpp:46 |
| `AdminViewSelfDocs` | `true` | булево | база, затем файл | `false` | dtmod.cpp:489 |
| `AtOncePrint` | `false` | булево | только файл | `false` | dtmod.cpp:1229 |
| `AutoCheck` | `true` | булево | файл, затем база | `false` | dtmod.cpp:503 |
| `AutoEnableTMH` | `true` | булево | файл, затем база | `false` | dtmod.cpp:552 |
| `AutorizationCod` ⚠ | *(секрет, не показывается)* | строка | только файл | `300183` | dtmod.cpp:6564 |
| `BackAdminTime` | `40` | целое | только файл | `7` | dtmod.cpp:7047 |
| `BarcodePrefixCode` ⚠ |  | целое | база, затем файл | `36` | dtmod.cpp:505 |
| `BlockCancel` | `false` | булево | база, затем файл | `false` | dtmod.cpp:493 |
| `BlockCardMultiPay` | `false` | булево | файл, затем база | `false` | dtmod.cpp:11583 |
| `BonDir` | `C:` | строка | только файл |  | dtmod.cpp:909 |
| `CanDisableTMH` | `false` | булево | файл, затем база | `false` | dtmod.cpp:550 |
| `CanModifyEmptyFPCReceipt` | `true` | булево | база, затем файл | `false` | dtmod.cpp:5017, fMenu.cpp:335 |
| `CanPayZeroBon` | `true` | булево | база, затем файл | `false` | dtmod.cpp:8005 |
| `CanPrintZeroPosition` | `false` | булево | база, затем файл | `false` | dtmod.cpp:7848 |
| `CantDecreaseByPIN` | `true` | булево | база, затем файл | `false` | dtmod.cpp:4719 |
| `CaptionCassirBarmen` | `Cassier` | строка | только файл | `кассир` | dtmod.cpp:5709, fMenu.cpp:2222, и ещё 2 |
| `CardPrefix` | `9804` | строка | только файл |  | dtmod.cpp:6972 |
| `CardPrefix2` | `981` | строка | только файл |  | dtmod.cpp:6973 |
| `CashOutOrder` | `true` | булево | база, затем файл | `false` | dtmod.cpp:12268, fMenu.cpp:1453 |
| `CassaDatecsNrLogic` | `101` | строка | только файл | `0` | dtmod.cpp:222 |
| `CekChecked` | `false` | булево | только файл | `false` | dtmod.cpp:975, order.cpp:209 |
| `CheckCanPrint` | `false` | булево | база, затем файл | `false` | dtmod.cpp:9901 |
| `CheckDateTimeEnabled` ⚠ |  | булево | файл, затем база | `false` | dtmod.cpp:12675 |
| `CheckFPCNewBon` | `true` | булево | база, затем файл | `false` | dtmod.cpp:3369 |
| `CheckScalesOnStart` ⚠ |  | булево | база, затем файл | `false` | dtmod.cpp:902 |
| `CheckTranzaction` | `true` | булево | только файл | `false` | dtmod.cpp:6623 |
| `ClientDefault` | `1763` | целое | только файл | `0` | dtmod.cpp:992 |
| `COM` | `6` | целое | только файл | `1` | dtmod.cpp:945 |
| `COMbaudrate` | `115200` | целое | только файл | `4800` | dtmod.cpp:6518 |
| `ComED2500` | `1` | целое | только файл | `1` | dtmod.cpp:10698 |
| `CommitOnUseCardNcp` | `true` | булево | база, затем файл | `false` | dtmod.cpp:7357 |
| `CopyErrTable` ⚠ |  | булево | только файл | `false` | dtmod.cpp:4647 |
| `CreateDocUN4` | `false` | булево | только файл | `false` | dtmod.cpp:5506 |
| `CustDisplay` | `Posiflex` | строка | файл, затем база | `ED2500` | dtmod.cpp:786 |
| `CustDisplayCOM` | `5` | целое | файл, затем база | `AppIniFile->ReadInteger("Ge…` | dtmod.cpp:10698 |
| `CustDisplayEnabled` | `false` | булево | файл, затем база | `false` | dtmod.cpp:781 |
| `DatecsFPModel` | `WP50MX` | строка | только файл |  | dtmod.cpp:7445 |
| `DatecsTypeProtocol` | `1` | целое | только файл | `0` | dtmod.cpp:7436 |
| `DelayFail` | `10` | строка | только файл | `10` | dtmod.cpp:4425 |
| `DeletePositionByPin` | `true` | булево | база, затем файл | `false` | dtmod.cpp:5167 |
| `DisableBeep` | `true` | булево | файл, затем база | `false` | dtmod.cpp:9309 |
| `DiscountCheckText` | `Вы сэкономили` | строка | база, затем файл | `REDUCERE` | dtmod.cpp:6259 |
| `DisplayOutputEnabled` | `false` | булево | файл, затем база | `true` | dtmod.cpp:9856 |
| `DocBase` | `99022` | строка | только файл |  | dtmod.cpp:3292 |
| `ErrorsMB` | `false` | булево | только файл | `false` | dtmod.cpp:9944 |
| `ErrorsUA` | `true` | булево | только файл | `false` | dtmod.cpp:9944 |
| `EurekaLogActive` | `false` | булево | только файл | `false` | dtmod.cpp:438 |
| `FiscalDeviceSerialNo` | `300042` | строка | только файл |  | dtmod.cpp:9861 |
| `FiscalDriverLog` | `true` | булево | файл, затем база | `true` | dtmod.cpp:9848 |
| `FiscalPrinter` | `VirtualFP` | строка | база, затем файл | `VirtualFP` | dtmod.cpp:248 |
| `FNCheckTvrCount` | `true` | булево | база, затем файл | `false` | dtmod.cpp:555 |
| `FNPrintBeforePayCard` | `true` | булево | база, затем файл | `false` | dtmod.cpp:11637 |
| `FNTvrCount` | `2` | целое | база, затем файл | `30` | dtmod.cpp:557 |
| `FP550BarcodeTypeCode` | `4` | целое | файл, затем база | `2` | dtmod.cpp:8578 |
| `FP550BreakAfterOpenFiscal` ⚠ |  | булево | файл, затем база | `false` | dtmod.cpp:7888 |
| `FP550DailySumsCode` | `65` | целое | файл, затем база | `67` | dtmod.cpp:8564 |
| `FP550Display` ⚠ |  | булево | файл, затем база | `false` | dtmod.cpp:784 |
| `FP550EmptyNFComand` | `true` | булево | файл, затем база | `false` | dtmod.cpp:7741 |
| `FP550SubTotalNewFormat` | `true` | булево | файл, затем база | `false` | dtmod.cpp:8993 |
| `FP550UseOpenPortL` | `true` | булево | файл, затем база | `false` | dtmod.cpp:7457 |
| `FullPosCardPayment` ⚠ |  | булево | база, затем файл | `true` | dtmod.cpp:515 |
| `GetPOSReportXZFromBD` | `true` | булево | файл, затем база | `false` | dtmod.cpp:11921 |
| `HideUnfiscalOnPreview` | `true` | булево | база, затем файл | `false` | dtmod.cpp:7155 |
| `LoadComenzAfterStart` | `true` | булево | только файл | `false` | dtmod.cpp:803 |
| `LogTCPWrp` ⚠ |  | булево | файл, затем база | `false` | dtmod.cpp:9662 |
| `MonoApplicationMode` | `true` | булево | база, затем файл | `false` | dtmod.cpp:494 |
| `MPPaymentCredit` | `1` | булево | файл, затем база | `false` | dtmod.cpp:7059 |
| `notTME&TMH` | `true` | булево | файл, затем база | `false` | dtmod.cpp:7651 |
| `PathPrinterTxt` | `\\Cassa\datecsep` | строка | только файл | `\\\\127.0.0.1\\datecsep` | dtmod.cpp:9449 |
| `PauseAfterPos` | `5` | целое | только база | `60` | dtmod.cpp:7805 |
| `PinOfficiant` | `false` | булево | только файл | `false` | dtmod.cpp:860, order.cpp:219 |
| `PinOnTimer` ⚠ |  | булево | только файл | `false` | dtmod.cpp:5244, fMenu.cpp:785 |
| `PosID` | `101` | строка | база, затем файл | `0` | dtmod.cpp:221, uLoyaltyUI.cpp:66, и ещё 1 |
| `POSTermIngenico` | `true` | булево | только файл | `false` | dtmod.cpp:642 |
| `POSTermNoOfCopiesCut` | `0` | целое | файл, затем база | `2` | dtmod.cpp:1546 |
| `POSTermPort` ⚠ |  | целое | файл, затем база | `9999` | dtmod.cpp:640 |
| `POSTermPrintRCPTAfterAsNewCheck` | `false` | булево | база, затем файл | `true` | dtmod.cpp:1715 |
| `POSTermPrintRCPTBefore` | `true` | булево | база, затем файл | `false` | dtmod.cpp:1662 |
| `POSTermSocketHost` | `127.0.0.1` | строка | файл, затем база | `127.0.0.1` | dtmod.cpp:627 |
| `POSTermSocketPort` | `9990` | целое | файл, затем база | `8882` | dtmod.cpp:628 |
| `PosWriteLogXZ` | `true` | булево | база, затем файл | `false` | dtmod.cpp:6446 |
| `PrintBonFRF` | `false` | булево | только файл | `true` | dtmod.cpp:9160, order.cpp:2446 |
| `PrintCashierNameInCheck` | `true` | булево | только файл | `false` | dtmod.cpp:1538 |
| `PrintRest` | `true` | булево | только файл | `false` | dtmod.cpp:1927 |
| `RefreshOnLoad` | `false` | булево | только файл | `false` | dtmod.cpp:775 |
| `RefreshUnirest` ⚠ |  | булево | только файл | `false` | dtmod.cpp:1304 |
| `SelectPersonType` ⚠ |  | булево | база, затем файл | `false` | dtmod.cpp:7325 |
| `SelfMode` | `false` | булево | база, затем файл | `false` | dtmod.cpp:895 |
| `SetClientCodeAskPayType` | `true` | булево | база, затем файл | `false` | dtmod.cpp:10946 |
| `ShowComandForAll` | `true` | булево | только файл | `false` | dtmod.cpp:1271 |
| `ShowTSSelPos` | `true` | булево | база, затем файл | `false` | dtmod.cpp:547 |
| `SQLAllInOneBeg` ⚠ |  | строка | только файл | `defSQLAllInOneBeg` | dtmod.cpp:5820 |
| `SyncFPDateTime` ⚠ |  | булево | файл, затем база | `true` | dtmod.cpp:7526 |
| `TCPSocketFPName` ⚠ |  | строка | база, затем файл | `TREMOL` | dtmod.cpp:251 |
| `TCPSocketFPPort` ⚠ |  | строка | база, затем файл | `8880` | dtmod.cpp:253 |
| `TcpwrpIP` | `<ip>` | строка | только файл |  | dtmod.cpp:9615 |
| `TcpwrpPort` | `4901` | целое | только файл | `0` | dtmod.cpp:9616 |
| `TcpwrpUseIDTCP` | `true` | булево | файл, затем база | `false` | dtmod.cpp:9525 |
| `TEMPLATE_DIR` | `D:\RAD_Tokyo\Sources\UAMenu\Win32\Debug\Templat…` | строка | только файл |  | dtmod.cpp:5717, ucLogin.cpp:519 |
| `TMEPOSIngenicoEnabled` ⚠ |  | булево | файл, затем база | `false` | dtmod.cpp:548 |
| `TMEPOSVerifoneEnabled` ⚠ |  | булево | файл, затем база | `false` | dtmod.cpp:549 |
| `TotalsVisible` | `false` | булево | только файл | `true` | dtmod.cpp:5751, ucLogin.cpp:555 |
| `UseED2500` ⚠ |  | булево | только файл | `false` | dtmod.cpp:781 |
| `UseEnvInirest` | `true` | булево | только файл | `true` | dtmod.cpp:473 |
| `UseNewScalesForm` ⚠ |  | булево | файл, затем база | `false` | dtmod.cpp:10520 |
| `UseOtdel` | `false` | булево | только файл | `false` | dtmod.cpp:3733 |
| `UseReportIni` | `true` | булево | только файл | `true` | dtmod.cpp:447 |
| `UseScaner` | `false` | булево | только файл | `false` | dtmod.cpp:776 |
| `UseTcpwrp` | `true` | булево | только файл | `false` | dtmod.cpp:777 |
| `UseTM` | `true` | булево | файл, затем база | `false` | dtmod.cpp:517 |
| `WordWrap` | `true` | булево | только файл | `false` | dtmod.cpp:7790 |
| `WriteLogDB` ⚠ |  | булево | только файл | `false` | dtmod.cpp:9384 |
| `WriteSqlMonLog` | `true` | булево | только файл | `false` | dtmod.cpp:433 |
| `ZeroPriceWarning` | `true` | булево | только база | `true` | dtmod.cpp:496 |
| `ZReminderEnabled` ⚠ |  | булево | база, затем файл | `false` | dtmod.cpp:12357 |

**`AddDisplayEnabled`** — Второй экран покупателя подключён.

**`AddLogMsg`** — Добавлять в журнал сообщения кассиру.

**`BackAdminTime`** — Через сколько секунд снимаются права старшего.

**`BlockCardMultiPay`** — Запретить оплату картой в мультиоплате.

**`BonDir`** — Каталог, куда складываются чеки.

**`CanPayZeroBon`** — Разрешить закрыть чек на нулевую сумму.

**`CanPrintZeroPosition`** — Разрешить строку чека с нулевой ценой.

**`CantDecreaseByPIN`** — Уменьшение количества требует ПИН-кода.

**`CardPrefix`** — Префикс номера карты лояльности.

**`CardPrefix2`** — Второй допустимый префикс номера карты.

**`CheckScalesOnStart`** — Проверять связь с весами при запуске.

**`CustDisplay`** — Модель экрана покупателя.

**`CustDisplayCOM`** — COM-порт экрана покупателя.

**`CustDisplayEnabled`** — Экран покупателя подключён.

**`DatecsFPModel`** — Модель принтера Datecs.

**`DatecsTypeProtocol`** — Версия протокола Datecs.

**`DeletePositionByPin`** — Удаление строки чека требует ПИН-кода.

**`DisplayOutputEnabled`** — Выводить строки чека на экран покупателя.

**`DocBase`** — База документов.

**`EurekaLogActive`** — Ловить исключения средствами EurekaLog.

**`FiscalDeviceSerialNo`** — Заводской номер принтера, сверяется при старте.

**`FiscalDriverLog`** — Писать журнал обмена с принтером.

**`FiscalPrinter`** — Драйвер фискального принтера. Значение `VirtualFP` включает эмулятор: чек рисуется на экране и никуда не печатается. Возможные значения: `VirtualFP`, `DatecsFP550`, `ElicomFP`, `ElicomECR`, `DaisyMicroC`, `Daisy`, `IKCE260T`, `Mercury114`, `Mercury114TXT`, `SocketFP`.

**`FullPosCardPayment`** — Оплачивать картой всю сумму целиком.

**`MonoApplicationMode`** — Не давать запустить вторую копию кассы.

**`MPPaymentCredit`** — Колонка суммы кредита в истории чеков. Значение 0 добавляет в запрос колонку, которая в представлении уже есть, и запрос падает с ORA-00918.

**`PathPrinterTxt`** — Куда складывать чек, печатаемый в файл.

**`PinOnTimer`** — Запрашивать ПИН-код по бездействию.

**`PosID`** — Номер кассы.

**`POSTermIngenico`** — Терминал Ingenico.

**`POSTermNoOfCopiesCut`** — Сколько копий отрезать.

**`POSTermPort`** — COM-порт терминала.

**`POSTermPrintRCPTAfterAsNewCheck`** — Печатать слип после, отдельным чеком.

**`POSTermPrintRCPTBefore`** — Печатать слип до чека.

**`POSTermSocketHost`** — Адрес терминала в сети.

**`POSTermSocketPort`** — Порт терминала в сети.

**`PrintRest`** — Печатать сдачу в чеке.

**`SelfMode`** — Касса работает как киоск самообслуживания.

**`SyncFPDateTime`** — Синхронизировать часы принтера с часами кассы.

**`TCPSocketFPName`** — Адрес принтера, подключённого по сети.

**`TCPSocketFPPort`** — Порт принтера, подключённого по сети.

**`TEMPLATE_DIR`** — Каталог с шаблонами печатных форм.

**`UseNewScalesForm`** — Новое окно работы с весами.

**`WriteLogDB`** — Писать журнал работы в базу.

**`WriteSqlMonLog`** — Писать журнал всех запросов к базе. Сильно замедляет кассу, включать только для разбора.

**`ZeroPriceWarning`** — Предупреждать о товаре с нулевой ценой.

### Окно кассира и работа с чеком

Поведение основного окна продажи: что видно кассиру, что разрешено делать с чеком, как ведёт себя карта лояльности в строке чека.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `ActivateHiddenBrowseChecksList` | `true` | булево | база, затем файл | `false` | Uhvbb.cpp:3122, fMenu.cpp:1759 |
| `ActiveCard` | `true` | булево | только файл | `false` | Uhvbb.cpp:617, order.cpp:947 |
| `APILoyalty` | `false` | булево | база, затем файл | `false` | Uhvbb.cpp:2876, dtmod.cpp:1778, и ещё 1 |
| `APILoyaltyAcumulate` | `false` | булево | база, затем файл | `false` | Uhvbb.cpp:2881, uLoyalitySelect.cpp:22, и ещё 1 |
| `APISincronyzeOffline` | `false` | булево | файл, затем база | `false` | Uhvbb.cpp:142 |
| `AutoCancelCheckByPIN` | `true` | булево | база, затем файл | `false` | Uhvbb.cpp:957, dtmod.cpp:13340 |
| `AutoCancelCheckInDB` | `false` | булево | база, затем файл | `true` | Uhvbb.cpp:981 |
| `BonFiscal` | `true` | булево | только файл | `false` | Uhvbb.cpp:650, dtmod.cpp:280, и ещё 1 |
| `BusyWaitTimeout` | `0` | целое | файл, затем база | `0` | Uhvbb.cpp:791, dtmod.cpp:1554 |
| `CancelCard` | `true` | булево | только файл | `false` | Uhvbb.cpp:1693, order.cpp:761 |
| `CardNCpFromManualBarcod` | `true` | булево | только файл | `false` | Uhvbb.cpp:1378, Uscan.cpp:15 |
| `CekVisisble` ⚠ |  | булево | только файл | `true` | Uhvbb.cpp:209, order.cpp:177 |
| `CheckFPC` | `true` | булево | база, затем файл | `false` | Uhvbb.cpp:662, dtmod.cpp:3349 |
| `CheckPay` | `2` | целое | только файл | `1` | Uhvbb.cpp:262, order.cpp:1043 |
| `FillRcptInComenzAdd` | `true` | булево | база, затем файл | `false` | Uhvbb.cpp:507, dtmod.cpp:1620 |
| `FindTovarByArticol` | `false` | булево | только файл | `false` | Uhvbb.cpp:1811 |
| `FindTovarByShortCode` | `false` | булево | только файл | `false` | Uhvbb.cpp:1826 |
| `IgnoreNFPErrors` | `true` | булево | база, затем файл | `false` | Uhvbb.cpp:847 |
| `ImageBackGroundPath` | `C:\Windows\Bomba_big.jpg` | строка | только файл |  | Uhvbb.cpp:148 |
| `lbCardBonusVisible` | `false` | булево | файл, затем база | `true` | Uhvbb.cpp:1944 |
| `LoadDBUnivPhoto` ⚠ |  | булево | база, затем файл | `false` | Uhvbb.cpp:3024, fMenu.cpp:1774 |
| `LogoFromDB` ⚠ |  | булево | база, затем файл | `false` | Uhvbb.cpp:3018 |
| `NewCloseForm` | `true` | булево | только файл | `true` | Uhvbb.cpp:201, dtmod.cpp:4823 |
| `NFPEnabled` | `true` | булево | файл, затем база | `false` | Uhvbb.cpp:3098 |
| `PersJurIsOutFN` | `false` | булево | база, затем файл | `false` | Uhvbb.cpp:1057, dtmod.cpp:10159 |
| `PersJurIsOutFNNoCopies` | `2` | целое | файл, затем база | `2` | Uhvbb.cpp:1073 |
| `PersJurWithCardIsOutFN` ⚠ |  | булево | база, затем файл | `false` | Uhvbb.cpp:1058, dtmod.cpp:10162 |
| `PosTermCancelOnBonCancel` | `true` | булево | только файл | `false` | Uhvbb.cpp:1618 |
| `PosTermPrintCheckCopy` | `false` | булево | база, затем файл | `false` | Uhvbb.cpp:782 |
| `PrintAfterPay` | `false` | булево | только файл | `false` | Uhvbb.cpp:1474 |
| `PrintReportTxtCom` | `false` | булево | только файл | `false` | Uhvbb.cpp:1105 |
| `ResolutionTerminal` | `false` | булево | только файл | `false` | Uhvbb.cpp:185, dtmod.cpp:6785, и ещё 2 |
| `ScanerHideContentForCards` | `true` | булево | база, затем файл | `false` | Uhvbb.cpp:1941 |
| `ShowCertifcatesLbls` ⚠ |  | булево | база, затем файл | `false` | Uhvbb.cpp:168, dtmod.cpp:4952 |
| `SpecialCheckFailedMsg` | `false` | булево | база, затем файл | `false` | Uhvbb.cpp:301, dtmod.cpp:11402 |
| `SplitterTSBEnabled` | `false` | булево | файл, затем база | `true` | Uhvbb.cpp:2701 |

**`APILoyalty`** — Работа с внешним сервисом лояльности включена.

**`APILoyaltyAcumulate`** — Начислять баллы, а не только списывать.

**`APISincronyzeOffline`** — Отключить онлайн-синхронизацию. Нужно на прогонах: иначе запуск упирается в сертификат.

**`AutoCancelCheckByPIN`** — Автоматическая отмена чека требует ПИН-кода.

**`BonFiscal`** — Печатать фискальный чек. Выключено — чек нефискальный.

**`CheckPay`** — Правило оплаты чека. Разбирается в коде закрытия чека.

**`FillRcptInComenzAdd`** — Automatically fills the receipt when adding a command. (из перечня заказчика)

**`IgnoreNFPErrors`** — Specifies whether to ignore non-fatal fiscal printer errors. (из перечня заказчика)

**`PosTermCancelOnBonCancel`** — Отменять оплату картой при отмене чека.

**`ShowCertifcatesLbls`** — Controls the display of labels for certificates. (из перечня заказчика)

**`SpecialCheckFailedMsg`** — Specifies whether to display a special message when a check fails. (из перечня заказчика)

**`SplitterTSBEnabled`** — Разрешить менять размер панели кнопок мышью.

### Главное меню и права по ПИН-коду

Какие пункты меню показывать и какие действия закрывать ПИН-кодом старшего. Выключенный пункт меню не прячет саму возможность — он прячет кнопку.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `AllowActivateVirtualFP` | `true` | булево | только база | `false` | fMenu.cpp:1303 |
| `AllowInitFP` | `true` | булево | только база | `false` | fMenu.cpp:1301 |
| `APIScanerCOMPort` ⚠ |  | строка | база, затем файл |  | fMenu.cpp:2656 |
| `BrowseChecksListByPIN` | `true` | булево | только файл | `false` | fMenu.cpp:1762 |
| `BrowseUnfiscalChecksListByPIN` | `true` | булево | только файл | `false` | fMenu.cpp:1788 |
| `CancelCheckByPIN` | `true` | булево | только файл | `false` | fMenu.cpp:267 |
| `CantinaCardsEnabled` | `true` | булево | файл, затем база | `false` | fMenu.cpp:1386 |
| `FP550ZMode` | `0` | целое | файл, затем база | `Z_MODE1` | fMenu.cpp:1864 |
| `LogOffEnable` ⚠ |  | булево | база, затем файл | `false` | fMenu.cpp:1336 |
| `LogOffTime` | `15000` | целое | база, затем файл | `300000` | fMenu.cpp:76 |
| `LogWMChar` | `true` | булево | база, затем файл | `false` | fMenu.cpp:612 |
| `mItemMIA` | `true` | булево | база, затем файл | `false` | fMenu.cpp:79 |
| `SeveralTovarScanCheck` | `false` | булево | база, затем файл | `true` | fMenu.cpp:715 |
| `ShowMenuDatecsReadEJ` | `true` | булево | только база | `false` | fMenu.cpp:1314 |
| `ShowMenuPayCardTerm` | `true` | булево | файл, затем база | `true` | fMenu.cpp:1410 |
| `ShowMenuPreview` | `false` | булево | только база | `false` | fMenu.cpp:1334 |
| `ShowMenuReports` | `true` | булево | только база | `false` | fMenu.cpp:1313 |
| `ShowMenuSelfService` | `true` | булево | файл, затем база | `false` | fMenu.cpp:1315 |
| `UseWholeReturn` | `true` | булево | только база | `false` | fMenu.cpp:1290 |

**`BrowseChecksListByPIN`** — Просмотр списка чеков требует ПИН-кода.

**`BrowseUnfiscalChecksListByPIN`** — Просмотр нефискальных чеков требует ПИН-кода.

**`CancelCheckByPIN`** — Отмена чека требует ПИН-кода старшего.

**`LogOffEnable`** — Выходить из смены по бездействию.

**`LogOffTime`** — Через сколько секунд бездействия выходить.

### Заказы и печатные формы

Режим заказов: шаблоны печати, запросы выборки, поведение списка.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `AllowPrintSeveralTimes` | `true` | булево | только файл | `false` | order.cpp:2402 |
| `AvansTemplate` | `Disp_incasare_casa.frf` | строка | только файл | `cek.fr3` | order.cpp:1129 |
| `CekTemplate` | `Pub3_ContPentruPlata.frf` | строка | только файл | `cek.fr3` | order.cpp:1131 |
| `DblClick` | `false` | булево | только файл | `false` | order.cpp:1638 |
| `DefaultDataFilterCod` | `7` | целое | только файл | `-1` | order.cpp:152 |
| `DelaySessionOfficiant` | `15` | целое | только файл | `1` | order.cpp:147 |
| `DublEnabled` | `false` | булево | только файл | `false` | order.cpp:245 |
| `HideAnul` | `false` | булево | только файл | `false` | order.cpp:166 |
| `NotCloseDatasetFiltr` | `true` | булево | только файл | `false` | order.cpp:141 |
| `OrderComenzdSortAsc` | `true` | булево | только файл | `false` | order.cpp:111 |
| `OrderStateVisible` | `true` | булево | только файл | `true` | order.cpp:179 |
| `SilentPrint` | `true` | булево | только файл | `false` | order.cpp:2434 |
| `SQLAllInOneAvans` | `begin yunirest.prepare_report_avans(:SQLHeader,…` | строка | только файл |  | order.cpp:1097 |
| `SQLAllInOneCek` | `begin unirest_rep.AllInOneCek(:SQLHeader,:SQLMa…` | строка | только файл |  | order.cpp:1099 |
| `SQLHeader` ⚠ |  | строка | только файл | `defHeader` | order.cpp:1120 |
| `SQLMaster` ⚠ |  | строка | только файл | `defMaster` | order.cpp:1121 |
| `UseTerminal` | `true` | булево | только файл | `true` | order.cpp:218 |

### Лояльность: экран покупателя

Окно карты лояльности целиком: подписи на трёх языках и цвета кнопок. Подпись задаётся одной строкой вида `румынский|русский|английский`.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `APIBaseURL` | `ENC:ФгйФЧџҐ’НЯЮ’ЧЗ¤ДОЬбУЭЖвЧеќЦФФ` | строка | база, затем файл | `https://api.sb.abmloyalty.a…` | uLoyaltyUI.cpp:41 |
| `APIDebugMode` | `true` | булево | база, затем файл | `false` | uLoyaltyUI.cpp:147 |
| `APILoyaltyAvailableText` | `Aveti disponibil:\|Вам доступно:\|Available point…` | подпись на трёх языках | файл, затем база | `Aveti disponibil:\|Вам досту…` | uLoyaltyUI.cpp:86 |
| `APILoyaltyBtnPadBgColor` | `RGB(0, 139, 88)` | строка | база, затем файл | `RGB(0, 139, 88)` | uLoyaltyUI.cpp:95 |
| `APILoyaltyBtnPadFontColor` | `RGB(0, 0, 0)` | строка | база, затем файл | `RGB(0, 0, 0)` | uLoyaltyUI.cpp:94 |
| `APILoyaltyCardInfoText` | `Introduceti numarul cardui\|Введите № Карты \|Ent…` | подпись на трёх языках | файл, затем база | `Introduceti numarul cardui\|…` | uLoyaltyUI.cpp:80 |
| `APILoyaltyCardText` | `Card\| \|Card` | подпись на трёх языках | файл, затем база | `Card\|Карточка\|Card` | uLoyaltyUI.cpp:81 |
| `APILoyaltyChPhoneCardBgColor` | `RGB(0, 139, 88)` | строка | база, затем файл | `RGB(0, 139, 88)` | uLoyaltyUI.cpp:119 |
| `APILoyaltyChPhoneCardFontColor` | `RGB(0, 0, 0)` | строка | база, затем файл | `RGB(0, 0, 0)` | uLoyaltyUI.cpp:118 |
| `APILoyaltyExitBgColor` | `RGB(215, 0, 0)` | строка | база, затем файл | `RGB(215, 0, 0)` | uLoyaltyUI.cpp:92 |
| `APILoyaltyExitFontColor` | `RGB(0, 0, 0)` | строка | база, затем файл | `RGB(0, 0, 0)` | uLoyaltyUI.cpp:91 |
| `APILoyaltyExitText` | `IESIRE\|ВЫХОД\|EXIT` | подпись на трёх языках | файл, затем база | `IESIRE\|ВЫХОД\|EXIT` | uLoyaltyUI.cpp:89 |
| `APILoyaltyNameText` | `Nume\|Имя\|Name` | подпись на трёх языках | файл, затем база | `Nume\|Имя\|Name` | uLoyaltyUI.cpp:84 |
| `APILoyaltyPhone` | `false` | булево | база, затем файл | `false` | uLoyaltyUI.cpp:124 |
| `APILoyaltyPhoneText` | `Telefon\|Телефон\|Phone` | подпись на трёх языках | файл, затем база | `Telefon\|Телефон\|Phone` | uLoyaltyUI.cpp:82 |
| `APILoyaltyRestrictDiscount` | `false` | булево | база, затем файл | `false` | uLoyaltyUI.cpp:604 |
| `APILoyaltySearchBgColor` | `RGB(0, 139, 88)` | строка | база, затем файл | `RGB(0, 139, 88)` | uLoyaltyUI.cpp:116 |
| `APILoyaltySearchFontColor` | `RGB(0, 0, 0)` | строка | база, затем файл | `RGB(0, 0, 0)` | uLoyaltyUI.cpp:115 |
| `APILoyaltySearchText` | `Cauta\|Поиск\|Search` | подпись на трёх языках | файл, затем база | `Cauta\|Поиск\|Search` | uLoyaltyUI.cpp:83 |
| `APILoyaltySendText` | `Trimite\|Отправить\|Send` | подпись на трёх языках | файл, затем база | `Trimite\|Послать\|Send` | uLoyaltyUI.cpp:88 |
| `APILoyaltySurnameText` | `Prenume\|Фамилия\|Surname` | подпись на трёх языках | файл, затем база | `Prenume\|Фамилия\|Surname` | uLoyaltyUI.cpp:85 |
| `APILoyaltyUseBgColor` | `RGB(0, 139, 88)` | строка | база, затем файл | `RGB(0, 139, 88)` | uLoyaltyUI.cpp:113 |
| `APILoyaltyUseFontColor` | `RGB(0, 0, 0)` | строка | база, затем файл | `RGB(0, 0, 0)` | uLoyaltyUI.cpp:112 |
| `APILoyaltyUseText` | `Uitilizeaza cantiate:\|Использовать кол-во:\|Use:` | подпись на трёх языках | файл, затем база | `Uitilizeaza cantiate:\|Испол…` | uLoyaltyUI.cpp:87 |
| `GlobalDep` ⚠ |  | целое | только файл | `0` | uLoyaltyUI.cpp:65, ucLogin.cpp:448 |

**`APIBaseURL`** — Адрес сервиса лояльности.

**`APIDebugMode`** — Подробный журнал обмена с сервисом лояльности.

**`GlobalDep`** — Номер подразделения. От него зависит, какие прайс-листы видит касса, см. docs/erp-price-boundary.md.

### Лояльность: связь с сервисом

Адрес и ключ POS API сервиса карт в мобильном кошельке. Ключ в файле рядом с exe — не лучшее место, см. docs/loyalty-providers.md.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `PosApiBaseURL` | `https://nufarul.eminescu.md/myloyalwalletcard/a…` | строка | база, затем файл |  | uLoyaltyPosApi.cpp:26 |
| `PosApiKey` | *(секрет, не показывается)* | строка | база, затем файл |  | uLoyaltyPosApi.cpp:34 |
| `PosApiSimulate` | `0` | булево | база, затем файл | `false` | uLoyaltyPosApi.cpp:41 |
| `PosApiTimeoutMs` | `8000` | целое | база, затем файл | `8000` | uLoyaltyPosApi.cpp:113 |

**`PosApiBaseURL`** — Адрес POS API сервиса карт в мобильном кошельке.

**`PosApiKey`** — Ключ доступа к этому сервису. Секрет, в репозиторий не попадает.

**`PosApiSimulate`** — Отвечает встроенная имитация, в сеть касса не ходит.

**`PosApiTimeoutMs`** — Выдержка ожидания ответа сервиса, миллисекунды.

### Оплата MIA

Мгновенные платежи MIA: режим работы, доступ к API банка и выдержки ожидания. Режим `simulate` отвечает локально и в сеть не ходит.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `MIAClientId` | *(пусто — значит не задан)* | строка | файл, затем база |  | uMIARest.cpp:118 |
| `MIAClientSecret` | *(секрет, не показывается)* | строка | файл, затем база |  | uMIARest.cpp:119 |
| `MIAMode` | `simulate` | строка | база, затем файл | `printer` | uMIARest.cpp:28 |
| `MIAPollIntervalMs` | `1500` | целое | база, затем файл | `2000` | uMIARest.cpp:319 |
| `MIAPollTimeoutSec` | `60` | целое | база, затем файл | `120` | uMIARest.cpp:320 |
| `MIAQrLifetimeSec` | `300` | целое | база, затем файл | `300` | uMIARest.cpp:191 |
| `MIARestBaseURL` | *(пусто — значит не задан)* | строка | база, затем файл |  | uMIARest.cpp:34 |
| `MIATerminalId` | *(пусто — значит не задан)* | строка | файл, затем база |  | uMIARest.cpp:203 |
| `MIAUseTestPay` | `0` | булево | база, затем файл | `false` | uMIARest.cpp:311 |

**`MIAClientId`** — Идентификатор клиента в API банка. Секрет.

**`MIAClientSecret`** — Пароль клиента в API банка. Секрет.

**`MIAMode`** — Как проводится оплата MIA: `printer` — через фискальный принтер, `rest` — через API банка, `simulate` — тот же протокол с локальными ответами. Возможные значения: `printer`, `rest`, `simulate`.

**`MIAPollIntervalMs`** — Как часто спрашивать банк о результате.

**`MIAPollTimeoutSec`** — Сколько всего ждать оплаты.

**`MIAQrLifetimeSec`** — Сколько секунд живёт QR-код на оплату.

**`MIARestBaseURL`** — Адрес API банка для режима `rest`.

**`MIATerminalId`** — Номер терминала в API банка.

**`MIAUseTestPay`** — Имитировать оплату вызовом песочницы банка.

### Оплата MIA: реквизиты

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `MIAApiIBAN` | `MD11QW000000000937769542` | строка | файл, затем база |  | uMIAPayments.cpp:217, uMIARest.cpp:315 |

### Эмулятор фискального принтера

Окно, в котором чек рисуется на экране вместо печати на настоящем принтере. См. docs/fiscal-emulator.md.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `VirtualFPCloseAfterSec` | `30` | целое | база, затем файл | `30` | uFiscalView.cpp:369 |
| `VirtualFPLineDelayMs` | `180` | целое | база, затем файл | `60` | uFiscalView.cpp:348 |
| `VirtualFPShotAtLine` | `6` | целое | база, затем файл | `0` | uFiscalView.cpp:335 |
| `VirtualFPWindowWidth` | `520` | целое | база, затем файл | `420` | uFiscalView.cpp:31 |

**`VirtualFPCloseAfterSec`** — Через сколько секунд окно закроется само. Ноль — ждать кассира.

**`VirtualFPLineDelayMs`** — Задержка между строками, чтобы печать было видно.

**`VirtualFPShotAtLine`** — На какой строке снять экран для протокола.

**`VirtualFPWindowWidth`** — Ширина окна эмулятора в точках.

### Самообслуживание

Киоск самообслуживания: весы, логотип, страница благодарности.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `CategoryButtonSetup` | `true` | булево | файл, затем база | `false` | uSelfService.cpp:1225 |
| `SSGetWeightOnShowScale` | `true` | булево | база, затем файл | `false` | uSelfService.cpp:1769 |
| `SSSelectPackageOnStart` ⚠ |  | булево | база, затем файл | `false` | uSelfService.cpp:741 |
| `SSShowLogoImage` | `true` | булево | база, затем файл | `true` | uSelfService.cpp:2072 |
| `SSThanksInterval` | `1000` | целое | база, затем файл | `30000` | uSelfService.cpp:473 |
| `SSWeightThreads` | `true` | булево | база, затем файл | `false` | uSelfService.cpp:1609 |

**`SSGetWeightOnShowScale`** — Считывать вес сразу при показе окна весов.

**`SSSelectPackageOnStart`** — Determines if a package selection is required at the start of the self-service session. (из перечня заказчика)

**`SSShowLogoImage`** — Показывать логотип на экране киоска.

**`SSThanksInterval`** — Сколько секунд показывать страницу благодарности.

**`SSWeightThreads`** — Number of threads used for weight processing in self-service mode. (из перечня заказчика)

### Самообслуживание: витрина с картинками

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `SSAddDisplayOnTop` ⚠ |  | булево | база, затем файл | `false` | uImgMenu.cpp:250, uSelfService.cpp:427 |
| `TSSelfMenuID` ⚠ |  | целое |  | `2` | uImgMenu.cpp:64, uSelfService.cpp:1153 |

**`SSAddDisplayOnTop`** — Держать второй экран поверх остальных окон.

**`TSSelfMenuID`** — Номер набора кнопок витрины самообслуживания.

### Тачскрин: кнопки и витрина

Внешний вид сетки кнопок. Сами кнопки в файле не описаны: они лежат в базе, а файл задаёт только их вид и номера наборов.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `POSTermSocket` | `false` | булево | только файл | `false` | TS.cpp:1216, TSPOSTermIP.cpp:406, и ещё 3 |
| `SSScaleFactor` | `67` | целое | база, затем файл | `100` | TS.cpp:531, uImgMenu.cpp:59, и ещё 2 |
| `TSUseMultiTab` | `true` | булево | база, затем файл | `true` | TS.cpp:1418 |
| `UseTSLang` | `false` | булево | база, затем файл | `true` | TS.cpp:1408 |

**`POSTermSocket`** — Связь с терминалом по сети, а не по COM-порту.

**`SSScaleFactor`** — Масштаб кнопок в процентах.

**`TSUseMultiTab`** — Показывать страницы кнопок вкладками.

**`UseTSLang`** — Брать подписи кнопок на языке интерфейса.

### Тачскрин: поведение

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `CostumSelectPage` | `true` | булево | база, затем файл | `false` | TSController.cpp:761, uSelfService.cpp:332 |

### Тачскрин: оплата картой

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `POSRRNByPIN` | `true` | булево | только файл | `true` | TSPOSTermIP.cpp:220 |

**`POSRRNByPIN`** — Просмотр номера банковской операции требует ПИН-кода.

### Мультиоплата

Окно, в котором чек раскладывается на несколько средств оплаты.

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `POSTermEnabled` | `true` | булево | база, затем файл | `false` | MultiPaymentsPay.cpp:202, Uclose_bon.cpp:528, и ещё 3 |
| `TSPOSShowForm` | `true` | булево | файл, затем база | `false` | MultiPaymentsPay.cpp:278, dtmod.cpp:11748 |

**`POSTermEnabled`** — Банковский терминал подключён.

**`TSPOSShowForm`** — Показывать окно оплаты картой в режиме тачскрина.

### Закрытие чека

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `CanCancelPOSPay` | `false` | булево | база, затем файл | `false` | Uclose_bon.cpp:351 |
| `PaymentsEnabled` | `true` | булево | база, затем файл | `false` | Uclose_bon.cpp:458, dtmod.cpp:10247, и ещё 1 |
| `ShowCertificateField` | `true` | булево | база, затем файл | `false` | Uclose_bon.cpp:294 |

**`CanCancelPOSPay`** — Разрешить отмену оплаты картой.

**`PaymentsEnabled`** — Окно способов оплаты включено.

**`ShowCertificateField`** — Показывать поле сертификата при закрытии чека.

### Фискальный принтер: общее

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `BusyWaitTimeoutPOSTermLine` ⚠ |  | целое | файл, затем база | `0` | CustomFiscalPrintDevice.cpp:163 |
| `FPFiscalTextLen` | `34` | целое | файл, затем база | `30` | CustomFiscalPrintDevice.cpp:26, Daisy.cpp:10, и ещё 3 |
| `PaperCutPosTerm` | `false` | булево | файл, затем база | `true` | CustomFiscalPrintDevice.cpp:28 |
| `PrintRCPTClearEmptyLines` | `true` | булево | база, затем файл | `true` | CustomFiscalPrintDevice.cpp:177, Utils.cpp:545 |

**`FPFiscalTextLen`** — Ширина строки чека в знаках.

**`PaperCutPosTerm`** — Отрезать ленту после слипа банковского терминала.

**`PrintRCPTClearEmptyLines`** — Убирать пустые строки из слипа терминала.

### Фискальный принтер Elicom и Datecs

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `ElicomCardCode` | `4` | целое | база, затем файл | `4` | ElicomFP.cpp:41 |
| `ElicomCertType` | `3` | целое | файл, затем база | `1` | ElicomFP.cpp:591, SocketFP.cpp:419, и ещё 1 |
| `ElicomFPPrintTextInCheckPaperCut` | `false` | булево | база, затем файл | `true` | ElicomFP.cpp:1333 |
| `ElicomTMECode` | `5` | целое | база, затем файл | `4` | ElicomFP.cpp:44 |
| `ElicomTMHCode` | `6` | целое | база, затем файл | `5` | ElicomFP.cpp:45 |
| `FPElicomLang` | `2` | целое | файл, затем база | `1` | ElicomFP.cpp:11 |
| `MultiPaymentEnabled` | `true` | булево | база, затем файл | `true` | ElicomFP.cpp:541, IKCE260T.cpp:556, и ещё 3 |
| `POSTermPrintRCPTAfterAsCurrentCheck` | `true` | булево | база, затем файл | `false` | ElicomFP.cpp:830, IKCE260T.cpp:547, и ещё 3 |

**`FPElicomLang`** — Язык чека у принтера Elicom.

**`MultiPaymentEnabled`** — Разрешить оплату чека несколькими средствами.

**`POSTermPrintRCPTAfterAsCurrentCheck`** — Печатать слип после, в том же чеке.

### Фискальный принтер по сети

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `DatecsFPTMELetter` | `5` | строка | только файл | `E` | SocketFP.cpp:383, dtmod.cpp:7447 |
| `TCPSocketFPCardLetter` ⚠ |  | строка | база, затем файл | `N` | SocketFP.cpp:389 |
| `TCPSocketFPCashLetter` ⚠ |  | строка | база, затем файл | `P` | SocketFP.cpp:388 |
| `TCPSocketFPDemoMode` | `true` | булево | файл, затем база | `false` | SocketFP.cpp:41 |

**`TCPSocketFPDemoMode`** — Сетевой принтер отвечает сам, ничего не печатая.

### Банковский терминал по сети

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `POSCurrencyID` | `498` | строка | файл, затем база | `498` | UnPOSTermIP.cpp:58 |
| `POSCurrencyName` | `MDL` | строка | файл, затем база | `MDL` | UnPOSTermIP.cpp:59, TSPOSTermIP.cpp:114, и ещё 1 |
| `POSKkmVer` | `2.0.16` | строка | файл, затем база | `2.0.16` | UnPOSTermIP.cpp:60 |
| `POSTermNoOfCopies` | `0` | целое | файл, затем база | `2` | UnPOSTermIP.cpp:598 |
| `POSTimeWaitResultOper` | `120` | строка | файл, затем база | `120` | UnPOSTermIP.cpp:61 |

**`POSTermNoOfCopies`** — Сколько копий слипа печатать.

**`POSTimeWaitResultOper`** — Сколько секунд ждать ответа терминала.

### Банковский терминал Ingenico

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `IngenicoCheckConnOp` | `96` | целое | файл, затем база | `90` | UnPOSTermIngen.cpp:185 |
| `IngenicoReceiptCopyOp` | `60` | целое | файл, затем база | `27` | UnPOSTermIngen.cpp:186 |

**`IngenicoCheckConnOp`** — Код операции проверки связи с терминалом.

**`IngenicoReceiptCopyOp`** — Код операции повторной печати слипа.

### Весы: товары с весом

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `AlwaysRefreshScalesGoodWeight` | `true` | булево | файл, затем база | `false` | ScalesI.cpp:63 |
| `CountScalesGoodWeight` | `10000` | целое | файл, затем база | `10` | ScalesI.cpp:135 |
| `RefreshScalesGoodWeightInterval` | `100` | целое | файл, затем база | `1000` | ScalesI.cpp:310 |
| `ShowSumScalesGoodWeight` | `true` | булево | файл, затем база | `false` | ScalesI.cpp:303 |

**`AlwaysRefreshScalesGoodWeight`** — Опрашивать весы непрерывно.

**`CountScalesGoodWeight`** — Сколько замеров усреднять.

**`RefreshScalesGoodWeightInterval`** — Как часто опрашивать весы.

**`ShowSumScalesGoodWeight`** — Показывать сумму рядом с весом.

### Весы

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `EnableTaraScalesGoodWeight` | `true` | булево | файл, затем база | `false` | Scales.cpp:92, ScalesI.cpp:203, и ещё 1 |

**`EnableTaraScalesGoodWeight`** — Разрешить учёт тары.

### Сертификаты

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `CertificatesWidth` | `600` | целое | база, затем файл | `Width` | Certificates.cpp:72 |

### Фискальная накладная

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `FNAllowPreview` | `true` | булево | база, затем файл | `false` | FiscalNote.cpp:96 |
| `FNTSMode` | `true` | булево | база, затем файл | `false` | FiscalNote.cpp:142 |

### Карта в мобильном кошельке

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `WalletPassTitle` | `MyLoyalWalletCard` | строка | база, затем файл | `MyLoyalWalletCard` | uWalletPass.cpp:40 |

**`WalletPassTitle`** — Название карты в мобильном кошельке.

### Общие

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `Language` | `ro` | строка |  | `ADefault` | Utils.cpp:143 |
| `StrictPrintRCPTClearEmptyLines` | `true` | булево | файл, затем база | `false` | Utils.cpp:505, dtmod.cpp:11421 |

**`Language`** — Язык интерфейса по умолчанию.

**`StrictPrintRCPTClearEmptyLines`** — То же, но строго: убираются и строки из одних пробелов.

### Считыватель карт

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `SCardReader` | `OMNIKEY CardMan 5x21-CL 0` | строка | файл, затем база |  | CardReader.cpp:56, SCardReader.cpp:29 |

### Прочее

| Параметр | Сейчас | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|---|
| `AddDisplayIdleMsgSize` | `70` | целое | база, затем файл | `36` | uAddDisplay.cpp:45 |
| `APIKey` | *(секрет, не показывается)* | строка | база, затем файл | `8de44b37-3fcc-4ffa-a540-c92…` | uLoyalityAPICommunication.cpp:29 |
| `APISyncRepeatTime` | `150000` | целое | файл, затем база | `14400000` | uLoyalityTThread.cpp:30 |
| `FNSaveToPdf` | `true` | булево | база, затем файл | `false` | FRep.cpp:84 |
| `NrComandReportPass` ⚠ |  | булево | только файл | `false` | reports.cpp:52 |
| `PaymentsGetUserMessage` | `false` | булево | база, затем файл | `true` | Payments.cpp:144 |
| `SQLListCard` | `Select cod,denumirea,to_number(codvechi) Nomina…` | строка | только файл |  | Uadaug.cpp:135 |
| `TSSELMenu` | `14` | целое |  | `12` | uSelMenu.cpp:29 |

**`AddDisplayIdleMsgSize`** — Sets the size of the idle message on the additional display. (из перечня заказчика)

**`PaymentsGetUserMessage`** — Determines if a user message should be retrieved during payments. (из перечня заказчика)

**`TSSELMenu`** — Номер набора кнопок выбора меню.

---

## Мёртвые параметры

Этих имён нет ни в одном исходнике кассы и ни в одном компоненте: ни как параметра, ни как строкового литерала. Строка в файле есть, смысла у неё нет. Проверено поиском по 852 файлам исходников.

Удалять их не обязательно, но и настраивать ими нечего. Скорее всего это следы прежних версий и чужих сборок: например семейство `Bank0_…`, `Bank1_…`, `Bank2_…` описывает выбор банка, которого в этой сборке нет.

| Параметр | Строка | Значение |
|---|---|---|
| `AdsTopTextVisible` | 600 | `false` |
| `allowCasirAlchoolPin` | 93 | `true` |
| `APIDebugCasa` | 76 | `true` |
| `APILoyaltyWorkType` | 79 | `2` |
| `AppDesign` | 81 | `DG1` |
| `Bank0_BankName` | 174 | `MAIB` |
| `Bank0_ButtonColor` | 177 | `0x00FFE0C0` |
| `Bank0_ConnectionParams` | 176 | `COM9` |
| `Bank0_ConnectionType` | 175 | `Arcus` |
| `Bank0_ImageFileName` | 178 | `maib.png` |
| `Bank1_BankName` | 180 | `MICB` |
| `Bank1_ButtonColor` | 183 | `0x00C0FFC0` |
| `Bank1_ConnectionParams` | 182 | `9999` |
| `Bank1_ConnectionType` | 181 | `IP` |
| `Bank1_ImageFileName` | 184 | `micb.png` |
| `Bank2_BankName` | 186 | `Victoriabank` |
| `Bank2_ButtonColor` | 188 | `0x00FFC0FF` |
| `Bank2_ConnectionParams` | 187 | `9990` |
| `Bank2_ImageFileName` | 189 | `exim.png` |
| `BankCount` | 173 | `3` |
| `BegTemplate` | 337 | `Beg.frf` |
| `CheckFnNeedOnReturn` | 548 | `true` |
| `coffeBrandId` | 99 | `3416` |
| `cuponPrefix` | 72 | `123` |
| `CuponPrefixFS` | 750 | `A3900,B3900,M3900` |
| `EnableMenuSave` | 330 | `true` |
| `excludeProductPrefix` | 41 | `20088` |
| `FilterClient` | 317 | `gr1 in ('R','E') and tip ='O'` |
| `hvbbComenzRestaurantSQL` | 100 | `select * from (     select  0.00 cred_s…` |
| `idBanks` | 191 | `{"banks":[{"id":1013,"name":"MICB"},{"i…` |
| `insertTMDBBankInfo` | 192 | `true` |
| `LastSchema` | 762 | `clouddev` |
| `licenseKey` | 119 | `@secret:cantina.ini/General/licenseKey` |
| `MIAApiKey` | 219 | `@secret:cantina.ini/General/MIAApiKey` |
| `MIAApiSecrect` | 220 | `@secret:cantina.ini/General/MIAApiSecrect` |
| `MIAQiwiMerchantPrefix` | 102 | `LOCAL_` |
| `MIAType` | 103 | `Qiwi` |
| `MIAWorkType` | 101 | `Dynamic` |
| `NavBtnStyle` | 89 | `2025` |
| `printCoffeQR` | 98 | `true` |
| `Reduction` | 315 | `10` |
| `ScanAnulPrefix` | 68 | `2200000123158` |
| `Scanner2_COMPort` | 686 | `46` |
| `selfAddBag` | 95 | `true` |
| `selfBagBarCode` | 761 | `9789975744218` |
| `SelfServiceWeb` | 125 | `true` |
| `SelfWebView` | 84 | `true` |
| `SSWebIdleTimeout` | 50 | `60` |
| `SSWebMonitor` | 83 | `1` |
| `SYSMultipos` | 172 | `false` |
| `TSFontLog` | 32 | `1` |
| `wmfCM` | 759 | `false` |

---

## Что ещё умеет касса

В файле не записано 558 параметров, которые касса читать умеет. Они работают со значениями по умолчанию. Список нужен, когда поведение надо изменить, а подходящей строки в файле нет — её достаточно дописать.

| Параметр | Тип | Откуда берётся | По умолчанию | Где читается |
|---|---|---|---|---|
| `AddDisplayAdInterval` | целое | файл, затем база | `5000` | dtmod.cpp:510 |
| `AddDisplayAdPath` | строка | файл, затем база | `Advertising` | dtmod.cpp:511 |
| `AddDisplayBonusBtnHeight` | целое | база, затем файл | `110` | uAddDisplay.cpp:212 |
| `AddDisplayBonusBtnSize` | целое | база, затем файл | `22` | uAddDisplay.cpp:156 |
| `AddDisplayBonusChoice` | булево | база, затем файл | `false` | dtmod.cpp:3095, uAddDisplay.cpp:68 |
| `AddDisplayBonusColor` | целое | база, затем файл | `128` | uAddDisplay.cpp:151 |
| `AddDisplayBonusStep` | целое | база, затем файл | `10` | dtmod.cpp:3101 |
| `AddDisplayBonusTimeout` | целое | база, затем файл | `60` | uAddDisplay.cpp:348 |
| `AddDisplayBonusTitleSize` | целое | база, затем файл | `28` | uAddDisplay.cpp:154 |
| `AddDisplayBonusValueSize` | целое | база, затем файл | `72` | uAddDisplay.cpp:155 |
| `AddDisplayCardColor` | целое | база, затем файл | `128` | uAddDisplay.cpp:111 |
| `AddDisplayCardFontSize` | целое | база, затем файл | `20` | uAddDisplay.cpp:114 |
| `AddDisplayCardHeight` | целое | база, затем файл | `92` | uAddDisplay.cpp:108 |
| `AddDisplayDecimalColor` | целое | база, затем файл | `128` | uAddDisplay.cpp:47 |
| `AddDisplayLogoPath` | строка | файл, затем база | `Advertising` | dtmod.cpp:512 |
| `AddDisplayShowCard` | булево | база, затем файл | `true` | dtmod.cpp:2733, uAddDisplay.cpp:65 |
| `AddScaleServerAutorun` | булево | файл, затем база | `false` | Scales.cpp:255, ScalesI.cpp:366 |
| `AddScaleServerClass` | строка | файл, затем база |  | Scales.cpp:257, ScalesI.cpp:368 |
| `AddScaleServerPath` | строка | файл, затем база |  | Scales.cpp:263, ScalesI.cpp:374 |
| `AddScaleServerTitle` | строка | файл, затем база |  | Scales.cpp:258, ScalesI.cpp:369 |
| `advancedMultipayment` | булево | файл, затем база | `false` | MultiPayments.cpp:48, MultiPaymentsPay.cpp:129, и ещё 1 |
| `AltDlgMode` | булево | база, затем файл | `false` | dtmod.cpp:507, ucLogin.cpp:336 |
| `APBSocketCheckOnStart` | булево | файл, затем база | `false` | UnAPBSocket.cpp:18 |
| `APBSocketHost` | строка | файл, затем база | `127.0.0.1` | dtmod.cpp:665 |
| `APBSocketPort` | целое | файл, затем база | `8885` | dtmod.cpp:666 |
| `APBSocketServerName` | строка | файл, затем база | `Server_PaymentApbQR.exe` | UnAPBSocket.cpp:14 |
| `APBSocketServerPath` | строка | файл, затем база | `IncludeTrailingBackslas…` | UnAPBSocket.cpp:17 |
| `APBSocketUpTimeOut` | целое | файл, затем база | `10` | UnAPBSocket.cpp:74 |
| `APBTerminalID` | строка | файл, затем база | `unknow` | dtmod.cpp:667 |
| `APIScanerCOMBoundRate` | целое | база, затем файл | `9600` | fMenu.cpp:2681 |
| `APIScanerCOMByteSize` | целое | база, затем файл | `8` | fMenu.cpp:2684 |
| `APIScanerCOMParity` | строка | база, затем файл | `None` | fMenu.cpp:2695 |
| `APIScanerCOMStopBits` | строка | база, затем файл | `1` | fMenu.cpp:2687 |
| `ArchiveLog` | булево | файл, затем база | `true` | dtmod.cpp:747 |
| `AskPrintInvoice` | булево | база, затем файл | `true` | Uhvbb.cpp:358 |
| `AutoCancelCheckInDBSS` | булево | база, затем файл | `true` | Uhvbb.cpp:987 |
| `AutoCompletePayment` | булево | база, затем файл | `false` | order.cpp:543 |
| `AutoDisableEmptyCardPayment` | булево | база, затем файл | `false` | Uclose_bon.cpp:120 |
| `AutoSetPayTerm` | булево | база, затем файл | `true` | Uclose_bon.cpp:378 |
| `AutoUnionOnPrintError` | булево | база, затем файл | `true` | Uhvbb.cpp:966 |
| `BackupLogDir` | строка | файл, затем база | `Log` | dtmod.cpp:751 |
| `BackupLogPeriod` | целое | файл, затем база | `365` | dtmod.cpp:765 |
| `BarcodeAddon` | булево | база, затем файл | `false` | Uhvbb.cpp:1342, dtmod.cpp:2084 |
| `BarCodeAridon` | булево | только база | `false` | Uhvbb.cpp:197, dtmod.cpp:2301 |
| `BarCodeAridonUseBarcodeInt` | булево | только база | `false` | dtmod.cpp:2303 |
| `BCQRCODVaucerAutoDetect` | булево | база, затем файл | `true` | dtmod.cpp:6993 |
| `BeforeDiscountLineText` | строка | база, затем файл | `>>  :qnt x :price <exp>…` | Daisy.cpp:450, ElicomFP.cpp:499, и ещё 4 |
| `BegAutoPrint` | строка | только база |  | Ubeg.cpp:94 |
| `BegRePrintEnabled` | булево | база, затем файл | `true` | Ubeg.cpp:28, order.cpp:2368 |
| `BemolReaderCom` | строка | база, затем файл | `COM3` | Payments.cpp:1109 |
| `BemolReaderTries` | целое | база, затем файл | `3` | Payments.cpp:1102 |
| `BlockCardSMKMultiPay` | булево | файл, затем база | `true` | dtmod.cpp:11583 |
| `BlockZeroWeightBarcodes` | булево | база, затем файл | `false` | dtmod.cpp:2444 |
| `BulkReprintEnabled` | булево | база, затем файл | `false` | fMenu.cpp:1428 |
| `BusyWaitTimeoutPOSTerm` | целое | файл, затем база | `0` | CustomFiscalPrintDevice.cpp:159 |
| `CalcBPAY` | булево | база, затем файл | `false` | dtmod.cpp:7544 |
| `CalcGift` | булево | база, затем файл | `false` | dtmod.cpp:7543 |
| `CalcONLine` | булево | база, затем файл | `false` | dtmod.cpp:7545 |
| `CancelButtonTextSize` | целое | база, затем файл | `dxTBMainCancel->Text1->…` | uSelfService.cpp:954 |
| `CancelCheckInPrinter` | булево | база, затем файл | `true` | Uhvbb.cpp:922 |
| `CanelButtonSelectPage` | булево | база, затем файл | `false` | uSelfService.cpp:913 |
| `cantButtonsWidth` | целое | файл, затем база | `0` | uSelfService.cpp:820 |
| `CantDecreaseByAdminPin` | строка | база, затем файл | `FALSE` | order.cpp:575 |
| `cantLabelFontSize` | целое | файл, затем база | `productCantLabel->Font-…` | uSelfService.cpp:827 |
| `CardColorButtons` | строка | база, затем файл | `ReadStrParam(rpmDBFirst…` | TS.cpp:257 |
| `CardInfoWidth` | целое | база, затем файл | `pnCardInfo->Width` | Uhvbb.cpp:1947 |
| `CardReaderEnabled` | булево | база, затем файл | `false` | fMenu.cpp:796 |
| `CardsOnlineProcessing` | булево | файл, затем база | `false` | dtmod.cpp:11109 |
| `CashierFullCheckHistory` | булево | база, затем файл | `false` | dtmod.cpp:7048 |
| `CashOutEnabled` | булево | база, затем файл | `false` | CashInOut.cpp:40 |
| `CekVisible` | булево | база, затем файл | `ReadIniBoolean("CekVisi…` | Uhvbb.cpp:209 |
| `CertificatesAppendOnShow` | булево | база, затем файл | `false` | Certificates.cpp:69 |
| `ChangePrice` | булево | только база | `false` | dtmod.cpp:9169, fMenu.cpp:1376 |
| `check_kol_decrease` | булево | только база | `false` | dtmod.cpp:4718 |
| `check_paym_cards_print_mode` | булево | база, затем файл | `false` | Uhvbb.cpp:1063 |
| `CheckBarcode` | булево | база, затем файл | `true` | Uhvbb.cpp:1368 |
| `CheckBlock` | булево | база, затем файл | `false` | dtmod.cpp:513 |
| `CheckDailySum` | булево | база, затем файл | `false` | dtmod.cpp:6406 |
| `CheckDateTimeMaxSeconds` | целое | файл, затем база | `120` | dtmod.cpp:12688 |
| `CheckDocTypeOnSave` | булево | база, затем файл | `false` | fMenu.cpp:491 |
| `CheckNlsLang` | булево | только файл | `false` | ucLogin.cpp:733 |
| `CheckPosDocsIsPrinted` | булево | база, затем файл | `false` | Uhvbb.cpp:2861 |
| `CheckPrintPayType` | булево | файл, затем база | `false` | ElicomFP.cpp:578, SocketFP.cpp:405, и ещё 1 |
| `CheckRefNumberRT` | булево | база, затем файл | `false` | order.cpp:2543 |
| `CheckSelfPinRequire` | булево | база, затем файл | `false` | dtmod.cpp:14652 |
| `CheckTestMode` | булево | база, затем файл | `false` | Uhvbb.cpp:592 |
| `CheckTvrCount` | булево | база, затем файл | `false` | dtmod.cpp:556 |
| `CheckZeroPosition` | булево | база, затем файл | `false` | TSPOSTermIP.cpp:80, Uhvbb.cpp:712, и ещё 1 |
| `CircusEnabled` | булево | база, затем файл | `false` | Uhvbb.cpp:812 |
| `ClearPayOnAutoSetPayTerm` | булево | файл, затем база | `false` | dtmod.cpp:516 |
| `CloseBonIfEmpty` | булево | база, затем файл | `false` | dtmod.cpp:9774 |
| `CloseByX550` | булево | только база | `false` | dtmod.cpp:6433 |
| `CloseByZ` | булево | база, затем файл | `true` | dtmod.cpp:6433 |
| `CMD_circ` | строка | база, затем файл | `mstsc /v:<ip>…` | Payments.cpp:1034 |
| `cod_ecotaxa` | целое | база, затем файл | `-1` | ElicomFP.cpp:403, SocketFP.cpp:329, и ещё 2 |
| `ComenzdAuxArdFields` | булево | база, затем файл | `false` | dtmod.cpp:3932 |
| `ComenzNFPrint` | булево | файл, затем база | `false` | dtmod.cpp:1748 |
| `CommitOnIsertTovar` | булево | база, затем файл | `true` | dtmod.cpp:2543 |
| `ConsultEnabled` | булево | только база | `false` | fMenu.cpp:1323 |
| `ConsultRequired` | булево | база, затем файл | `false` | Uhvbb.cpp:1051 |
| `costumButtomHeight` | целое | база, затем файл | `bottomPanel->Height` | TS.cpp:619, uSelfService.cpp:2861 |
| `CostumCantButtons` | булево | база, затем файл | `false` | uSelfService.cpp:356 |
| `costumLangButton` | булево | база, затем файл | `false` | uSelLang.cpp:54, uSelfService.cpp:2773 |
| `costumPanelButtonHeight` | целое | база, затем файл | `60` | uImgMenu.cpp:84, uSelfService.cpp:2824 |
| `costumPanelButtonWidth` | целое | база, затем файл | `100` | uImgMenu.cpp:83, uSelfService.cpp:2823 |
| `costumPanelHeight` | целое | база, затем файл | `dxTileBar1->Parent->Hei…` | uImgMenu.cpp:85, uSelfService.cpp:2962 |
| `CostumProductButtons` | булево | база, затем файл | `false` | TS.cpp:124 |
| `costumSearch` | булево | файл, затем база | `false` | dtmod.cpp:2302 |
| `costumShoppingCard` | булево | база, затем файл | `false` | uSelfService.cpp:2795 |
| `costumSizeMenuButtons` | булево | файл, затем база | `false` | uSelfService.cpp:755 |
| `costumToolsPanel` | булево | база, затем файл | `false` | uImgMenu.cpp:77, uSelfService.cpp:2065 |
| `CustDispIdleMsg` | строка | база, затем файл | `    UNISIM-SOFT` | CustomCustomerDisplay.cpp:74, uAddDisplay.cpp:44, и ещё 1 |
| `CustDisplayClearTotalInterval` | целое | файл, затем база | `0` | dtmod.cpp:3285 |
| `CustDisplayCOMBaudRate` | целое | файл, затем база | `9600` | dtmod.cpp:10704 |
| `CustDisplayDriverLog` | булево | файл, затем база | `true` | dtmod.cpp:10699 |
| `CustDisplayLng` | строка | база, затем файл | `RO` | dtmod.cpp:249 |
| `CustomBarcodesMode` | строка | только база |  | uszlen.cpp:22 |
| `DaisyFPTextLen` | целое | файл, затем база | `ReadIntParam(rpmIniFirs…` | Daisy.cpp:10 |
| `DATECSFP550TextLen` | целое | файл, затем база | `ReadIntParam(rpmIniFirs…` | dtmod.cpp:7422 |
| `DatecsFPBPAYLetter` | строка | только файл | `N` | dtmod.cpp:7448 |
| `DatecsFPCardLetter` | строка | только файл | `N` | SocketFP.cpp:384, dtmod.cpp:7449 |
| `DatecsFPCashLetter` | строка | база, затем файл | `P` | dtmod.cpp:7987 |
| `DatecsFPCertLetter` | строка | только файл | `C` | SocketFP.cpp:385, dtmod.cpp:7450 |
| `DatecsFPGiftLetter` | строка | только файл | `X` | SocketFP.cpp:386, dtmod.cpp:7451 |
| `DatecsFPOnlineLetter` | строка | только файл | `O` | dtmod.cpp:7452 |
| `DatecsFPPaymentCredit` | булево | файл, затем база | `false` | Uclose_bon.cpp:671, Uhvbb.cpp:1233, и ещё 2 |
| `DatecsFPPaymentCreditType` | целое | база, затем файл | `8` | SocketFP.cpp:470, dtmod.cpp:6230 |
| `DatecsFPTMHLetter` | строка | только файл | `H` | SocketFP.cpp:382, dtmod.cpp:7446 |
| `DatecsFPValutaLetter` | строка | только файл | `V` | dtmod.cpp:7453 |
| `DatecsPrintBarcode` | булево | база, затем файл | `false` | dtmod.cpp:6324 |
| `DatecsPrintBarcodeText` | булево | база, затем файл | `false` | dtmod.cpp:6339 |
| `DatecsPrintExitOnCtrl` | булево | файл, затем база | `false` | dtmod.cpp:4441 |
| `DatecsTypeModel` | целое | только файл | `0` | dtmod.cpp:7437 |
| `DatecsUseDiscount` | булево | база, затем файл | `false` | dtmod.cpp:4416 |
| `DeferredDocEnabled` | булево | база, затем файл | `false` | Uhvbb.cpp:2853 |
| `DeletePositionByAdminPin` | строка | база, затем файл | `FALSE` | order.cpp:2177 |
| `DeleteWholeWeightPosition` | булево | только файл | `false` | order.cpp:640 |
| `DiagFP550Visible` | булево | только база | `true` | fMenu.cpp:1353 |
| `DisableBeepScalesGoodWeight` | булево | файл, затем база | `false` | Scales.cpp:171, ScalesI.cpp:171 |
| `disableBorderLines` | булево | база, затем файл | `false` | TS.cpp:639, uSelfService.cpp:2777 |
| `DisableCantEdit` | булево | только база | `false` | Uhvbb.cpp:197 |
| `DisableCheckDatecsPLines` | булево | файл, затем база | `false` | dtmod.cpp:508 |
| `DisableDetailCommentsEdit` | булево | база, затем файл | `false` | Uhvbb.cpp:2420 |
| `DisableReturnFP` | булево | база, затем файл | `false` | Uhvbb.cpp:725 |
| `DisableSecondPinOnLog` | булево | только файл | `false` | dtmod.cpp:862 |
| `DiscontAdvanced` | булево | только база | `false` | dtmod.cpp:495 |
| `DiscountLineText` | строка | база, затем файл | `>>  reducere  - <exp> :…` | Daisy.cpp:488, ElicomFP.cpp:509, и ещё 4 |
| `EdCantLockFocus` | булево | база, затем файл | `false` | dtmod.cpp:538 |
| `EdPodarocAlwaysVisible` | булево | база, затем файл | `false` | Uhvbb.cpp:1950, dtmod.cpp:4953 |
| `ElicomBPAYCode` | целое | база, затем файл | `4` | ElicomFP.cpp:47 |
| `ElicomBPAYType` | целое | файл, затем база | `7` | ElicomFP.cpp:615 |
| `ElicomCecCode` | целое | база, затем файл | `2` | ElicomFP.cpp:43 |
| `ElicomCreditCode` | целое | база, затем файл | `3` | ElicomFP.cpp:42 |
| `ElicomCreditType` | целое | файл, затем база | `8` | ElicomFP.cpp:633 |
| `ElicomFpBonText` | строка | база, затем файл | `Bon ` | ElicomFP.cpp:806, SocketFP.cpp:669, и ещё 1 |
| `ElicomFPDeleteFPObject` | булево | файл, затем база | `false` | ElicomFP.cpp:30 |
| `ElicomFPDep` | целое | файл, затем база | `0` | ElicomFP.cpp:471, SocketFP.cpp:209, и ещё 1 |
| `ElicomFPPrintTextInCheckReplace` | булево | база, затем файл | `true` | ElicomFP.cpp:1315 |
| `ElicomFPSellDepartment` | булево | файл, затем база | `false` | ElicomFP.cpp:469, SocketFP.cpp:207, и ещё 1 |
| `ElicomFPTextLen` | целое | файл, затем база | `ReadIntParam(rpmIniFirs…` | ElicomFP.cpp:19 |
| `ElicomGiftCode` | целое | база, затем файл | `6` | ElicomFP.cpp:46 |
| `ElicomGiftType` | целое | файл, затем база | `6` | ElicomFP.cpp:609, SocketFP.cpp:440 |
| `ElicomONLineCode` | целое | база, затем файл | `4` | ElicomFP.cpp:48 |
| `ElicomONlineType` | целое | файл, затем база | `8` | ElicomFP.cpp:621 |
| `ElicomPass` | строка | база, затем файл | `0000` | ElicomFP.cpp:14 |
| `ElicomPrintBarcode` | булево | база, затем файл | `false` | ElicomFP.cpp:367, VirtualFP.cpp:407 |
| `ElicomTMEType` | целое | файл, затем база | `4` | ElicomFP.cpp:597, SocketFP.cpp:426 |
| `ElicomTMHType` | целое | файл, затем база | `5` | ElicomFP.cpp:603, SocketFP.cpp:433 |
| `EmulateE260ErrorOnDiscount` | булево | файл, затем база | `false` | IKCE260T.cpp:446 |
| `EnableMenuPreview` | булево | база, затем файл | `false` | dtmod.cpp:506 |
| `EnderRedus` | булево | только база | `false` | dtmod.cpp:9479, fMenu.cpp:1373 |
| `ErrFontSize` | целое | база, затем файл | `12` | dtmod.cpp:5564, uErrDialog.cpp:140 |
| `ErrorDialogAutoCloseSec` | целое | база, затем файл | `10` | uAutoCloseDlg.cpp:30 |
| `FastEmpBarcodeAuth` | булево | база, затем файл | `false` | ucLogin.cpp:838 |
| `FieldForPret` | строка | только база | `pretv4` | dtmod.cpp:3452 |
| `FixChecksExtended` | булево | база, затем файл | `false` | FixChecks.cpp:25 |
| `FNEditMode` | целое | база, затем файл | `0` | FiscalNote.cpp:358 |
| `FNMode` | булево | база, затем файл | `false` | dtmod.cpp:10159 |
| `FNPersPhysCode` | целое | база, затем файл | `0` | CashOutOrder.cpp:118, FiscalNote.cpp:417 |
| `FNRequiredOnReturn` | булево | база, затем файл | `false` | Uhvbb.cpp:321 |
| `FNRGDocTypeENCaption` | строка | файл, затем база | `FN\nTN` | FiscalNote.cpp:339 |
| `FNRGDocTypeROCaption` | строка | файл, затем база | `FF\nF` | FiscalNote.cpp:341 |
| `FNRGDocTypeRUCaption` | строка | файл, затем база | `НН\nТТН` | FiscalNote.cpp:343 |
| `FNSNAutoComplete` | булево | база, затем файл | `false` | FiscalNote.cpp:392 |
| `ForceOpenBox` | булево | база, затем файл | `false` | dtmod.cpp:14681 |
| `ForcePrintNonFiscal` | булево | файл, затем база | `false` | dtmod.cpp:1588 |
| `ForceSyncFPDateTime` | булево | файл, затем база | `false` | dtmod.cpp:11288 |
| `FormCBAlignLeft` | булево | база, затем файл | `false` | Uclose_bon.cpp:472 |
| `FormCBAlignRight` | булево | база, затем файл | `false` | Uclose_bon.cpp:473 |
| `FP550QRCodeSizeCmd` | целое | файл, затем база | `5` | dtmod.cpp:8584 |
| `FPCyrillicTVALetters` | булево | файл, затем база | `false` | dtmod.cpp:7765 |
| `FPNFTextLen` | целое | файл, затем база | `30` | dtmod.cpp:12001 |
| `FromContEnabled` | булево | только файл | `false` | order.cpp:248 |
| `FSCustomCheckBonusText` | строка | база, затем файл |  | CustomFiscalPrintDevice.cpp:287, dtmod.cpp:6197 |
| `FSCustomDiscText` | строка | база, затем файл |  | Daisy.cpp:539, ElicomFP.cpp:755, и ещё 4 |
| `FSCustomNameText` | строка | база, затем файл |  | CustomFiscalPrintDevice.cpp:278, dtmod.cpp:6189 |
| `FSDiscPercentText` | строка | база, затем файл | `Reducere la card %s%` | CustomFiscalPrintDevice.cpp:274, dtmod.cpp:6188 |
| `FSEnabled` | булево | только база | `false` | fMenu.cpp:1401 |
| `fSeveralHeight` | целое | файл, затем база | `469` | uSeveralTovar.cpp:29 |
| `fSeveralWidth` | целое | файл, затем база | `749` | uSeveralTovar.cpp:28 |
| `FSPointsText` | строка | база, затем файл | `Nr. de puncte %s` | CustomFiscalPrintDevice.cpp:273, dtmod.cpp:6187 |
| `FSPrintBarcode` | булево | база, затем файл | `ReadStrParam(rpmDBFirst…` | CustomFiscalPrintDevice.cpp:280 |
| `FSPrintCostumerBarcod` | булево | база, затем файл | `true` | CustomFiscalPrintDevice.cpp:282, dtmod.cpp:6192 |
| `GetBonCommentary` | булево | файл, затем база | `true` | dtmod.cpp:1727 |
| `GetPOSReceiptCopyFromBD` | булево | файл, затем база | `false` | dtmod.cpp:11867 |
| `global_dep` | строка | база, затем файл | `null` | uLoyaltyUI.cpp:1179 |
| `GlobalColorButtons` | строка | база, затем файл | `RGB(90, 159, 37)` | TS.cpp:257, uImgMenu.cpp:79, и ещё 2 |
| `GlobalFont` | строка | файл, затем база | `none` | TS.cpp:414, uSelfService.cpp:773 |
| `headerTextBottom` | целое | база, затем файл | `0` | uSelfService.cpp:2611 |
| `headerTextTop` | целое | база, затем файл | `0` | uSelfService.cpp:2598 |
| `heightMenuButtons` | целое | файл, затем база | `200` | uSelfService.cpp:759 |
| `HideAfterPay` | булево | только база | `false` | Uhvbb.cpp:432 |
| `IgnoreCDDError` | булево | база, затем файл | `false` | CustomCustomerDisplay.cpp:43 |
| `IKC_E260T_RTITextLen` | целое | файл, затем база | `ReadIntParam(rpmIniFirs…` | IKCE260T.cpp:682 |
| `IKC_E260TTextLen` | целое | файл, затем база | `ReadIntParam(rpmIniFirs…` | IKCE260T.cpp:66 |
| `ImgScaleFactor` | целое | база, затем файл | `100` | uImgMenu.cpp:42 |
| `infoPageNextSection` | подпись на трёх языках | файл, затем база | `Pentru a vizualiza alte…` | TS.cpp:1832 |
| `infoPageNextSectionFontColor` | строка | база, затем файл | `RGB(90, 159, 37)` | TS.cpp:1835 |
| `infoPageNextSectionFontSize` | целое | файл, затем база | `pnTSNav->Font->Size` | TS.cpp:1834 |
| `IngenicoCancelOp` | целое | файл, затем база | `4` | UnPOSTermIngen.cpp:175 |
| `IngenicoPayOp` | целое | файл, затем база | `1` | UnPOSTermIngen.cpp:172 |
| `IngenicoReportCopyOp` | целое | файл, затем база | `13` | UnPOSTermIngen.cpp:187 |
| `IngenicoSleepTimeout` | целое | файл, затем база | `3000` | UnPOSTermIngen.cpp:242 |
| `IngenicoXRepOp` | целое | файл, затем база | `6` | UnPOSTermIngen.cpp:183 |
| `IngenicoZRepOp` | целое | файл, затем база | `7` | UnPOSTermIngen.cpp:184 |
| `InventrDocType` | целое | файл, затем база | `2` | dtmod.cpp:3315 |
| `IPCServerID` | строка | файл, затем база |  | dtmod.cpp:9892 |
| `IQOSEnabled` | булево | база, затем файл | `false` | dtmod.cpp:10594 |
| `IQOSwarrantyGetLink` | строка | база, затем файл | `https://iqos.linella.md…` | dtmod.cpp:14747 |
| `IQOSwarrantyNavLink` | строка | база, затем файл | `https://iqos.linella.md` | dtmod.cpp:14744 |
| `IQOSwarrantyNeedNavigate` | булево | база, затем файл | `true` | dtmod.cpp:14743 |
| `KillMySessions` | булево | файл, затем база | `false` | fMenu.cpp:1446 |
| `KvintCredAccPrint` | булево | файл, затем база | `true` | dtmod.cpp:6246 |
| `KvintMode` | булево | база, затем файл | `false` | dtmod.cpp:519, fMenu.cpp:1299, и ещё 1 |
| `KvintModeDatecsRegisterAsOnePosition` | булево | файл, затем база | `true` | dtmod.cpp:6064 |
| `KvintModeNoPrintPosReport` | булево | файл, затем база | `true` | dtmod.cpp:11930 |
| `KvintModePOSTermModeType` | целое | база, затем файл | `1` | Uclose_bon.cpp:531 |
| `KvintModePOSTermWithoutUI` | булево | база, затем файл | `true` | Uclose_bon.cpp:529 |
| `KvintModePreviewFirstLocate` | булево | файл, затем база | `true` | dtmod.cpp:7163 |
| `KvintPayCredit` | булево | файл, затем база | `true` | Uclose_bon.cpp:413, fMenu.cpp:1388 |
| `KvintPayMobile` | булево | файл, затем база | `true` | fMenu.cpp:1391 |
| `KvintShowValuta` | булево | файл, затем база | `true` | casa.cpp:97, fMenu.cpp:1394 |
| `KvintTerminal` | булево | файл, затем база | `true` | fMenu.cpp:1299 |
| `LangButtonTextSize` | целое | база, затем файл | `dxTBLang->Text1->Font->…` | uSelfService.cpp:3026 |
| `LangMsgProcessing` | булево | база, затем файл | `false` | dtmod.cpp:12244 |
| `LedgerEarnRate` | строка | база, затем файл | `4` | uLoyaltyLedger.cpp:35 |
| `LedgerHoldSec` | целое | база, затем файл | `900` | uLoyaltyLedger.cpp:42 |
| `LedgerPackage` | строка | база, затем файл | `csDefaultPackage` | uLoyaltyLedger.cpp:22 |
| `leftTotal` | целое | база, затем файл | `Label1->Left` | uSelfService.cpp:2802 |
| `leftTotalValue` | целое | база, затем файл | `Label1->Left` | uSelfService.cpp:2803 |
| `LineFeedNonFiscal` | целое | файл, затем база | `5` | CustomFiscalPrintDevice.cpp:167 |
| `LogDir` | строка | файл, затем база | `Log` | dtmod.cpp:750 |
| `Login` | строка | только файл |  | ucLogin.cpp:325 |
| `LogInOut` | булево | база, затем файл | `false` | fMenu.cpp:1741 |
| `LogoPath` | строка | только файл | `asPath` | ucLogin.cpp:296 |
| `LogUWMC` | булево | база, затем файл | `false` | fMenu.cpp:822 |
| `LogWinMsg` | булево | база, затем файл | `false` | fMenu.cpp:515 |
| `LotoReportNoOfCopiesCut` | целое | файл, затем база | `1` | dtmod.cpp:12066 |
| `LowerFreeCheckText` | строка | база, затем файл |  | Daisy.cpp:557, ElicomFP.cpp:795, и ещё 3 |
| `LowerFSeparatorText` | строка | база, затем файл |  | Daisy.cpp:561, ElicomFP.cpp:799, и ещё 3 |
| `LoyaltyBackend` | строка | база, затем файл | `bridge` | uLoyaltyLedger.cpp:29 |
| `LoyaltyDBPackage` | строка | файл, затем база | `pkg_loyalty_util` | UnPOSTermSocket.cpp:24, dtmod.cpp:14534 |
| `LoyaltyServerName` | строка | файл, затем база | `LoyaltyBridge.bat` | dtmod.cpp:682 |
| `LoyaltySocketHost` | строка | файл, затем база | `127.0.0.1` | dtmod.cpp:680 |
| `LoyaltySocketPort` | строка | файл, затем база | `8883` | dtmod.cpp:681 |
| `LoyaltySocketServiceEnabled` | булево | только файл | `false` | dtmod.cpp:677, fMenu.cpp:1296 |
| `MainMenuCount` | целое | файл, затем база | `5` | uSelfService.cpp:912 |
| `MainMenuCountColumns` | целое | файл, затем база | `5` | uSelfService.cpp:752 |
| `MainMenuCountRows` | целое | файл, затем база | `2` | uSelfService.cpp:753 |
| `ManualReturn` | булево | файл, затем база | `FPrinter->ManualReturnS…` | dtmod.cpp:9867 |
| `ManualSearchDenum` | булево | только база | `false` | Uhvbb.cpp:1875, order.cpp:2720 |
| `maxCardWordsProductName` | целое | файл, затем база | `30` | TS.cpp:368 |
| `MaxDocItems` | целое | файл, затем база | `FPrinter->MaxDocItems` | dtmod.cpp:12227 |
| `MaxItemQnt` | целое | база, затем файл | `1000` | dtmod.cpp:4705 |
| `MenuSortOrder` | строка | только база |  | order.cpp:108 |
| `MIACallbackUrl` | строка | файл, затем база |  | uMIARest.cpp:207 |
| `MIATimeOut` | целое | база, затем файл | `60` | uMIAPayments.cpp:36 |
| `MIATimeoutMs` | целое | база, затем файл | `15000` | uMIARest.cpp:66 |
| `mItemPayCart` | булево | база, затем файл | `true` | fMenu.cpp:78 |
| `mItemPrint` | булево | база, затем файл | `true` | fMenu.cpp:77 |
| `ModalOrdList` | булево | база, затем файл | `false` | order.cpp:2187 |
| `MoldcellMinAmount` | целое | файл, затем база | `5` | Payments.cpp:768 |
| `MsgOnChangeQntPortion` | булево | база, затем файл | `false` | uCnt.cpp:56 |
| `MsgOnOpenReports` | булево | база, затем файл | `true` | fMenu.cpp:160 |
| `MultiCurrencyPrices` | булево | база, затем файл | `false` | dtmod.cpp:523, ucLogin.cpp:511 |
| `MultiPayment` | булево | файл, затем база | `false` | UnPOSTermIngen.cpp:173, Uhvbb.cpp:1272, и ещё 2 |
| `MultiPaymentOpenBox` | булево | файл, затем база | `false` | fMenu.cpp:385 |
| `multipaymentRestrictedPayIDList` | строка | база, затем файл |  | MultiPayments.cpp:255 |
| `multipaymentRestrictedRemovePayIDList` | строка | база, затем файл |  | MultiPayments.cpp:328 |
| `multipaymentTextColor` | строка | база, затем файл | `RGB(255, 255, 255)` | MultiPayments.cpp:41, MultiPaymentsPay.cpp:69 |
| `MutexName` | строка | файл, затем база | `UAMENU_MUTEX` | UAMenu.cpp:93 |
| `NFPCustomText` | строка | база, затем файл | `Copia bon. ` | ElicomFP.cpp:805, SocketFP.cpp:668, и ещё 1 |
| `NFPSupported` | булево | файл, затем база | `true` | Uhvbb.cpp:652 |
| `NoCheckLocale` | булево | только файл | `false` | ucLogin.cpp:238 |
| `NoPrintHotelChecks` | булево | база, затем файл | `false` | order.cpp:975 |
| `OrangeMinAmount` | целое | файл, затем база | `10` | Payments.cpp:769 |
| `OrderedSearch` | булево | только база | `true` | dtmod.cpp:3571 |
| `OrderNrAutoComplete` | булево | база, затем файл | `false` | CashOutOrder.cpp:177 |
| `pageContolButtonsFontSize` | целое | файл, затем база | `btNext->Text1->Font->Si…` | TS.cpp:1777 |
| `PagePanelHeight` | целое | файл, затем база | `pnAddrBar->Height` | TS.cpp:596 |
| `PageTextFontSize` | целое | файл, затем база | `lbPath->Font->Size` | TS.cpp:595 |
| `Password` | строка | только файл |  | ucLogin.cpp:326 |
| `PauseAfterItog` | целое | только база | `1500` | dtmod.cpp:7897, uMIAPayments.cpp:195 |
| `PauseAfterOpen` | целое | только база | `1000` | dtmod.cpp:7736 |
| `PauseAfterZX` | целое | только база | `1000` | dtmod.cpp:7682 |
| `PaymentsDigitKeyCheck` | булево | база, затем файл | `true` | Payments.cpp:992 |
| `PersJurIsNonFiscal` | целое | файл, затем база | `1` | Uhvbb.cpp:1061 |
| `POSSendTMECurrency` | булево | база, затем файл | `false` | TSPOSTermIP.cpp:118, dtmod.cpp:13723 |
| `PosTermBPAYDisplayCOM` | строка | только файл | `1` | dtmod.cpp:716 |
| `PosTermBPAYDisplayCOMbaudrate` | целое | только файл | `9600` | dtmod.cpp:717 |
| `PosTermBPAYMERCHANTID` | строка | файл, затем база | `retailtest` | UnPOSTermBPAY.cpp:48 |
| `POSTermBPAYServiceEnabled` | булево | только файл | `false` | dtmod.cpp:714 |
| `POSTermCount` | целое | файл, затем база | `1` | dtmod.cpp:632 |
| `PosTermDellCommentIngenico` | булево | файл, затем база | `false` | CustomFiscalPrintDevice.cpp:171, dtmod.cpp:1531 |
| `PosTermForceCancelOnBonCancel` | булево | только файл | `false` | Uhvbb.cpp:1618 |
| `POSTermLog` | булево | файл, затем база | `true` | dtmod.cpp:672 |
| `POSTermReceiptNoOfCopiesCut` | целое | файл, затем база | `1` | dtmod.cpp:11884 |
| `POSTermReportNoOfCopiesCut` | целое | файл, затем база | `1` | dtmod.cpp:11936 |
| `POSTermSocketCheckOnStart` | булево | файл, затем база | `false` | UnPOSTermSocket.cpp:27 |
| `POSTermSocketDemoMode` | булево | файл, затем база | `false` | UnPOSTermSocket.cpp:16 |
| `POSTermSocketServerName` | строка | файл, затем база | `Server_POSTerminal2.exe` | UnPOSTermSocket.cpp:21 |
| `POSTermSocketServerPath` | строка | файл, затем база | `IncludeTrailingBackslas…` | UnPOSTermSocket.cpp:26 |
| `POSTermSocketServiceEnabled` | булево | только файл | `false` | dtmod.cpp:686 |
| `POSTermSocketUpTimeOut` | целое | файл, затем база | `10` | UnPOSTermSocket.cpp:227 |
| `POSTermSocketValutaCod` | целое | база, затем файл | `498` | UnPOSTermSocket.cpp:276 |
| `POSTMECurrencyName` | строка | файл, затем база | `Tichet De Masa` | TSPOSTermIP.cpp:119, dtmod.cpp:13724 |
| `PrefixSpecialCaseWParam` | целое | база, затем файл | `66` | fMenu.cpp:555 |
| `PriceFontSize` | целое | файл, затем база | `20` | TS.cpp:480 |
| `PriceMarginBottom` | целое | файл, затем база | `20` | TS.cpp:484 |
| `PriceMarginRight` | целое | файл, затем база | `20` | TS.cpp:483 |
| `PriceMarkFontSize` | целое | файл, затем база | `10` | TS.cpp:479 |
| `PrintCheckLineByLine` | булево | файл, затем база | `false` | dtmod.cpp:9868 |
| `PrintCurrencyReportAfterX` | булево | база, затем файл | `false` | fMenu.cpp:1852 |
| `PrintCurrencyReportAfterZ` | булево | база, затем файл | `false` | fMenu.cpp:1868 |
| `PrintDefectPin` | булево | файл, затем база | `false` | dtmod.cpp:257 |
| `PrintDetailComments` | булево | файл, затем база | `true` | dtmod.cpp:504 |
| `PrintLotoReportAfterX` | булево | база, затем файл | `false` | fMenu.cpp:1850 |
| `PrintTMReportAfterX` | булево | база, затем файл | `false` | fMenu.cpp:1848 |
| `PrivetEd2500` | строка | база, затем файл | `ReadStrParam(rpmDBFirst…` | CustomCustomerDisplay.cpp:74, uAddDisplay.cpp:44 |
| `productMarkPriceSize` | целое | файл, затем база | `Label3->Font->Size` | uSelfService.cpp:775 |
| `ProductNameBold` | булево | файл, затем база | `false` | TS.cpp:420 |
| `ProductNameFontSize` | целое | файл, затем база | `DG->Canvas->Font->Size` | TS.cpp:418 |
| `productPriceMarkText` | подпись на трёх языках | файл, затем база | `Pret:\|Цена:\|Price:` | uSelfService.cpp:974 |
| `productPriceSize` | целое | файл, затем база | `Label3->Font->Size` | uSelfService.cpp:799 |
| `qPayTotalQuery` | строка | база, затем файл | `QPayTotals->SQL->Text` | MultiPayments.cpp:33 |
| `QueryDailySum` | булево | база, затем файл | `false` | dtmod.cpp:6400 |
| `QueryTableNumber` | булево | база, затем файл | `false` | order.cpp:2563 |
| `RestCheckFPC` | булево | база, затем файл | `false` | order.cpp:889 |
| `RestCloseEnabled` | булево | только база | `true` | dtmod.cpp:5257, order.cpp:323 |
| `RestCNFEnabled` | булево | только база | `false` | order.cpp:985 |
| `RestInvisibleState` | целое | база, затем файл | `100` | dtmod.cpp:1281 |
| `RestPrintEnabled` | булево | только база | `true` | order.cpp:322 |
| `RestPrintNonFiscal` | булево | только база | `false` | order.cpp:2462 |
| `RetailSolutionText` | строка | база, затем файл | `una.md/Oracle-POS` | Daisy.cpp:568, ElicomFP.cpp:818, и ещё 4 |
| `ReturnButtonTextSize` | целое | база, затем файл | `dxTileBar1dxTileBarItem…` | uImgMenu.cpp:341, uSelfService.cpp:1012 |
| `RTITMECode` | целое | база, затем файл | `5` | IKCE260T.cpp:17 |
| `RTITMHCode` | целое | база, затем файл | `4` | IKCE260T.cpp:16 |
| `Scales` | строка | файл, затем база |  | dtmod.cpp:725 |
| `ScalesCOM` | целое | файл, затем база | `1` | dtmod.cpp:9886 |
| `ScalesCOMBaudRate` | целое | файл, затем база | `9600` | dtmod.cpp:9887 |
| `ScalesDriverLog` | булево | файл, затем база | `true` | dtmod.cpp:9889 |
| `ScalesEnabled` | булево | файл, затем база | `false` | dtmod.cpp:723, fMenu.cpp:1423 |
| `ScalesManualEdit` | булево | файл, затем база | `false` | Scales.cpp:286, ScalesI.cpp:397 |
| `ScalesServerPath` | строка | файл, затем база |  | dtmod.cpp:9893 |
| `ScanBaudRate` | целое | файл, затем база | `38400` | dtmod.cpp:2045 |
| `ScanCOM` | целое | файл, затем база | `1` | dtmod.cpp:2044 |
| `ScanerVisibleChars` | целое | база, затем файл | `4` | Uhvbb.cpp:1940 |
| `Scanner` | строка | файл, затем база | `MS6720` | dtmod.cpp:776 |
| `ScardReaderSleepInterval` | целое | файл, затем база | `100` | CardReader.cpp:57, SCardReader.cpp:30 |
| `SearchByArticolEnabled` | булево | только база | `true` | dtmod.cpp:499 |
| `SearchByClientNameEnabled` | булево | база, затем файл | `false` | partDenum.cpp:35 |
| `SearchByCodeEnabled` | булево | только база | `true` | dtmod.cpp:500 |
| `SearchByNameEnabled` | булево | только база | `true` | dtmod.cpp:498 |
| `SearchByPersCodeEnabled` | булево | база, затем файл | `false` | partDenum.cpp:36 |
| `SearchByPriceEnabled` | булево | только база | `true` | dtmod.cpp:497 |
| `SearchByPriceKey` | строка | база, затем файл | `)` | Uhvbb.cpp:1839 |
| `SearchByShortCodeEnabled` | булево | только база | `true` | dtmod.cpp:501 |
| `SearchByShortCodeExEnabled` | булево | только база | `true` | dtmod.cpp:502 |
| `SelectClientEnabled` | булево | база, затем файл | `false` | fMenu.cpp:1425 |
| `SendTextMsgCount` | целое | база, затем файл | `2` | CustomCustomerDisplay.cpp:18 |
| `SendTextTimerEnabled` | булево | база, затем файл | `true` | CustomCustomerDisplay.cpp:16 |
| `SendTextTimerInterval` | целое | база, затем файл | `500` | CustomCustomerDisplay.cpp:17 |
| `ServerID` | строка | только база | `0` | dtmod.cpp:6286 |
| `SeveralTovarByPIN` | булево | база, затем файл | `false` | uSeveralTovar.cpp:108 |
| `ShadowProductButton` | булево | база, затем файл | `false` | TS.cpp:283 |
| `shoppingCardqtyTextColor` | строка | база, затем файл | `none` | uSelfService.cpp:3137 |
| `shoppingCardqtyTextFontName` | строка | файл, затем база | `ACanvas->Font->Name` | uSelfService.cpp:3142 |
| `shoppingCardqtyTextFontSize` | целое | база, затем файл | `ACanvas->Font->Size` | uSelfService.cpp:3143 |
| `shoppingCardText` | подпись на трёх языках | файл, затем база | `Cosul de cumparaturi\|Ко…` | uSelfService.cpp:2805 |
| `shoppingCardTextColor` | строка | база, затем файл | `none` | uSelfService.cpp:3122 |
| `shoppingCardTextFontName` | строка | файл, затем база | `ACanvas->Font->Name` | uSelfService.cpp:3127 |
| `shoppingCardTextFontSize` | целое | база, затем файл | `ACanvas->Font->Size` | uSelfService.cpp:3128 |
| `shoppingCardTotalPriceMarkColor` | строка | база, затем файл | `none` | uSelfService.cpp:3194 |
| `shoppingCardTotalPriceTextColor` | строка | база, затем файл | `none` | uSelfService.cpp:3181 |
| `shoppingCardUnitPriceMarkColor` | строка | база, затем файл | `none` | uSelfService.cpp:3166 |
| `shoppingCardUnitPriceTextColor` | строка | база, затем файл | `none` | uSelfService.cpp:3152 |
| `shoppingTotalPriceMarkFontName` | строка | файл, затем база | `ACanvas->Font->Name` | uSelfService.cpp:3198 |
| `shoppingTotalPriceMarkFontSize` | целое | база, затем файл | `ACanvas->Font->Size` | uSelfService.cpp:3199 |
| `shoppingTotalPriceTextFontName` | строка | файл, затем база | `ACanvas->Font->Name` | uSelfService.cpp:3185 |
| `shoppingTotalPriceTextFontSize` | целое | база, затем файл | `ACanvas->Font->Size` | uSelfService.cpp:3186 |
| `shoppingUnitPriceMarkFontName` | строка | файл, затем база | `ACanvas->Font->Name` | uSelfService.cpp:3170 |
| `shoppingUnitPriceMarkFontSize` | целое | база, затем файл | `ACanvas->Font->Size` | uSelfService.cpp:3171 |
| `shoppingUnitPriceTextFontName` | строка | файл, затем база | `ACanvas->Font->Name` | uSelfService.cpp:3156 |
| `shoppingUnitPriceTextFontSize` | целое | база, затем файл | `ACanvas->Font->Size` | uSelfService.cpp:3157 |
| `ShowCardInfo` | булево | база, затем файл | `false` | Uhvbb.cpp:2974 |
| `ShowCategoryButtonWithoutText` | булево | файл, затем база | `true` | uSelfService.cpp:1439 |
| `showCostumButtom` | булево | база, затем файл | `false` | TS.cpp:612, uSelfService.cpp:2775 |
| `ShowInformativePanel` | булево | файл, затем база | `true` | uImgMenu.cpp:337 |
| `ShowItog` | булево | только база | `false` | dtmod.cpp:770 |
| `ShowLogin` | целое | только файл | `1` | ucLogin.cpp:332 |
| `ShowMenuAddForms` | булево | файл, затем база | `true` | fMenu.cpp:1408 |
| `ShowMenuCancel` | булево | только база | `true` | fMenu.cpp:196 |
| `ShowMenuCardInfo` | булево | файл, затем база | `false` | fMenu.cpp:1419 |
| `ShowMenuCashInOut` | булево | файл, затем база | `true` | fMenu.cpp:1359 |
| `ShowMenuCertificates` | булево | база, затем файл | `false` | fMenu.cpp:1430 |
| `ShowMenuDataBase` | булево | только база | `true` | fMenu.cpp:1332 |
| `ShowMenuDeferred` | булево | только база | `true` | fMenu.cpp:1307 |
| `ShowMenuImgMenu` | булево | только база | `false` | fMenu.cpp:1317 |
| `ShowMenuLogInOut` | булево | только база | `false` | fMenu.cpp:1320 |
| `ShowMenuLotoPay` | булево | только база | `false` | fMenu.cpp:1318 |
| `ShowMenuNonCash` | булево | база, затем файл | `true` | fMenu.cpp:1449 |
| `ShowMenuRefreshCardBalance` | булево | база, затем файл | `true` | fMenu.cpp:1403 |
| `ShowMenuSelDocType` | булево | только файл | `false` | fMenu.cpp:1297 |
| `ShowMenuTME` | булево | файл, затем база | `true` | fMenu.cpp:1416 |
| `ShowMenuTvrInfo` | булево | файл, затем база | `false` | fMenu.cpp:1421 |
| `ShowMenuWebPay` | булево | база, затем файл | `true` | fMenu.cpp:1404 |
| `ShowMenuXZLog` | булево | база, затем файл | `false` | fMenu.cpp:1456 |
| `ShowPageNr` | булево | файл, затем база | `true` | TS.cpp:1804 |
| `ShowPrintLastBon` | булево | только база | `true` | Uhvbb.cpp:199 |
| `ShowSearchBarcodeButton` | булево | файл, затем база | `true` | uSelfService.cpp:1443 |
| `ShowTabSessions` | булево | только база | `false` | Uadaug.cpp:117 |
| `ShowTextCategoryButton` | булево | файл, затем база | `true` | uSelfService.cpp:1379 |
| `ShowUsedBonusInfo` | булево | база, затем файл | `false` | Uhvbb.cpp:2990 |
| `SinglePayTM` | булево | файл, затем база | `true` | dtmod.cpp:551 |
| `slideDownStartButton` | целое | база, затем файл | `3` | uSelfService.cpp:2558 |
| `slideUpStartButton` | целое | база, затем файл | `3` | uSelfService.cpp:2557 |
| `smClientNameGr1Filter` | строка | база, затем файл | `gr1 = 'E'` | dtmod.cpp:3441 |
| `SMKSocketDemoMode` | булево | файл, затем база | `false` | dtmod.cpp:14035 |
| `SMKSocketHost` | строка | база, затем файл | `127.0.0.1` | dtmod.cpp:543 |
| `SMKSocketPort` | целое | база, затем файл | `8885` | dtmod.cpp:544 |
| `SpecialCaseBChar` | булево | база, затем файл | `false` | fMenu.cpp:572 |
| `SpecialMessage` | булево | база, затем файл | `false` | dtmod.cpp:12308 |
| `SpecialMessageBeep` | булево | база, затем файл | `false` | dtmod.cpp:12323 |
| `SQLSearch` | строка | только файл |  | dtmod.cpp:3453 |
| `SQLSearchCond` | строка | только файл | ` and barcode_int ` | dtmod.cpp:3454 |
| `SQLTraceLevel` | строка | файл, затем база | `0` | dtmod.cpp:10443 |
| `SSAddDisplayHeight` | целое | база, затем файл | `fSelfService->Height/10…` | uSelfService.cpp:440 |
| `SSAddDisplayIdleMsgSize` | целое | база, затем файл | `36` | uSelfService.cpp:435 |
| `SSAddDisplayPrivetEdHeight` | целое | база, затем файл | `pnAdvTop->Height` | uSelfService.cpp:449 |
| `SSAddDisplayPrivetEdOnBottom` | булево | база, затем файл | `false` | uImgMenu.cpp:167, uSelfService.cpp:443 |
| `SSExitByPin` | булево | база, затем файл | `true` | uSelfService.cpp:698 |
| `SSImgPath` | строка | файл, затем база | `SelfService` | uSelfService.cpp:2082 |
| `SSMenuItemSize` | целое | база, затем файл | `200` | uSelfService.cpp:472 |
| `SSNeedUserPin` | булево | база, затем файл | `false` | dtmod.cpp:10869 |
| `SSPrivetEd2500` | строка | база, затем файл | `ReadStrParam(rpmDBFirst…` | uSelfService.cpp:434 |
| `SSScaleBottom` | целое | база, затем файл | `100` | uSelfService.cpp:454 |
| `SwitchUser` | булево | база, затем файл | `false` | fMenu.cpp:2203, uLock.cpp:33 |
| `SyssMayDelete` | булево | только файл |  | usdk_lSYSS.cpp:219, usdk_lSYSS.cpp:219 |
| `TCPSocketFPBPAYLetter` | строка | база, затем файл | `N` | SocketFP.cpp:394 |
| `TCPSocketFPCertLetter` | строка | база, затем файл | `C` | SocketFP.cpp:390 |
| `TCPSocketFPGiftLetter` | строка | база, затем файл | `X` | SocketFP.cpp:393 |
| `TCPSocketFPHost` | строка | база, затем файл | `127.0.0.1` | dtmod.cpp:252 |
| `TCPSocketFPOnlineLetter` | строка | база, затем файл | `O` | SocketFP.cpp:395 |
| `TCPSocketFPTMELetter` | строка | база, затем файл | `E` | SocketFP.cpp:391 |
| `TCPSocketFPTMHLetter` | строка | база, затем файл | `H` | SocketFP.cpp:392 |
| `Text1PayButton` | подпись на трёх языках | файл, затем база | `Plata\|Оплата\|Pay` | uSelfService.cpp:2626 |
| `Text1PayButtonFontSize` | целое | база, затем файл | `dxTCPay->Text1->Font->S…` | uSelfService.cpp:2627 |
| `Text1WaitButton` | подпись на трёх языках | файл, затем база | `Vă rugăm să așteptați, …` | uSelfService.cpp:2573 |
| `Text1WaitButtonFontSize` | целое | база, затем файл | `dxTCStartdxTileControlI…` | uSelfService.cpp:2577 |
| `Text1WelcomeButton` | подпись на трёх языках | файл, затем база | `Bine ați venit\|Добро по…` | uSelfService.cpp:2581 |
| `Text1WelcomeButtonFontSize` | целое | база, затем файл | `dxTCStartdxTileControlI…` | uSelfService.cpp:2583 |
| `Text2WelcomeButton` | подпись на трёх языках | файл, затем база | `Începeți cumpărăturile\|…` | uSelfService.cpp:2584 |
| `Text2WelcomeButtonFontSize` | целое | база, затем файл | `dxTCStartdxTileControlI…` | uSelfService.cpp:2587 |
| `Text3WelcomeButton` | подпись на трёх языках | файл, затем база | `Apăsați aici\|Нажмите зд…` | uSelfService.cpp:2588 |
| `Text3WelcomeButtonFontSize` | целое | база, затем файл | `dxTCStartdxTileControlI…` | uSelfService.cpp:2590 |
| `TextCategoryInfoLabel1` | подпись на трёх языках | файл, затем база | `Scanează produsele sau …` | uSelfService.cpp:2597 |
| `TextCategoryInfoLabel1FontSize` | целое | база, затем файл | `cxLabel1->Style->Font->…` | uSelfService.cpp:2603 |
| `TextCategoryInfoLabel2` | подпись на трёх языках | файл, затем база | `Nu uitați să scanați ca…` | uSelfService.cpp:2609 |
| `TextCategoryInfoLabel2FontSize` | целое | база, затем файл | `cxLabel13->Style->Font-…` | uSelfService.cpp:2610 |
| `TextCategoryInfoLabel3` | подпись на трёх языках | файл, затем база | `Nu uitați să scanați ba…` | uSelfService.cpp:2618 |
| `TextCategoryInfoLabel3FontSize` | целое | база, затем файл | `cxLabel18->Style->Font-…` | uSelfService.cpp:2619 |
| `TextCategoryInfoLabel4` | подпись на трёх языках | файл, затем база | `Cind toate produsele au…` | uSelfService.cpp:2622 |
| `TextCategoryInfoLabel4FontSize` | целое | база, затем файл | `cxLabel2->Style->Font->…` | uSelfService.cpp:2623 |
| `TMEPOSTermType` | строка | база, затем файл | `Ingenico` | TSPOSTermIP.cpp:478 |
| `TMHBarcodeMaxLength` | целое | база, затем файл | `24` | dtmod.cpp:554 |
| `TMHBarcodeMinLength` | целое | база, затем файл | `21` | dtmod.cpp:553 |
| `TMHPrefix` | строка | только файл |  | dtmod.cpp:6968 |
| `TMReportNoOfCopiesCut` | целое | файл, затем база | `1` | dtmod.cpp:12022 |
| `topIndentProductGrid` | целое | файл, затем база | `0` | TS.cpp:572 |
| `TrimBarcode` | булево | база, затем файл | `false` | dtmod.cpp:2105 |
| `TSAdjustResolution` | булево | файл, затем база | `false` | Uhvbb.cpp:2688, order.cpp:2088 |
| `TSCmdButtonsID` | целое |  | `3` | Uhvbb.cpp:2711, order.cpp:2115 |
| `TSGroupsID` | целое |  | `1` | Uhvbb.cpp:2706, order.cpp:2113 |
| `TSIncFontSizeNoImg` | булево | база, затем файл | `true` | TS.cpp:344 |
| `TSLang` | строка | база, затем файл | `RO` | TS.cpp:1409, TSDispatcher.cpp:40 |
| `TSMenuID` | целое |  | `2` | Uhvbb.cpp:2708, order.cpp:2114, и ещё 2 |
| `TSPackageMenuID` | целое |  | `2` | uImgMenu.cpp:66 |
| `TSPaymButtonsID` | целое |  | `5` | TSPay.cpp:35 |
| `TSPlacesID` | целое |  | `2` | order.cpp:2264 |
| `TSPOSID` | целое |  | `9` | TSPOSTermIP.cpp:380 |
| `TSSearchKeepLastUsed` | булево | файл, затем база | `true` | TSController.cpp:885 |
| `TSSelDocType` | целое |  | `13` | uSelDocType.cpp:32 |
| `TSSelfTvr` | целое |  | `9` | uSelfService.cpp:633 |
| `TSSELPOS` | целое |  | `12` | uSelPos.cpp:28 |
| `TSSumButtonsID` | целое |  | `4` | TSPay.cpp:34 |
| `TSVKeybdID` | целое |  | `6` | partDenum.cpp:55 |
| `TvrCount` | целое | база, затем файл | `99` | dtmod.cpp:558 |
| `TvrCountVisible` | булево | файл, затем база | `false` | Uhvbb.cpp:212 |
| `TxtCancelButton` | подпись на трёх языках | файл, затем база | `Anulare\|Отмена\|Cancel` | uSelfService.cpp:953 |
| `TxtReturnButton` | подпись на трёх языках | файл, затем база | `Inapoi\|Назад\|Back` | uImgMenu.cpp:340, uSelfService.cpp:1011 |
| `UambCenterForm` | булево | база, затем файл | `true` | uamb.cpp:57 |
| `UambSetForegroundWindow` | булево | база, затем файл | `false` | uamb.cpp:65 |
| `UDSSocketServiceEnabled` | булево | только файл | `false` | dtmod.cpp:686, fMenu.cpp:1295 |
| `UnivDepToOficiant` | булево | база, затем файл | `false` | dtmod.cpp:5697, ucLogin.cpp:495 |
| `UpgManWizardMode` | булево | файл, затем база | `false` | dtmod.cpp:421 |
| `UpperFSeparatorText` | строка | база, затем файл |  | Daisy.cpp:531, ElicomFP.cpp:747, и ещё 4 |
| `UseCardPodaroc` | булево | только база | `true` | fMenu.cpp:1340 |
| `UseFr3` | булево | база, затем файл | `true` | reports.cpp:106 |
| `UseLogOnlyForClose` | булево | только база | `false` | dtmod.cpp:8860 |
| `UseLogOnlyForErrItog` | булево | только база | `false` | dtmod.cpp:8858 |
| `UsePackedIni` | булево | только файл | `false` | ucLogin.cpp:331 |
| `UsePrintOnBase` | булево | только база | `true` | fMenu.cpp:1342 |
| `UseReturn` | булево | только база | `true` | fMenu.cpp:1288 |
| `UseSMK` | булево | база, затем файл | `false` | dtmod.cpp:522 |
| `UseSMKDBIntegration` | булево | база, затем файл | `true` | dtmod.cpp:524 |
| `UseSzLen` | булево | база, затем файл | `true` | dtmod.cpp:2392 |
| `UseTMH` | булево | база, затем файл | `true` | dtmod.cpp:518 |
| `UseVirtualFPOnError` | булево | база, затем файл | `false` | Uhvbb.cpp:850 |
| `ValutaReportNoOfCopiesCut` | целое | файл, затем база | `1` | dtmod.cpp:12110 |
| `VATValueA` | строка | база, затем файл | `0.2` | ElicomFP.cpp:660, SocketFP.cpp:521, и ещё 1 |
| `VATValueB` | строка | база, затем файл | `0.08` | ElicomFP.cpp:662, SocketFP.cpp:523, и ещё 1 |
| `VATValueC` | строка | база, затем файл | `0.05` | ElicomFP.cpp:664, SocketFP.cpp:525, и ещё 1 |
| `VATValueD` | строка | база, затем файл | `0.00` | ElicomFP.cpp:666, SocketFP.cpp:527, и ещё 1 |
| `VirtFP550` | булево | файл, затем база | `false` | dtmod.cpp:7420 |
| `VirtualFPFontSize` | целое | база, затем файл | `10` | uFiscalView.cpp:85 |
| `VirtualFPShowOnScreen` | булево | база, затем файл | `true` | uFiscalView.cpp:397 |
| `VirtualFPStayOnTop` | булево | база, затем файл | `false` | uFiscalView.cpp:36 |
| `VirtualFPWindowHeight` | целое | база, затем файл | `620` | uFiscalView.cpp:32 |
| `VirtualFPWindowLeft` | целое | база, затем файл | `40` | uFiscalView.cpp:33 |
| `VirtualFPWindowTop` | целое | база, затем файл | `40` | uFiscalView.cpp:34 |
| `vmsUnivCreditCheck` | булево | база, затем файл | `false` | MultiPaymentsPay.cpp:84 |
| `WalletPassColor` | строка | база, затем файл |  | uWalletPass.cpp:198 |
| `WebMode` | булево | база, затем файл | `false` | dtmod.cpp:528 |
| `WebPayDigitKeyCheck` | булево | база, затем файл | `false` | WebPay.cpp:544 |
| `WebPayGetUserMessage` | булево | база, затем файл | `true` | WebPay.cpp:139 |
| `WebUpdateEnabled` | булево | только файл | `false` | dtmod.cpp:457 |
| `WebUpdateFilesListUrl` | строка | только файл | `https://una.md/ticket/d…` | dtmod.cpp:462 |
| `WebUpdateUrl` | строка | только файл | `https://update.una.md/` | dtmod.cpp:461 |
| `WebVersion` | строка | только файл | `0` | dtmod.cpp:466 |
| `widthMenuButtons` | целое | файл, затем база | `200` | uSelfService.cpp:758 |
| `ZeroPriceWarn` | булево | база, затем файл | `true` | dtmod.cpp:10717 |
| `ZReminderInterval` | целое | база, затем файл | `5` | Uhvbb.cpp:1933, dtmod.cpp:12352 |
| `ZReminderPeriodicity` | целое | база, затем файл | `3` | Uhvbb.cpp:1935, dtmod.cpp:12354 |
| `ZReminderSecondsBeforeLockPrint` | целое | база, затем файл | `300` | Uhvbb.cpp:1937 |
| `ZReminderSecondsBeforeLockSales` | целое | база, затем файл | `600` | Uhvbb.cpp:1936 |
| `ZReminderStartBefore` | целое | база, затем файл | `60` | Uhvbb.cpp:1934, dtmod.cpp:12353 |
| `ZXReportByAdminOrInventr` | булево | база, затем файл | `false` | dtmod.cpp:6382 |
| `ZXReportByPIN` | булево | база, затем файл | `false` | dtmod.cpp:6386 |

---

## Как это собрано

Просмотрено 852 файлов исходников кассы и её компонентов. Каждое обращение к настройке найдено разбором вызова со счётом скобок, поэтому многострочные вызовы и вложенные выражения разобраны верно. Имя параметра берётся только из строкового литерала: там, где оно собирается в коде из кусков, параметр в справочник не попадает — выдумывать имя хуже, чем его не показать.

Поведение чтения ini проверено вызовом той самой функции Windows, которой пользуется касса, а не взято из общих соображений.

Пояснения на русском живут отдельно, в `cfgtool/descriptions.py`, и при пересборке не теряются.
