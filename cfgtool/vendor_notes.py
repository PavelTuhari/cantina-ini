# -*- coding: utf-8 -*-
"""Пояснения к параметрам из перечня, присланного заказчиком.

Это не мой текст и не текст, извлечённый из кода: перечень пришёл файлом
`parametri.txt` — имя параметра, значение и короткое пояснение по-английски.
Хранится отдельно от `descriptions.py`, чтобы было видно, где чьи слова.

## Что с перечнем не так

В присланном файле 521 строк с параметрами. **Кодом подтверждается только
66.** Остальные 455 имён не встречаются ни в одном исходнике кассы и её
компонентов — ни как параметр, ни как строковый литерал.

Это не пропуск в моём поиске. Настоящие параметры идут подряд до строки 69,
а с 30 и до конца файла не подтверждается ни одно имя. Содержание
этой части говорит само за себя: `UmbrellaSessionTimeout`,
`KnowledgeBaseIntegration`, `SupportQualityAssessment`, `AssetVersioning` — в
кассовой программе такого нет. У всех до единого значение `false`, включая
`UmbrellaServiceURL` и `SendTextTimerInterval`, где должны быть адрес и
интервал.

Похоже, перечень кто-то дополнил выдуманными строками. Сюда взята только
подтверждённая часть: 66 параметров. Полный файл не теряется — он лежит
в приложении к разбору, см. `docs/selfservice-config.md`.

Пояснение показывается, только если своего нет: оно короче и общее.
"""

from __future__ import unicode_literals

