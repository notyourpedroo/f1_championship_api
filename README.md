# F1 Championship API

A lightweight REST API built with Flask that provides dynamic access to Formula 1 championship data stored in Google Sheets. This project demonstrates how to integrate external spreadsheet data as a data source for a web service.

## 🚀 Features

The API provides endpoints to retrieve data from various championship categories. All data is fetched in real-time from Google Sheets and returned in JSON format.

### Endpoints

| Endpoint | Description | Example Response |
| :--- | :--- | :--- |
| `/load/races` | Race information (Date, Grand Prix, Circuit) | `[{"race_date": "2024-03-02", "grand_prix": "Bahrain GP", ...}]` |
| `/load/drivers` | Driver profiles and information | `[{"driver_name": "Max Verstappen", "nationality": "Dutch", ...}]` |
| `/load/results` | Race results and finishing positions | `[{"race": "Bahrain GP", "driver": "Max Verstappen", "position": 1, ...}]` |
| `/load/teams` | Team details and constructors | `[{"team_name": "Red Bull Racing", "base": "Milton Keynes", ...}]` |
| `/load/scores` | Points attribution per position | `[{"position": 1, "points": 25}, ...]` |

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.x**
- **pip** (Python package manager)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/notyourpedroo/f1_championship_api.git
   cd f1_championship_api
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory to store the Google Sheets IDs:
   ```env
   RACES_ID=your_races_file_id
   DRIVERS_ID=your_drivers_file_id
   RESULTS_ID=your_results_file_id
   TEAMS_ID=your_teams_file_id
   SCORES_ID=your_scores_file_id
   ```
   *Note: You can find the file ID in the URL of your Google Sheet: `docs.google.com/spreadsheets/d/[FILE_ID]/edit`.*

## 🏃 Running the Project

Start the Flask server:
```bash
python app.py
```
The server will be available at `http://127.0.0.1:5000/`.

### Usage Example
To get the drivers' data, simply access:
`GET http://127.0.0.1:5000/load/drivers`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the MIT License.
