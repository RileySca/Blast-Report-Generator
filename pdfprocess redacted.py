# -*- coding: utf-8 -*-
"""
Created on Wed May 20 12:20:33 2026

"""

# pdfprocess.py
import pdfplumber
import re
import pandas as pd
from datetime import datetime
from pdfvalues import extract_values


def extract_blast_number(filename):
    match = re.search(r'blast\s*(\d+)', filename.lower())
    if match:
        return int(match.group(1))
    return None

def extract_blasts(pdf_path):
    data = []
    blast_date = None
    file_blast_date = None
    # Pulls all the data and text available in the report. Should only be the machine reports none from hand written notes
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # ---- Date ----
            #Searches the found data for a month and then adds the day and year
            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',text)
            #Once the date is found it converts to a numeric format
            if date_match:
                blast_date = datetime.strptime(date_match.group(), "%B %d, %Y").strftime("%b %d, %Y")
                # Takes the year away for file name formatting
                file_blast_date = blast_date.rsplit(",", 1)[0]
            # ---- Time ----
            # Searches for the time of the blast and takes the hour minute seconds
            time_match = re.search(r'at\s(\d{2}:\d{2}:\d{2})', text)
            if not time_match:
                continue

            time_str = time_match.group(1)
            time_obj = datetime.strptime(time_str, "%H:%M:%S")
            time_display = time_obj.strftime("%I:%M %p").lstrip("0")

            values = extract_values(text)

            # Only keep valid machine rows
            if all(values.get(k) is not None for k in ("Tran_PPv", "Vert_PPv", "Long_PPv")):
                data.append({
                    "Time": time_display,        # for Excel (12âhour)
                    "Time_24": time_str[:5],     # for blast grouping
                    **values
                    })


    # ---- Build DataFrame ----
    df = pd.DataFrame(data)

    if df.empty:
        return df, blast_date, file_blast_date

    # ---- Sort by time ----
    df = df.sort_values("Time_24").reset_index(drop=True)

    # ---- Group into blasts by time gap ----
    blast_id = 1
    blast_ids = [blast_id]

    for i in range(1, len(df)):
        h1, m1 = map(int, df.loc[i - 1, "Time_24"].split(":"))
        h2, m2 = map(int, df.loc[i, "Time_24"].split(":"))

        diff_seconds = abs((h2 * 60 + m2) - (h1 * 60 + m1)) * 60

        #  new blast if gap > 2 minutes
        if diff_seconds > 120:
            blast_id += 1

        blast_ids.append(blast_id)

    df["BlastGroup"] = blast_ids

    return df, blast_date, file_blast_date