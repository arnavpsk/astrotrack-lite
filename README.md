# AstroTrack Lite

A beginner-friendly Flask astronomy catalogue and CSV analysis demo with a dashboard, quiz, and curated space resources.

> **Data disclaimer:** `data/astronomy_catalogue.csv` contains synthetic demonstration records. Values are illustrative and are not verified scientific observations.

## Run on Windows
1. Install Python 3.11 or newer and Git (Git is only needed for GitHub).
2. Extract this folder and open it in VS Code.
3. In VS Code choose **Terminal → New Terminal** and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

4. Open `http://127.0.0.1:5000` in your browser. If PowerShell blocks activation, run `.venv\Scripts\python.exe -m pip install -r requirements.txt`, then `.venv\Scripts\python.exe app.py`.

## Tests
```powershell
python -m pytest -q
```

## Deploy
This Flask app can be deployed to a Python web host that supports Gunicorn. Set the start command to `gunicorn app:app`. Install dependencies from `requirements.txt`. Do not commit virtual environments or secret credentials. The built-in secret key is for a local student demo only; configure a strong environment-provided secret for a public production deployment.

## Main modules and routes
- `app.py`: Flask routes, catalogue loading, charts, CSV upload analysis, quiz and resource data.
- `data/astronomy_catalogue.csv`: 67 synthetic demonstration records.
- `templates/`: Jinja pages for dashboard, catalogue analysis, quiz and resources.
- `static/css/style.css`: responsive visual theme.
- `tests/test_app.py`: basic route, data, and upload validation tests.

## Interface contract
- `load_catalogue() -> pandas.DataFrame`: reads the catalogue CSV.
- `make_chart(series, kind='bar', xlabel='', ylabel='Count') -> str`: returns a base64-encoded PNG for embedding in a page.
- `GET /`: dashboard statistics and charts.
- `GET|POST /explore`: catalogue filtering and CSV analysis; uploaded CSV is limited to 5 MB and 10,000 rows are read.
- `GET /download`: downloads the sample catalogue as CSV.
- `GET|POST /quiz`: question and feedback flow.
- `GET /resources`: external ISRO and NASA resource cards.

## Limitations
The catalogue's measurements are synthetic. This is an educational demo, not a scientific database. Quiz state is a simple form flow and is not stored permanently. Uploaded files are analyzed in memory and are not retained on disk.
