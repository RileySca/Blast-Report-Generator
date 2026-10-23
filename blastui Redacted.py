# -*- coding: utf-8 -*-
"""
Created on Thu May 21 12:03:12 2026

"""

# blastui.py
def blast_folder():
    job_number = input("Enter job number (e.g. Redacted):\n").strip()

    if not job_number:
        raise SystemExit("No job number entered.")

    return job_number



