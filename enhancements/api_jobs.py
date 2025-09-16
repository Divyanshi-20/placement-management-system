# enhancements/api_jobs.py
import os, traceback, requests

def fetch_api_jobs(query=None, location=None, max_results=5):
    """
    Fetch jobs from Adzuna (if configured). Returns list of job dicts.
    """
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    country = os.environ.get("ADZUNA_COUNTRY", "in")

    if not app_id or not app_key:
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": query or "",
        "where": location or "",
        "results_per_page": max_results
    }
    try:
        resp = requests.get(url, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        jobs = []
        for job in data.get("results", []):
            company = (job.get("company") or {}).get("display_name", "Unknown")
            jobs.append({
                "company": company,
                "role": job.get("title"),
                "location": (job.get("location") or {}).get("display_name", ""),
                "description": (job.get("description") or "")[:300],
                "link": job.get("redirect_url") or "",
                "id": "api-" + str(job.get("id"))
            })
        return jobs
    except Exception as e:
        print("⚠️ API fetch error:", e)
        traceback.print_exc()
        return []
