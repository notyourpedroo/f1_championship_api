from flask import Flask, jsonify
import requests
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

file_ids = {
    "races": os.getenv("RACES_ID"),
    "drivers": os.getenv("DRIVERS_ID"),
    "results": os.getenv("RESULTS_ID"),
    "teams": os.getenv("TEAMS_ID"),
    "scores": os.getenv("SCORES_ID")
}

def get_xlsx_from_drive(file_id):
    url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
    print(f"Downloading from: {url}")

    response = requests.get(url)

    if response.status_code != 200:
        return None, f"Erro ao baixar o arquivo: {response.status_code}"

    try:
        xlsx_data = BytesIO(response.content)
        df = pd.read_excel(xlsx_data, engine="openpyxl")
    except Exception as e:
        return None, f"Erro ao ler o arquivo XLSX: {str(e)}"

    return df, None


@app.route('/load/<file_type>', methods=['GET'])
def load_data(file_type):
    if file_type not in file_ids:
        return jsonify({"error": f"Arquivo '{file_type}' não encontrado."}), 400
    
    file_id = file_ids[file_type]
    df, error = get_xlsx_from_drive(file_id)
    
    if error:
        return jsonify({"error": error}), 500

    if file_type == 'races':
        df['race_date'] = pd.to_datetime(df['race_date'], dayfirst=True)

    return jsonify(df.to_dict(orient="records"))


if __name__ == '__main__':
    app.run(debug=False)
