import os
import xml.etree.ElementTree as ET

# Mappe som inneholder XML-filene
xml_directory = r"path"

# Initialiser total sum
total_sum = 0.0

# Iterer gjennom alle filer i mappen
for filename in os.listdir(xml_directory):
    if filename.endswith(".xml"):  # Sjekk om filen er en XML-fil
        file_path = os.path.join(xml_directory, filename)
        
        # Parse XML-filen
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Finn alle <ns1:PayableAmount> med currencyID="NOK"
            payable_elements = root.findall(".//ns1:PayableAmount[@currencyID='NOK']", 
                                            namespaces={'ns1': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            
            # Summer verdiene
            for element in payable_elements:
                try:
                    amount = float(element.text)
                    total_sum += amount
                except ValueError:
                    print(f"Ugyldig verdi i {filename}: {element.text}")
            
        except ET.ParseError as e:
            print(f"Kunne ikke parse {filename}: {e}")
        except Exception as e:
            print(f"En feil oppstod med {filename}: {e}")

# Print total summen
print(f"Total sum av alle <ns1:PayableAmount currencyID='NOK'> er: {total_sum:.2f} NOK")
