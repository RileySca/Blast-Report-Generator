
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 12:22:39 2026
"""
import os
os.system("title Blast Report Generator")
APP_VERSION = "v1.3.1"

print("=" * 40)
print(f" Blast Report Generator {APP_VERSION}")
print("=" * 40)
print("• Add job folder shortcut to OneDrive")
print("• Ensure blast PDF is available locally")
print("• Do not have template or old reports open\n")

import getpass
import re

from filesystem import newest_pdf, individual_blast_reports
from pdfprocess import extract_blasts
from excelwriter import write_to_template
from blastui import blast_folder


try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

Debug = False

# ---------- helpers ----------
def extract_blast_number_from_filename(filename):
    #finds previous blast file name for naming template
    match = re.search(r"blast\s*(\d+)", filename.lower())
    return int(match.group(1)) if match else None


def newest_blast_excel(root):
    #Sorts the blasts to find the most recent excel to copy name
    excels = []
    for f in os.listdir(root):
        if f.lower().endswith(".xlsx") and "blast" in f.lower():
            full = os.path.join(root, f)
            if os.path.isfile(full):
                excels.append(full)
    return max(excels, key=os.path.getmtime) if excels else None


# ---------- app start ----------
def main():
    # get the user name of person using so that copying file path from documents is not needed
    username = getpass.getuser()
    # Job number so search can start
    job_number = blast_folder()
    # Where the script will look for job number
    onedrive_root = rf"C:\Users\{username}\OneDrive - Redacted"

    job_root = None
    # in the onedrive foldder it will look for a folder with the job number
    for d in os.listdir(onedrive_root):
        if d.startswith("PM Site") and d.endswith(str(job_number)):
            job_root = os.path.join(onedrive_root, d)
            break
    if Debug == True:
        job_root = r"C:\Users\riley.scallion\Blast app\test\Redacted"
        print("Debug on")
    # if no job nummber is found it stops and asks to make sure one drive job is synced
    if not job_root:
        raise FileNotFoundError(f"Could not find job folder for {job_number}.\n""Make sure the job is synced to OneDrive.")

    # calls the function used to find the individual blast folder
    ibr_folder = individual_blast_reports(job_root)
    print("IBR folder:", ibr_folder)
    if not ibr_folder:
        raise FileNotFoundError("Could not find Individual Blast Reports / Records folder.")

    # calls the function that finds newest pdf which should be the report
    pdf_file = newest_pdf(ibr_folder)
    if not pdf_file:
        raise FileNotFoundError("No blast PDF found.")

    # ---------- PDF → DataFrame ----------
    df, blast_date, file_blast_date = extract_blasts(pdf_file)

    if df.empty:
        raise FileNotFoundError("No valid machine data extracted.")

    if "BlastGroup" not in df.columns:
        df["BlastGroup"] = 1
    # the location of the blast template everything will be written to
    TEMPLATE_PATH = (rf"C:\Users\{username}\OneDrive Redacted/BLAST_TEMPLATE.xlsx")


    # ---------- determine blast number ----------
    last_excel = newest_blast_excel(ibr_folder)
    # Takes the name of the last blast finds the blast number and increases the number by 1. if no excel then blast number is 1
    if last_excel:
        last_blast = extract_blast_number_from_filename(os.path.basename(last_excel))
        new_blast_number = last_blast + 1 if last_blast is not None else 1
    else:
        new_blast_number = 1



# ---------- write one Excel per blast ----------
    for blast_id, blast_df in df.groupby("BlastGroup"):
        blast_df = blast_df.reset_index(drop=True)

        Technician = blast_df.iloc[0]["Technician"]
        Total = blast_df.iloc[0]["explosives"]
        MaxDelay = blast_df.iloc[0]["MaxDelay"]

        filename = f"{file_blast_date} - {new_blast_number}.xlsx"
        output_path = os.path.join(ibr_folder, filename)

        write_to_template(
            blast_df,
            TEMPLATE_PATH,
            output_path,
            blast_date,
            Technician,
            Total,
            MaxDelay,
            new_blast_number
       )

        os.startfile(output_path)
        new_blast_number += 1
    # folder the excel report was put in
    print("IBR folder:", ibr_folder)
    

if __name__ == "__main__":
    while True:
        try:
            main()
            prompt = "\nCompleted successfully."
        except Exception as e:
            print("\nERROR:")
            print(e)
            prompt = "\nAn error occurred."

        choice = input(
            f"{prompt} Press ENTER to continue, or type Q to quit: "
        ).strip().lower()

        if choice == "q":
            break
