# -*- coding: utf-8 -*-
"""
Created on Wed May 20 12:22:16 2026

"""


# filesystem.py
import os

def individual_blast_reports(job_root):
    """
    Find the folder that represents Individual Blast Reports,
    regardless of numbering or prefixes like '.4-' or '9.'.
    """
    for root, dirs, _ in os.walk(job_root):
        for d in dirs:
            name = d.lower()
            # if a folder has the word blast and or report this folder is selected
            if ("blast" in name or"blasting" in name) and("report" in name or "record" in name or "records" in name or "reports" in name) and "individual" in name:
                return os.path.join(root, d)
    return None






def newest_pdf(root):
    pdfs = []
    # Looks in the folder found for a pdf which will be the blast report
    for path, _, files in os.walk(root):
        for f in files:
            if f.lower().endswith(".pdf"):
                full = os.path.join(path, f)
                pdfs.append(full)

    if not pdfs:
        return None
    # if there are multiple pdfs the newest one will be used
    if len(pdfs) > 1:
        print(f" Multiple PDFs found ({len(pdfs)}). Using newest.")

    return max(pdfs, key=os.path.getmtime)





