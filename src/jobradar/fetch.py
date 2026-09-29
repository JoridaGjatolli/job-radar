# Write a script that fetches postings from one job API, 
# handles errors, timeouts, and pagination, and saves the results 
# to a JSON file. Use Pydantic models to validate each posting.

import httpx
import json
from pydantic import BaseModel, ValidationError
from datetime import datetime
from pathlib import Path

API_URL = "https://www.arbeitnow.com/api/job-board-api"

class JobPosting(BaseModel):
    slug: str
    title: str
    company_name: str
    location: str = ""
    remote: bool = False
    url: str
    tags: list[str] = []
    created_at: datetime

def fetch_page(page:int) -> dict:
    response = httpx.get(API_URL, params = {"page": page},timeout=10)
    response.raise_for_status()
    return response.json()

def fetch_jobs(max_pages: int = 3) -> list[JobPosting]:
    jobs= []

    for page in range(1, max_pages + 1):
        data = fetch_page(page)

        for job in data["data"]:
            try:
                jobs.append(JobPosting.model_validate(job))
            except ValidationError:
                print("Job validation failed for job:", job.get("slug"))

        if not data["links"]["next"]:
            break

    return jobs

if __name__ == "__main__":
    try:
        jobs = fetch_jobs(4)
    except httpx.HTTPError as error:
        print(f"Could not fetch jobs: {error}")
        exit(1)
 
    Path("data").mkdir(exist_ok=True)
    with open("data/jobs.json", "w", encoding="utf-8") as file:
        json.dump([job.model_dump(mode="json") for job in jobs], file, indent=2)
 
    print(f"Saved {len(jobs)} jobs to data/jobs.json")