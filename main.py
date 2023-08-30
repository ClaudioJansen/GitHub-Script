import requests
import csv
from datetime import datetime

graphql_url = "https://api.github.com/graphql"
headers = {"Authorization": "Bearer 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"}

query_template = """
{
    search(query: "stars:>100", type: REPOSITORY, first: %d, after: %s) {
        pageInfo {
            hasNextPage
            endCursor
        }
        nodes {
            ... on Repository {
                name
                stargazers { totalCount }
                url
                createdAt
                updatedAt
                primaryLanguage {
                    name
                }
                pullRequests(states: [OPEN, CLOSED, MERGED]) {
                    totalCount
                }
                releases {
                    totalCount
                }
                issues {
                    totalCount
                }
            }
        }
    }
}
"""

INCREMENT = 5
MAX_REPOSITORIES = 50

def process_repository(repo):
    name = repo["name"]
    stars = repo["stargazers"]["totalCount"]
    url = repo["url"]
    created_at = repo["createdAt"]
    pull_requests = repo["pullRequests"]["totalCount"]
    releases = repo["releases"]["totalCount"]
    updated_at = repo["updatedAt"]
    primary_language = repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "N/A"
    total_issues = repo["issues"]["totalCount"]
    closed_issues = repo["issues"].get("closed", 0)
    issues_ratio = closed_issues / total_issues if total_issues > 0 else 0

    created_at_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.now()
    age_years = (current_date - created_at_date).days / 365
    last_updated_date = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
    time_since_last_update = (current_date - last_updated_date).days

    return [
        name, stars, url, age_years, pull_requests, releases,
        time_since_last_update, primary_language, closed_issues,
        total_issues, issues_ratio
    ]

query_counter = 0

cursor = None
has_next_page = True

with open("repository_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=";")
    
    header = [
        "Name", "Stars", "URL", "Years", "Total Pull Requests", "Total Releases",
        "Days Since Last Update", "Primary Language", "Closed Issues",
        "Total Issues", "Issues Ratio (Closed/Total)"
    ]
    csv_writer.writerow(header)
    
    while has_next_page and query_counter < MAX_REPOSITORIES:
        query = query_template % (INCREMENT, f'"{cursor}"' if cursor else "null")
        response = requests.post(graphql_url, json={"query": query}, headers=headers)

        if response.status_code == 200:
            data = response.json()
            search_data = data.get("data", {}).get("search", {})
            repositories = search_data.get("nodes", [])
            cursor = search_data["pageInfo"]["endCursor"]
            has_next_page = search_data["pageInfo"]["hasNextPage"]

            for repo in repositories:
                repo_data = process_repository(repo)
                csv_writer.writerow(repo_data)

            query_counter += INCREMENT
        else:
            print("Request error:", response.text)
            break