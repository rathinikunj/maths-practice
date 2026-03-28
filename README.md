# Maths Champions - Class 4

A Streamlit-based math practice app for Class 4 students, with timed worksheets, instant feedback, and a parent dashboard.

## Features

- Student practice mode with mixed worksheets
- Modules:
  - Fractions
  - Measurement
  - Perimeter & Area
  - Time
- Question types:
  - Multiple choice
  - True/False
  - Fill in the blank
- Live timer per worksheet
- Worksheet review after completion
- Parent dashboard (PIN-protected)
- Progress and score history tracking

## Tech Stack

- Python
- Streamlit
- Pandas
- SQLite (local file database)

## Project Structure

- `app.py` - Main Streamlit app
- `fractions_module.py` - Fractions worksheet generation
- `measurement_module.py` - Measurement worksheet generation
- `perimeter_area_module.py` - Perimeter & area worksheet generation
- `time_module.py` - Time worksheet generation
- `db.py` - SQLite score storage helpers
- `progress.py` - JSON progress persistence and badges
- `utils.py` - Timer helpers

## Setup

1. Clone the repo and move into it:

```bash
git clone <your-repo-url>
cd maths_app
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
streamlit run app.py
```

Open the local URL shown in terminal (usually `http://localhost:8501`).

## Configuration

Set parent dashboard PIN via environment variable (recommended):

```bash
export PARENT_DASHBOARD_PIN="your-strong-pin"
```

If not set, the app currently falls back to `1234`.

## Data Files

The app creates these local runtime files automatically:

- `scores.db` (SQLite score history)
- `progress.json` (worksheet progress and attempts)

These are intentionally ignored in `.gitignore` and should not be committed to a public repo.

## Notes for Deployment

- Ensure the deployment environment has write access to the app directory (or a mounted writable path), so local data files can be created.
- Set `PARENT_DASHBOARD_PIN` in your hosting platform secrets/environment settings.

## License

Add a license file before publishing (MIT is a good default for this project).
