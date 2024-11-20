import os
import xml.etree.ElementTree as ET

# Definer ny tekst for <cbc:Note>
new_note_text = "Note."

# Mappe som inneholder XML-filene
xml_directory = r"path"  # Endret til riktig sti

# Iterer gjennom alle filer i mappen
for filename in os.listdir(xml_directory):
    if filename.endswith(".xml"):  # Sjekk om filen er en XML-fil
        file_path = os.path.join(xml_directory, filename)
        
        # Parse XML-filen
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Finn den første <cbc:Note>-elementet
            note = root.find(".//cbc:Note", namespaces={'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            if note is not None:
                # Endre tekst i den første <cbc:Note>
                note.text = new_note_text
                print(f"Oppdatert første <cbc:Note> i {filename}")
            
            # Lagre endringene tilbake til filen
            tree.write(file_path, encoding="utf-8", xml_declaration=True)
        
        except ET.ParseError as e:
            print(f"Kunne ikke parse {filename}: {e}")
        except Exception as e:
            print(f"En feil oppstod med {filename}: {e}")

print("Ferdig med oppdatering av filer.")
