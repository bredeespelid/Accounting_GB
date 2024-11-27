# Set environment variables and create openai client

import os
from openai import AzureOpenAI
from google.colab import userdata # To get the secret keys

# Deployment name in azure openai studio
gpt_model = "gpt-4o-mini"  # ex. gpt-4o-mini

client = AzureOpenAI(
    api_key=userdata.get('AZURE_OPENAI_API_KEY'),
    api_version="2023-03-15-preview",
    azure_endpoint=userdata.get('AZURE_OPENAI_ENDPOINT'),
)


import json
import pandas as pd
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam

# Load CSV file
file_path = "/content/Google_rating.csv"
data = pd.read_csv(file_path, quotechar='"', escapechar='\\', sep=',', encoding='utf-8')

# Fill missing comments and reset index
data["Kommentar"] = data["Kommentar"].fillna("Ingen kommentar")
data.reset_index(inplace=True)

# Set maximum batch size
batch_size = 10

# Function to convert batch to JSON
def batch_to_json(batch):
    return json.dumps(batch.to_dict(orient="records"), ensure_ascii=False)

# Function to validate and parse JSON response
def validate_json_response(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        print("Invalid JSON response:\n", response_text)
        return None

# Function to process a batch
def process_batch(batch):
    batch_json = batch_to_json(batch)
    system_message = (
        "You are an assistant trained to analyze customer feedback. "
        "Classify each review into categories, including 'Positiv tilbakemelding', 'Dyre produkter', "
        "'Dårlige produkter', 'Dårlig kundeservice/opplevelse', 'Lang kø/ventetid', 'Dårlig renhold', and 'Ingen kommentar'. "
        "Assign binary values (0 or 1) for each category for each review. Exclude the original comment but include the review's index."
    )
    user_message = (
        f"Analyze the following data in JSON format:\n{batch_json}\n\n"
        "Output must include:\n"
        "{\n"
        "    \"departments\": {\n"
        "        \"<Avd>\": [\n"
        "            {\n"
        "                \"index\": <original_index>,\n"
        "                \"Dato\": \"<date>\",\n"
        "                \"★\": <star_rating>,\n"
        "                \"categories\": {\n"
        "                    \"Positiv tilbakemelding\": <0_or_1>,\n"
        "                    \"Dyre produkter\": <0_or_1>,\n"
        "                    \"Dårlige produkter\": <0_or_1>,\n"
        "                    \"Dårlig kundeservice/opplevelse\": <0_or_1>,\n"
        "                    \"Lang kø/ventetid\": <0_or_1>,\n"
        "                    \"Dårlig renhold\": <0_or_1>,\n"
        "                    \"Ingen kommentar\": <0_or_1>\n"
        "                }\n"
        "            },\n"
        "            ...\n"
        "        ]\n"
        "    }\n"
        "}"
    )
    
    messages = [
        ChatCompletionSystemMessageParam(role="system", content=system_message),
        ChatCompletionUserMessageParam(role="user", content=user_message),
    ]

    try:
        # Send the request to the model
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        response_text = completion.choices[0].message.content
        return validate_json_response(response_text)
    except Exception as e:
        print(f"Error processing batch: {e}")
        return None

# Function to split and retry failed batches
def retry_failed_batch(batch):
    if len(batch) == 1:
        print("Skipping single review due to persistent failure.")
        return []
    mid = len(batch) // 2
    return process_batches([batch[:mid], batch[mid:]])

# Function to process all batches
def process_batches(batches):
    results = []
    for batch in batches:
        result = process_batch(batch)
        if result:
            results.append(result)
        else:
            print("Retrying failed batch with smaller size...")
            smaller_results = retry_failed_batch(batch)
            results.extend(smaller_results)
    return results

# Split data into batches
batches = [data[i:i+batch_size] for i in range(0, len(data), batch_size)]

# Process all batches with retries
final_results = process_batches(batches)

# Combine results into final output
final_output = {"departments": {}}
for batch_result in final_results:
    for dept, comments in batch_result["departments"].items():
        if dept not in final_output["departments"]:
            final_output["departments"][dept] = []
        final_output["departments"][dept].extend(comments)

# Print final result
print(json.dumps(final_output, indent=4))
