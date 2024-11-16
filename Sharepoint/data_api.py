from flask import Flask, jsonify
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

# Database tilkobling
engine = create_engine('DATABASE_CONNECTION_STRING')  # Bytt til din skybaserte database

@app.route('/data/<sheet_name>', methods=['GET'])
def get_data(sheet_name):
    df = pd.read_sql(f'SELECT * FROM {sheet_name}', engine)
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run()