# имя -> (значение из перечня, пояснение заказчика)
NOTES = {
    "AddDisplayDecimalColor": ("false", "Specifies the decimal color value for the additional display."),
    "AddDisplayIdleMsgSize": ("false", "Sets the size of the idle message on the additional display."),
    "AskPrintInvoice": ("true", "Asks the user if they want to print the invoice after completing a transaction."),
    "AutoCompletePayment": ("false", "Automatically completes payment processing when conditions are met."),
    "AutoDisableEmptyCardPayment": ("false", "Automatically disables card payment if the card is empty."),
    "AutoSetPayTerm": ("false", "Automatically sets the payment term in transactions."),
    "BegRePrintEnabled": ("false", "Enables or disables the reprint functionality for receipts."),
    "BemolReaderCom": ("false", "COM port used for the Bemol reader communication."),
    "BemolReaderTries": ("false", "Number of tries for reading data from the Bemol reader."),
    "CMD_circ": ("false", "Command circulation parameter, used for specific network commands."),
    "CanCancelPOSPay": ("false", "Specifies if the POS payment can be cancelled."),
    "CancelCheckInPrinter": ("false", "Allows cancellation of the check directly in the printer."),
    "CekVisible": ("true", "Specifies whether the check payment option is visible to the user."),
    "CheckTestMode": ("false", "Checks if the system is in test mode."),
    "CheckZeroPosition": ("false", "Controls checking for items with zero quantity in orders."),
    "CircusEnabled": ("false", "Enables special features for the Circus module."),
    "DisableReturnFP": ("false", "Disables return functionality for fiscal point of sale terminals."),
    "FNRequiredOnReturn": ("false", "Determines if a fiscal number is required on returns."),
    "FastEmpBarcodeAuth": ("false", "Enables quick barcode authentication for employees."),
    "FillRcptInComenzAdd": ("false", "Automatically fills the receipt when adding a command."),
    "FormCBAlignLeft": ("false", "Aligns the form control block to the left."),
    "FormCBAlignRight": ("false", "Aligns the form control block to the right."),
    "IgnoreCDDError": ("false", "Specifies whether to ignore customer display device errors."),
    "IgnoreNFPErrors": ("false", "Specifies whether to ignore non-fatal fiscal printer errors."),
    "KvintMode": ("false", "Activates or deactivates Kvint mode, affecting payment processing or information display."),
    "KvintModePOSTermModeType": ("false", "Specifies the type mode for Kvint POS terminal."),
    "MultiCurrencyPrices": ("false", "Allows displaying prices in multiple currencies."),
    "PaymentsDigitKeyCheck": ("false", "Enables or disables digit key checking during payment processing."),
    "PaymentsEnabled": ("false", "Enables or disables the payment functionalities."),
    "PaymentsGetUserMessage": ("false", "Determines if a user message should be retrieved during payments."),
    "PrintRCPTClearEmptyLines": ("false", "Specifies whether to clear empty lines when printing receipts."),
    "PrivetEd2500": ("false", "Configuration parameter related to PrivetEd2500 functionality."),
    "SSAddDisplayHeight": ("false", "Sets the height of the self-service additional display."),
    "SSAddDisplayIdleMsgSize": ("false", "Sets the idle message size on the self-service additional display."),
    "SSAddDisplayOnTop": ("false", "Specifies if the self-service additional display should be on top."),
    "SSAddDisplayPrivetEdHeight": ("false", "Sets the height of the PrivetEd area on the self-service display."),
    "SSAddDisplayPrivetEdOnBottom": ("false", "Specifies if the PrivetEd on the self-service display should be at the bottom."),
    "SSExitByPin": ("false", "Specifies if the self-service session can be exited by entering a PIN."),
    "SSGetWeightOnShowScale": ("false", "Specifies if the weight should be retrieved when the scale is shown in self-service mode."),
    "SSMenuItemSize": ("false", "Size of the menu items on the self-service display."),
    "SSPrivetEd2500": ("false", "Specific parameter related to self-service PrivetEd2500 functionality."),
    "SSScaleBottom": ("false", "Scaling factor for the bottom part of the self-service display."),
    "SSScaleFactor": ("false", "Sets the scale factor for the self-service screen."),
    "SSSelectPackageOnStart": ("false", "Determines if a package selection is required at the start of the self-service session."),
    "SSShowLogoImage": ("false", "Specifies if the logo image should be shown on the self-service display."),
    "SSThanksInterval": ("false", "Interval for displaying the 'thanks' message on the self-service display."),
    "SSWeightThreads": ("false", "Number of threads used for weight processing in self-service mode."),
    "SearchByClientNameEnabled": ("false", "Enables or disables the feature to search by client name."),
    "SearchByPersCodeEnabled": ("false", "Enables or disables the feature to search by personal code."),
    "SendTextMsgCount": ("false", "Sets the number of text messages to be sent in a given interval."),
    "SendTextTimerEnabled": ("false", "Enables or disables the timer for sending text."),
    "SendTextTimerInterval": ("false", "Sets the interval for the timer used to send text messages."),
    "ShowCertifcatesLbls": ("false", "Controls the display of labels for certificates."),
    "ShowCertificateField": ("false", "Controls the display of the certificate field in the interface."),
    "SpecialCheckFailedMsg": ("false", "Specifies whether to display a special message when a check fails."),
    "TSIncFontSizeNoImg": ("false", "Increases font size for TS module when no image is present."),
    "TSUseMultiTab": ("false", "Enables or disables the use of multiple tabs in the TS module."),
    "UambCenterForm": ("false", "Specifies whether to center the form on the screen in UAMb module."),
    "UambSetForegroundWindow": ("false", "Specifies whether to set the UAMb window to the foreground."),
    "UnivDepToOficiant": ("false", "Specifies whether the university department should be automatically assigned to an attendant."),
    "UseFr3": ("false", "Determines whether to use the Fr3 reporting engine."),
    "UseTSLang": ("false", "Specifies whether to use the language settings in the TS module."),
    "UseTranslations": ("false", "Determines if the system should use translations for the user interface."),
    "UseVirtualFPOnError": ("false", "Uses a virtual fiscal printer in case of errors with the physical one."),
    "WebPayDigitKeyCheck": ("false", "Enables or disables digit key checking during web payment processing."),
    "WebPayGetUserMessage": ("false", "Determines if a user message should be retrieved during web payments."),
}


def note_for(name):
    """Пояснение заказчика либо пустая строка."""
    rec = NOTES.get(name)
    if rec is None:
        low = name.lower()
        for k in NOTES:
            if k.lower() == low:
                rec = NOTES[k]
                break
    return rec[1] if rec else ""


def listed_value(name):
    """Значение, указанное в присланном перечне."""
    rec = NOTES.get(name)
    return rec[0] if rec else ""
