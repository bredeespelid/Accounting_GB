from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File 
import io
import pandas as pd
from sqlalchemy import create_engine

# SharePoint URL og autentisering
url = 'https://company.sharepoint.com/Shared%20Documents/Folder/Target_Excel_File.xlsx'
username = 'Dumby_account@company.com'
password = 'Password!'

ctx_auth = AuthenticationContext(url)
if ctx_auth.acquire_token_for_user(username, password):
    ctx = ClientContext(url, ctx_auth)
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()
    print("Authentication successful")

response = File.open_binary(ctx, url)

# Lagre data til BytesIO stream
bytes_file_obj = io.BytesIO()
bytes_file_obj.write(response.content)
bytes_file_obj.seek(0) # Sett filobjektet til start

# Les Excel-filen til en pandas DataFrame
df = pd.read_excel(bytes_file_obj, sheet_name=None)

# Koble til den skybaserte databasen
engine = create_engine('DATABASE_CONNECTION_STRING')  # Bytt til din skybaserte database

# Lagre DataFrame til databasen
for sheet_name, sheet_data in df.items():
    sheet_data.to_sql(sheet_name, con=engine, if_exists='replace', index=False)
