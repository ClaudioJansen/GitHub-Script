import requests
import csv
from datetime import datetime

graphql_url = "https://api.github.com/graphql"
headers = {"Authorization": "Bearer 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"}

INCREMENT = 20
MAX_REPOSITORIES = 200

query_template = """
{
    search(query: "is:public", type: REPOSITORY, first: %d, after: %s) {
        pageInfo {
            hasNextPage
            endCursor
        }
        nodes {
            ... on Repository {
                name
                url
                pullRequests(states: [MERGED, CLOSED], first: 100) {
                    totalCount
                    nodes {
                        createdAt
                        closedAt
                        reviews(first: 1) {
                            totalCount
                            nodes {
                                createdAt
                            }
                        }
                    }
                }
            }
        }
    }
}
"""

filtered_repos = []
seen_repos = set()

query_counter = 0

cursor = None
has_next_page = True

while has_next_page and len(filtered_repos) < MAX_REPOSITORIES:
    query = query_template % (INCREMENT, f'"{cursor}"' if cursor else "null")
    response = requests.post(graphql_url, json={"query": query}, headers=headers)

    print(len(filtered_repos))
    
    if response.status_code == 200:
        data = response.json()
        search_data = data.get("data", {}).get("search", {})
        repositories = search_data.get("nodes", [])
        cursor = search_data["pageInfo"]["endCursor"]
        has_next_page = search_data["pageInfo"]["hasNextPage"]

        for repo in repositories:
            repo_name = repo['name']
            repo_url = repo['url']
            if repo_name not in seen_repos:
                prs = repo['pullRequests']['nodes']
                for pr in prs:
                    created_at = datetime.strptime(pr['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
                    closed_at = datetime.strptime(pr['closedAt'], '%Y-%m-%dT%H:%M:%SZ')
                    time_diff = closed_at - created_at
                    if pr['reviews']['totalCount'] > 0 and time_diff.total_seconds() > 3600:
                        filtered_repos.append([repo_name, repo_url])
                        seen_repos.add(repo_name)
                        break
    
    else:
        print("Request error:", response.text)
        break

with open('filtered_repos.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['repository_name', 'repository_url'])
    writer.writerows(filtered_repos)
