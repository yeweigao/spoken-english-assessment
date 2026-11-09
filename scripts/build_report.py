#!/usr/bin/env python3
"""Merge report-front.pdf + report-back.pdf (current directory) into report.pdf."""
import os
from pypdf import PdfWriter, PdfReader
w = PdfWriter()
for name in ('report-front.pdf', 'report-back.pdf'):
    for p in PdfReader(name).pages:
        w.add_page(p)
out = os.path.join(os.getcwd(), 'report.pdf')
with open(out, 'wb') as f:
    w.write(f)
print('saved', out)
