import tkinter as tk
from tkinter import filedialog, messagebox
import re
from collections import defaultdict
from datetime import datetime

# Prøv å lese filen med utf-8 først, og fall tilbake til iso-8859-1 om nødvendig
def read_file_with_fallback(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='strict') as file:
            return file.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='iso-8859-1', errors='replace') as file:
            return file.readlines()

# Ekstrakt måneder fra filen, filtrer basert på dato
def extract_filtered_months(filepath, start_date, end_date):
    months = defaultdict(list)
    try:
        lines = read_file_with_fallback(filepath)

        # Bruk regex for å finne linjer som begynner med "15" og hente datoene
        for line in lines:
            if line.startswith('"15"'):
                match = re.search(r'"(\d{8})"', line)  # Finn datoen i format YYYYMMDD
                if match:
                    date_str = match.group(1)
                    date_obj = datetime.strptime(date_str, "%Y%m%d")  # Konverter til datetime-objekt
                    if start_date <= date_obj <= end_date:
                        year = date_str[:4]
                        month = date_str[4:6]
                        months[f"{month}-{year}"].append(line)
    except Exception as e:
        messagebox.showerror("Feil", f"Det oppstod en feil ved lesing av filen: {str(e)}")

    return sorted(months.keys())  # Returner sortert liste av måneder i format MM-YYYY

# Sjekk for duplikater i linjene, ignorer siste verdi etter komma og linjer som starter med "99"
def check_for_duplicates(lines):
    line_dict = defaultdict(list)
    duplicates = []
    
    for i, line in enumerate(lines):
        if line.startswith('"15"'):  # Bare sjekk linjer som starter med "15"
            # Fjern siste verdi etter komma
            line_content = ",".join(line.split(",")[:-1])  # Ignorer siste verdi etter komma
            line_dict[line_content].append(i + 1)  # Lagre linjeindeks (i+1 for menneskelig lesbarhet)

    # Finn duplikater
    for content, indices in line_dict.items():
        if len(indices) > 1:
            duplicates.append((content, indices))
    
    return duplicates

# Vis pop-up for duplikater
def show_duplicate_popup(duplicates):
    if not duplicates:
        messagebox.showinfo("Ingen duplikater", "Ingen duplikater funnet.")
        return
    
    duplicate_window = tk.Toplevel()
    duplicate_window.title("Duplikater funnet")
    
    label = tk.Label(duplicate_window, text=f"Antall duplikater funnet: {len(duplicates)}", font=("Arial", 12, "bold"))
    label.pack(pady=10)

    text_area = tk.Text(duplicate_window, wrap="word", width=80, height=20)
    text_area.pack(pady=10)
    
    # Legg til duplikatinfo i tekstområdet
    for content, indices in duplicates:
        text_area.insert(tk.END, f"Duplikat på linjer: {', '.join(map(str, indices))}\nInnhold: {content}\n\n")

    ok_button = tk.Button(duplicate_window, text="OK", command=duplicate_window.destroy, font=("Arial", 10, "bold"), bg="lightblue", fg="black")
    ok_button.pack(pady=10)

    duplicate_window.transient()  # Gjør pop-up modal
    duplicate_window.grab_set()
    duplicate_window.wait_window()

# Vis pop-up for måneder som er i filen
def show_month_popup(months):
    if not months:
        messagebox.showinfo("Ingen måneder funnet", "Ingen gyldige måneder funnet i filen.")
        return
    
    month_window = tk.Toplevel()  # Opprett et nytt Toplevel-vindu for månedslisten
    month_window.title("Eksisterende måneder i målfilen")
    
    label = tk.Label(month_window, text="Måneder i filen:", font=("Arial", 12, "bold"))
    label.pack(pady=10)

    listbox = tk.Listbox(month_window, font=("Arial", 10), width=20, height=10)
    for month in months:
        listbox.insert(tk.END, month)
    listbox.pack(pady=10)

    ok_button = tk.Button(month_window, text="OK", command=month_window.destroy, font=("Arial", 10, "bold"), bg="lightblue", fg="black")
    ok_button.pack(pady=10)

    month_window.transient()  # Gjør pop-up modal
    month_window.grab_set()
    month_window.wait_window()

def merge_txt_files():
    # Opprett en Tk-interaksjon
    root = tk.Tk()
    root.withdraw()  # Skjul hovedvinduet

    # Velg målfil som allerede inneholder data
    target_file = filedialog.askopenfilename(title="Velg .txt-fil som de andre skal slås sammen med", filetypes=[("Text files", "*.txt")])

    if not target_file:
        messagebox.showinfo("Ingen målfil valgt", "Ingen fil ble valgt for sammenslåing.")
        return

    # Brukerdefinert start og slutt dato for å filtrere måneder
    start_date = datetime.strptime("20240701", "%Y%m%d")
    end_date = datetime.strptime("20240801", "%Y%m%d")

    # Finn månedene som allerede finnes i målfilen innenfor angitt periode
    months_in_target_file = extract_filtered_months(target_file, start_date, end_date)

    if months_in_target_file:
        # Vis popup for å vise hvilke måneder som finnes
        show_month_popup(months_in_target_file)
    else:
        messagebox.showinfo("Ingen data", "Ingen måneder funnet i målfilen innenfor tidsperioden.")

    # Velg flere .txt-filer som skal slås sammen
    files_to_merge = filedialog.askopenfilenames(title="Velg .txt-filer som skal slås sammen", filetypes=[("Text files", "*.txt")])

    if not files_to_merge:
        messagebox.showinfo("Ingen filer valgt", "Ingen filer ble valgt.")
        return

    try:
        # Les innholdet av målfilen, ignorer feil med ukjente tegn
        merged_content = read_file_with_fallback(target_file)

        # Slå sammen innholdet fra alle valgte filer uten å legge til ekstra linjer
        for file in files_to_merge:
            file_content = read_file_with_fallback(file)
            merged_content.extend(file_content)  # Legg til linjene fra filene til det totale innholdet

        # Sjekk for duplikater i det totale innholdet
        duplicates = check_for_duplicates(merged_content)
        show_duplicate_popup(duplicates)

        # Hvis alt er ok, skriv det nye innholdet tilbake til målfilen
        with open(target_file, 'w', encoding='utf-8', errors='replace') as outfile:
            outfile.writelines(merged_content)

        messagebox.showinfo("Suksess", f"Filene ble vellykket slått sammen med {target_file}")

    except Exception as e:
        messagebox.showerror("Feil", f"Det oppstod en feil under sammenslåingen: {str(e)}")


if __name__ == "__main__":
    merge_txt_files()
