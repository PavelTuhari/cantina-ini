# Примеры `cantina.ini`

Все файлы — реальные настройки касс из рабочего каталога владельца, собранные за несколько лет для разных торговых точек и интеграций. Перед публикацией каждый файл прошёл через `tools/scrub_examples.py`: пароли, ключи и токены заменены пометками `@secret:<файл>/<секция>/<ключ>` (так их читает касса из реестра, см. `docs/secrets.md`), закомментированные секреты — на `@removed`, IP-адреса — на `<ip>`, почта — на `<email>`. Остальное — байт в байт, включая кодировку (CP1251 либо UTF-8 с BOM) и дубли строк.

Как касса выбирает файл и почему его нельзя копировать между точками — `docs/install.md`. Что значит каждый ключ — `docs/cantina-ini.md`.

| Файл | Строк | Кодировка | PosID | Server | Schema | FiscalPrinter | Секретов → пометки | Удалено комментариев |
|---|---:|---|---|---|---|---|---:|---:|
| [2025_cantina.ini](2025_cantina.ini) | 372 | cp1251 | 9012 | BASE | — | VirtualFP | 1 | 0 |
| [cantina_111.ini](cantina_111.ini) | 469 | cp1251 | — | clouddev | — | DatecsFP550 | 1 | 0 |
| [cantina+.ini](cantina+.ini) | 539 | cp1251 | 305 | rezerv | pos | VirtualFP | 0 | 1 |
| [cantina----.ini](cantina----.ini) | 548 | cp1251 | 101 | casa | pos | VirtualFP | 0 | 1 |
| [cantina-alisca_pos.ini](cantina-alisca_pos.ini) | 324 | cp1251 | 101 | casa | — | virtualfp | 1 | 0 |
| [cantina.ini](cantina.ini) | 766 | cp1251 | 101 | clouddev | bonuspos_self24 | VirtualFP | 1 | 4 |
| [cantina.before-selftest.ini](cantina.before-selftest.ini) | 551 | cp1251 | 101 | clouddev | pos | VirtualFP | 0 | 1 |
| [cantina.ini](cantina.ini) | 527 | cp1251 | 101 | clouddev | pos | VirtualFP | 1 | 1 |
| [cantina_1.ini](cantina_1.ini) | 552 | cp1251 | 101 | clouddev | pos | VirtualFP | 0 | 1 |
| [cantina_111.ini](cantina_111.ini) | 398 | cp1251 | 101 | clouddev | — | ElicomFP | 1 | 0 |
| [cantina_15.06.2023_rogob.ini](cantina_15.06.2023_rogob.ini) | 346 | cp1251 | — | clouddev | — | IKC_E260T | 1 | 0 |
| [cantina_1_Rogob.ini](cantina_1_Rogob.ini) | 345 | cp1251 | — | rogob992 | — | VirtualFP | 1 | 0 |
| [cantina_2023.07.12.ini](cantina_2023.07.12.ini) | 549 | cp1251 | 5000 | clouddev | pos_rogob | IKC_E260T | 0 | 1 |
| [cantina_2023.08.22.ini](cantina_2023.08.22.ini) | 468 | cp1251 | — | clouddev | — | VirtualFP | 1 | 0 |
| [cantina_2023.10.02.ini](cantina_2023.10.02.ini) | 410 | cp1251 | 101 | clouddev | — | DatecsFP550 | 1 | 0 |
| [cantina_2023.12.27.ini](cantina_2023.12.27.ini) | 473 | cp1251 | — | clouddev | — | DatecsFP550 | 1 | 0 |
| [cantina_2023_10_09.ini](cantina_2023_10_09.ini) | 345 | cp1251 | — | rogob992 | — | VirtualFP | 1 | 0 |
| [cantina___2.ini](cantina___2.ini) | 469 | cp1251 | — | clouddev | — | DatecsFP550 | 1 | 0 |
| [cantina_.ini](cantina_.ini) | 459 | cp1251 | 1005 | casa | — | VirtualFP | 0 | 1 |
| [cantina__11.ini](cantina__11.ini) | 469 | cp1251 | — | clouddev | — | DatecsFP550 | 1 | 0 |
| [cantina___.ini](cantina___.ini) | 452 | cp1251 | — | casa | — | DatecsFP550 | 1 | 0 |
| [cantina_____.ini](cantina_____.ini) | 398 | cp1251 | 201 | XE_MAGAZ1 | — | VirtualFP | 3 | 0 |
| [cantina_alisca.ini](cantina_alisca.ini) | 324 | cp1251 | 101 | alisca_pos | — | virtualfp | 1 | 0 |
| [cantina_backup_sandu_2024_04_22.ini](cantina_backup_sandu_2024_04_22.ini) | 549 | cp1251 | 101 | casa | pos | VirtualFP | 0 | 1 |
| [cantina_bcasa.ini](cantina_bcasa.ini) | 394 | cp1251 | 22501 | xe | — | DatecsFP550 | 1 | 0 |
| [cantina_bemol31.ini](cantina_bemol31.ini) | 354 | cp1251 | — | bemol_m1 | — | VirtualFP | 1 | 0 |
| [cantina_bemolbpay.ini](cantina_bemolbpay.ini) | 525 | cp1251 | 6301 | casa | pos | VirtualFP | 0 | 1 |
| [cantina_bmx.ini](cantina_bmx.ini) | 318 | cp1251 | — | clouddev | — | VIRTUALFP | 1 | 0 |
| [cantina_bomba.ini](cantina_bomba.ini) | 397 | cp1251 | 22501 | xe | — | VirtualFP | 1 | 0 |
| [cantina_Bomba_Credit.ini](cantina_Bomba_Credit.ini) | 455 | cp1251 | — | clouddev | POS_BOMBA | TCPSocketFP | 1 | 0 |
| [cantina_BombaMPAY.ini](cantina_BombaMPAY.ini) | 396 | cp1251 | 101 | xe | — | DatecsFP550 | 1 | 0 |
| [cantina_dlc2.ini](cantina_dlc2.ini) | 360 | cp1251 | 9140 | — | — | VirtualFP | 1 | 0 |
| [cantina_dls_last.ini](cantina_dls_last.ini) | 529 | cp1251 | 913 | dlc1r | lin_cassa | VirtualFP | 1 | 1 |
| [cantina_dulcinella.ini](cantina_dulcinella.ini) | 526 | cp1251 | 913 | clouddev | pos_dulcinella | VirtualFP | 0 | 1 |
| [cantina_Dulcintella_22.ini](cantina_Dulcintella_22.ini) | 331 | cp1251 | 101 | clouddev | — | ElicomFP | 1 | 0 |
| [cantina_ferma.ini](cantina_ferma.ini) | 469 | cp1251 | 101 | cloudbd | — | VirtualFP | 0 | 1 |
| [cantina_goose.ini](cantina_goose.ini) | 354 | cp1251 | 201 | goose_pos2r | — | VirtualFP | 1 | 0 |
| [cantina_kvint.ini](cantina_kvint.ini) | 358 | cp1251 | 101 | KVINT_FRONTO | — | VirtualFP | 2 | 0 |
| [cantina_kvint2.ini](cantina_kvint2.ini) | 365 | cp1251 | 101 | KVINT_FRONTO | — | VirtualFP | 2 | 0 |
| [cantina_L.ini](cantina_L.ini) | 470 | cp1251 | — | clouddev | — | DatecsFP550 | 1 | 0 |
| [cantina_last.ini](cantina_last.ini) | 324 | cp1251 | 101 | alisca_pos | — | virtualfp | 1 | 0 |
| [cantina_LOCAL_2.ini](cantina_LOCAL_2.ini) | 481 | cp1251 | 101 | casa1 | — | VirtualFP | 0 | 1 |
| [cantina_LOCAL.ini](cantina_LOCAL.ini) | 428 | cp1251 | 1211 | clouddev | — | DatecsFP550 | 1 | 0 |
| [cantina_LOCAL_WORK.ini](cantina_LOCAL_WORK.ini) | 740 | cp1251 | 301 | casa | bonuspos_self24 | VirtualFP | 2 | 1 |
| [cantina_MoldElectrica.ini](cantina_MoldElectrica.ini) | 538 | cp1251 | 101 | m45r | pos | VirtualFP | 0 | 1 |
| [cantina_naringi.ini](cantina_naringi.ini) | 346 | cp1251 | — | bemol_naringi | pos | VirtualFP | 1 | 0 |
| [cantina_pm.ini](cantina_pm.ini) | 331 | cp1251 | 437 | xe | — | VirtualFP | 1 | 0 |
| [cantina_pos.ini](cantina_pos.ini) | 393 | cp1251 | 101 | clouddev | — | VirtualFP | 1 | 0 |
| [cantina_PosMPAY.ini](cantina_PosMPAY.ini) | 470 | cp1251 | — | clouddev | — | VirtualFP | 1 | 0 |
| [cantina_postest_mr.ini](cantina_postest_mr.ini) | 417 | cp1251 | — | casatest | — | VirtualFP | 1 | 0 |
| [cantina_rogob.ini](cantina_rogob.ini) | 549 | cp1251 | 5000 | clouddev | pos_rogob | IKC_E260T | 0 | 1 |
| [cantina_TO_TEST_LOCAL.ini](cantina_TO_TEST_LOCAL.ini) | 730 | cp1251 | 301 | casa | bonuspos_self24 | VirtualFP | 0 | 1 |
| [cantina_wine.ini](cantina_wine.ini) | 376 | cp1251 | 201 | clouddev | — | VirtualFP | 0 | 1 |
| [cantina_WORK_UA.ini](cantina_WORK_UA.ini) | 740 | cp1251 | 301 | casa | bonuspos_self24 | VirtualFP | 2 | 1 |
| [cantina_typo.ini](cantina_typo.ini) | 455 | cp1251 | — | clouddev | POS_BOMBA | DatecsFP550 | 1 | 0 |
| [cantinaFCO.ini](cantinaFCO.ini) | 468 | cp1251 | — | clouddev | — | VirtualFP | 1 | 0 |
| [FOXI_cantina.ini](FOXI_cantina.ini) | 729 | cp1251 | 301 | casa | bonuspos_self24 | DatecsFP550 | 0 | 1 |
| [mtc_cantina.ini](mtc_cantina.ini) | 440 | utf-8 | 101 | CANTINA_TEST | catex_pos | DatecsFP550 | 0 | 1 |
| [old_pegas_cantina.ini](old_pegas_cantina.ini) | 481 | cp1251 | 101 | casa1 | — | VirtualFP | 0 | 1 |
| [pegas_cantina.ini](pegas_cantina.ini) | 483 | cp1251 | 101 | casa1 | — | VirtualFP | 2 | 1 |
| [pos_bomba_cantina.ini](pos_bomba_cantina.ini) | 398 | cp1251 | 101 | clouddev | — | ElicomFP | 1 | 0 |
| [POS_cantina.ini](POS_cantina.ini) | 472 | cp1251 | — | clouddev | — | DatecsFP550 | 1 | 0 |
| [selftest-erp.ini](selftest-erp.ini) | 32 | cp1251 | — | clouddev | bonuspos_self24 | — | 2 | 0 |
| [selftest-ledger.ini](selftest-ledger.ini) | 54 | cp1251 | — | clouddev | bonuspos_self24 | — | 2 | 0 |
| [selftest.ini](selftest.ini) | 99 | cp1251 | — | clouddev | bonuspos_self24 | — | 0 | 0 |
| [sscantina.ini](sscantina.ini) | 398 | cp1251 | — | — | — | — | 0 | 0 |
| [zbvv_cantina.ini](zbvv_cantina.ini) | 481 | cp1251 | 101 | casa1 | — | VirtualFP | 0 | 1 |
