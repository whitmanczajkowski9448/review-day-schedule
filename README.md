# Senior CERT / PSAT Review Day | Student Schedule Lookup

Streamlit student schedule lookup for September 28, 2026.

## Run locally

```cmd
py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

Upload these files to the root of the GitHub repository:

- `app.py`
- `students.json`
- `requirements.txt`
- `.streamlit/config.toml`

Then point Streamlit Community Cloud at `app.py`.

## Optional access code

In Streamlit Cloud Secrets, you can add:

```toml
ACCESS_CODE = "your-code-here"
```

If no `ACCESS_CODE` is configured, the app opens directly to the student-name search.

## Search behavior

The student picker is a searchable Streamlit select box. Students click the box and begin typing their first name, last name, or full name; the matching list filters as they type. Selecting a name immediately loads the schedule.
