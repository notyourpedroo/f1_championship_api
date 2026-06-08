from flask import Flask, jsonify
import pandas as pd
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

def get_csv_from_local(year, file_type):
    file_path = os.path.join("files", "raw", year, f"{file_type}.csv")
    print(f"Reading from: {file_path}")

    if not os.path.exists(file_path):
        return None, f"Arquivo não encontrado: {file_path}"

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return None, f"Erro ao ler o arquivo CSV: {str(e)}"

    return df, None


@app.route('/load/<year>/<file_type>', methods=['GET'])
def load_data(year, file_type):
    if file_type not in file_ids:
        return jsonify({"error": f"Arquivo '{file_type}' não encontrado."}), 400
    
    df, error = get_csv_from_local(year, file_type)
    
    if error:
        return jsonify({"error": error}), 500

    if file_type == 'races':
        df['race_date'] = pd.to_datetime(df['race_date'], dayfirst=True)

    return jsonify(df.to_dict(orient="records"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
