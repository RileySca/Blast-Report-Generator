# -*- coding: utf-8 -*-
"""
Created on Wed May 20 12:20:00 2026

"""

# pdfvalues.py
import re

def extract_values(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    def safe_float(v):
        try:
            return float(v)
        except:
            return None
    # sets the machine data to nothing incase there are multiple reports in one file.
    tran_ppv = vert_ppv = long_ppv = None
    tran_freq = vert_freq = long_freq = None

    # PPV (mm/s only)
    for line in lines:
        if line.startswith("PPV") and "mm/s" in line:
            nums = re.findall(r'\d+\.\d+', line)
            if len(nums) >= 3:
                tran_ppv, vert_ppv, long_ppv = map(safe_float, nums[:3])
            break

    # ZC Freq (skip microphone)
    for line in lines:
        if line.startswith("ZC Freq"):
            nums = re.findall(r'\d+', line)
            if len(nums) >= 3:
                tran_freq, vert_freq, long_freq = map(safe_float, nums[:3])
                break

    # Serial
    serial = None
    for line in lines:
        if "Serial Number" in line:
            serial = line.split("Serial Number", 1)[1].strip()
            break

    # Street address
    address = None
    for line in lines:
        if line.lower().startswith("location"):
            address = re.sub(r"location[:\s]*", "", line, flags=re.IGNORECASE).strip()
            address = address.split("Max")[0].strip()
            break



    # Machine location
    easting = None
    northing = None
    for line in lines:
        if "E /" in line or "E/" in line:
            nums = re.findall(r'\d+', line)
            if len(nums) >= 2:
                easting = int(nums[0])
                northing = int(nums[1])
            break

    #Machine Distance to blast
    distance = None
    for i, line in enumerate(lines):
        if "Max/Delay" in line:
            if i + 1 < len(lines):
                nums = re.findall(r'\d+', lines[i + 1])
                if nums:
                    distance = int(nums[0])
            break

    #Blast Technician Name
    operator = None
    for line in lines:
        if line.startswith("Operator/Setup:"):
            val = line.replace("Operator/Setup:", "").strip()
            operator = val.split("/")[0].strip()
            break

    # Air DB measure at machine
    air_db = None
    air_match = re.search(r'PSPL.*?(\d+(?:\.\d+)?)\s*dB\(L\)',text,re.DOTALL)

    if air_match:
        air_db = float(air_match.group(1))

    #Total Blast Explosives
    exp_match = re.search(r'Total Explosives\s*-\s*([\d\.]+)', text)
    explosives = float(exp_match.group(1)) if exp_match else None

    #Max/Delay
    delay_match = re.search(r'Max/Delay\s*-\s*([\d\.]+)', text)
    max_delay = float(delay_match.group(1)) if delay_match else None


    return {
        "Tran_PPv": tran_ppv,
        "Tran_Freq": tran_freq,
        "Vert_PPv": vert_ppv,
        "Vert_Freq": vert_freq,
        "Long_PPv": long_ppv,
        "Long_Freq": long_freq,
        "Serial": serial,
        "Location": address,
        "Easting": easting,
        "Northing": northing,
        "Distance": distance,
        "Technician": operator,
        "AirDB": air_db,
        "explosives": explosives,
        "MaxDelay": max_delay
        }