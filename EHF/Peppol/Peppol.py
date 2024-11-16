import requests
import pandas as pd
import re
from datetime import datetime
import os

# Base URL for the Peppol Directory API
base_url = "https://directory.peppol.eu/search/1.0/json"

# Query parameter to fetch participants for Norway
params = {
    'country': 'NO',  # Fetch all participants for Norway
}

# Definer en ordbok for å mappe dokumenttyper til mer lesbare navn
doc_type_mapping = {
    "urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2::ApplicationResponse##urn:fdc:peppol.eu:poacc:trns:catalogue_response:3::2.1": "Katalog Respons",
    "urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2::ApplicationResponse##urn:fdc:peppol.eu:poacc:trns:invoice_response:3::2.1": "Faktura Respons",
    "urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2::ApplicationResponse##urn:fdc:peppol.eu:poacc:trns:mlr:3::2.1": "Melding Nivå Respons",
    "urn:oasis:names:specification:ubl:schema:xsd:Catalogue-2::Catalogue##urn:fdc:peppol.eu:poacc:trns:catalogue:3::2.1": "Katalog",
    "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2::CreditNote##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1": "Kreditnota",
    "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1": "Faktura",
    "urn:oasis:names:specification:ubl:schema:xsd:Order-2::Order##urn:fdc:peppol.eu:poacc:trns:order:3::2.1": "Ordre",
    "urn:oasis:names:specification:ubl:schema:xsd:OrderResponse-2::OrderResponse##urn:fdc:peppol.eu:poacc:trns:order_response:3::2.1": "Ordre Respons",
    "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100::CrossIndustryInvoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::D16B": "CII Faktura"
}

# Send GET request
response = requests.get(base_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse JSON response
    data = response.json()

    # Create lists to hold the data for each column
    participant_ids = []
    names = []
    country_codes = []
    doc_types_list = []

    # Collect all unique document types across participants
    all_doc_types = set()

    # Iterate through the matches and extract participants' details
    for match in data.get('matches', []):
        participant_id = match.get('participantID', {}).get('value', 'N/A')
        
        # Check if the organisasjonsnummer has 9 digits
        if re.match(r'^\d{9}$', participant_id.split(':')[-1]):
            entities = match.get('entities', [])
            doc_types = match.get('docTypes', [])

            # Collect all document types for each participant with new names
            doc_types_entry = [f"{doc.get('scheme')} - {doc_type_mapping.get(doc.get('value'), doc.get('value'))}" for doc in doc_types]
            
            # Add to all_doc_types set
            all_doc_types.update(doc_types_entry)

            for entity in entities:
                name = entity.get('name', 'N/A')
                country = entity.get('countryCode', 'N/A')

                # Append the values to respective lists
                participant_ids.append(participant_id)
                names.append(name)
                country_codes.append(country)
                doc_types_list.append(doc_types_entry)

    # Create a DataFrame with the core details first
    df = pd.DataFrame({
        'Participant ID': participant_ids,
        'Bedriftsnavn': names,
        'Country Code': country_codes,
    })

    # Split 'Participant ID' column
    df[['icd', 'organisasjonsnummer']] = df['Participant ID'].str.split(':', expand=True)

    # Remove the original 'Participant ID' column
    df = df.drop('Participant ID', axis=1)

    # Move the new columns to the beginning of the DataFrame
    cols = df.columns.tolist()
    cols = ['icd', 'organisasjonsnummer'] + [col for col in cols if col not in ['icd', 'organisasjonsnummer']]
    df = df[cols]

    # Fix the 'Bedriftsnavn' column to remove list format
    df['Bedriftsnavn'] = df['Bedriftsnavn'].apply(lambda x: x[0]['name'] if isinstance(x, list) and len(x) > 0 and 'name' in x[0] else x)

    # Convert the set of all document types to a sorted list
    all_doc_types = sorted(list(all_doc_types))

    # Add columns dynamically for each unique document type with new names
    for doc_type in all_doc_types:
        new_name = doc_type.split(' - ')[1]  # Use the mapped name
        df[new_name] = ['Ja' if doc_type in doc_types else 'Nei' for doc_types in doc_types_list]

    # Display the first few rows of the DataFrame
    print(df.head())

    # Generate a filename with current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"peppol_participants_norway_{current_time}.csv"

    # Specify the full path for saving the file
    save_path = r"     xx      "
    full_path = os.path.join(save_path, filename)

    # Create the directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)

    # Save the DataFrame to a CSV file
    df.to_csv(full_path, index=False, encoding='utf-8-sig')
    print(f"Data has been saved to {full_path}")

else:
    print(f"Error: {response.status_code}, Message: {response.text}")
