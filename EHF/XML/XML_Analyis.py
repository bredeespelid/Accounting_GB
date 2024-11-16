import xml.etree.ElementTree as ET
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Liste for å holde data
    data = []

    # Variabler for å lagre spesifikke verdier
    tax_amounts = []
    tax_inclusive_amount = None

    # Iterer gjennom alle elementer og legg til data hvis det er en tallverdi
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'CompanyID':
            # Sjekk lengde på CompanyID
            if elem.text and len(elem.text) == 9:
                data.append([tag, elem.text])
        elif tag == 'TaxAmount' and len(tax_amounts) < 3:
            try:
                # Prøv å konvertere til float og lagre de tre første verdiene av TaxAmount
                value = float(elem.text)
                tax_amounts.append(value)
            except (TypeError, ValueError):
                continue
        elif tag == 'TaxInclusiveAmount' and tax_inclusive_amount is None:
            try:
                # Finn første forekomst av TaxInclusiveAmount
                tax_inclusive_amount = float(elem.text)
            except (TypeError, ValueError):
                continue
        else:
            try:
                # Sjekk om verdien er en float eller int
                value = float(elem.text)
                data.append([tag, value])
            except (TypeError, ValueError):
                continue

    # Lag en DataFrame fra data-listen
    df = pd.DataFrame(data, columns=['Tag', 'Value'])

    # Finn alle unike CompanyID-verdier og sjekk lengden deres
    company_ids = df[df['Tag'] == 'CompanyID']['Value'].unique()
    company_id_lengths_ok = all(len(cid) == 9 for cid in company_ids)

    # Lag en rapport basert på de funne dataene
    report = ""
    if company_id_lengths_ok:
        report += "Lengde org_nr -> GOOD\n"
        report += "\n"
    else:
        report += "Lengde org_nr-> NOT GOOD\n"
        report += "\n"

    try:
        # Finn radindeksen for den første forekomsten av ID med verdi 1
        start_index = df[(df['Tag'] == 'ID') & (df['Value'] == 1)].index[0]

        # Filtrer DataFrame for å starte fra start_index
        filtered_df = df.iloc[start_index:]

        # Filtrer ut verdiene med tag 'LineExtensionAmount' og beregn summen
        line_extension_amount_sum = filtered_df[filtered_df['Tag'] == 'LineExtensionAmount']['Value'].sum()

        # Filtrer ut verdiene med tag 'TaxableAmount' og beregn summen
        taxable_amount_sum = df[df['Tag'] == 'TaxableAmount']['Value'].sum()

        # Filtrer ut verdiene med tag 'TaxExclusiveAmount' og beregn summen
        tax_exclusive_amount_sum = df[df['Tag'] == 'TaxExclusiveAmount']['Value'].sum()

        report += f"-> TaxExclusiveAmount: {tax_exclusive_amount_sum:.2f}\n"

        # Skriv ut den første TaxAmount-verdien hvis den er funnet
        
        if len(tax_amounts) >= 1:
            first_tax_amount = tax_amounts[0]
            report += f"-> Første TaxAmount-verdien: {first_tax_amount:.2f}\n"

            # Beregn og skriv ut summen av taxable_amount_sum og tax_amounts[0]
            total_sum = taxable_amount_sum + first_tax_amount

        # Skriv ut summen av de to neste TaxAmount-verdiene hvis de finnes
        if len(tax_amounts) >= 3:
            sum_of_next_two_tax_amounts = tax_amounts[1] + tax_amounts[2]

        report += f"\n∑ LineExtensionAmount: {line_extension_amount_sum:.2f}\n"
        report += f"+\n∑ TaxAmount-verdiene: {sum_of_next_two_tax_amounts:.2f}\n"
        report += f"=\n∑ TaxAmount-verdiene & LineExtensionAmount: {sum_of_next_two_tax_amounts+line_extension_amount_sum:.2f}\n"
        report += "==\n"
        if tax_inclusive_amount is not None:
            report += f"TaxInclusiveAmount: {tax_inclusive_amount:.2f}\n"
        else:
            report += "Ingen TaxInclusiveAmount-verdier funnet.\n"
    except IndexError:
        report += "Fant ikke start ID med verdi 1.\n"

    # Finn den første ID-verdien for å bruke som navn på popup-vindu
    first_id_value = df[df['Tag'] == 'ID']['Value'].iloc[0] if not df[df['Tag'] == 'ID'].empty else "Ingen ID funnet"

    return str(first_id_value), report

# Opprett et hovedvindu for filvalg
root = tk.Tk()
root.withdraw()  # Skjul hovedvinduet

# Åpne filvelger for å velge en eller flere XML-filer
file_paths = filedialog.askopenfilenames(title="Velg en eller flere XML-filer", filetypes=[("XML Files", "*.xml")])

# Behandle hver valgt fil
for file_path in file_paths:
    id_value, report = parse_xml(file_path)

    # Vis rapporten i et popup-vindu
    messagebox.showinfo(title=id_value, message=report)

# Avslutt hovedloopen etter at alle filer er behandlet
root.destroy()
