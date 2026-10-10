# -*- coding: utf-8 -*-
"""Кодировки исходников кассы: по каждому файлу - BOM / строгий UTF-8 / cp1251 / ascii."""
import os, sys, re, collections
ROOT = r"D:\RAD_Tokyo\Sources\UAMenu"
EXT = (".cpp", ".h", ".hpp", ".dfm", ".pas", ".rc")
SKIP = ("backup-", "Win32", "__history", "__recovery", "Debug", "Release", "pypos", "cfgtool", "docs", "Linella")
stat = collections.Counter(); per_ext = collections.defaultdict(collections.Counter)
cyr1251 = []
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if not d.startswith(SKIP) and d not in SKIP]
    for f in files:
        if not f.lower().endswith(EXT):
            continue
        p = os.path.join(root, f); raw = open(p, "rb").read()
        if raw.startswith(b"\xef\xbb\xbf"):
            kind = "utf8-bom"
        elif all(b < 0x80 for b in raw):
            kind = "ascii"
        else:
            try:
                raw.decode("utf-8"); kind = "utf8-nobom"
            except UnicodeDecodeError:
                kind = "cp1251"
                if f.lower().endswith((".cpp", ".h")):
                    cyr1251.append(os.path.relpath(p, ROOT))
        stat[kind] += 1; per_ext[os.path.splitext(f)[1].lower()][kind] += 1
print(dict(stat))
for e, c in sorted(per_ext.items()):
    print(e, dict(c))
print("cp1251 .cpp/.h:", len(cyr1251))
for p in cyr1251[:400]:
    print("  ", p)
