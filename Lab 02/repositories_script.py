import requests
import csv
from datetime import datetime
from github import Github

#
# Script para buscar os 1000 primeiros repositórios em Java e salvar no arquivo de dados
#

# Adicionar seu token do GitHub para acessar a API
github_pat = "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"
graphql_url = "https://api.github.com/graphql"
headers = {"Authorization": f"Bearer {github_pat}"}

query_template = """
{
    search(query: "stars:>100 language:Java", type: REPOSITORY, first: %d, after: %s) {
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
                primaryLanguage {
                    name
                }
                releases {
                    totalCount
                }
            }
        }
    }
}
"""

INCREMENT = 1
MAX_REPOSITORIES = 1000

def process_repository(repo, processed_urls):
    url = repo["url"]
    
    if url in processed_urls:
        return None
    
    processed_urls.add(url)

    name = repo["name"]
    stars = repo["stargazers"]["totalCount"]
    url = repo["url"]
    created_at = repo["createdAt"]
    primary_language = repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "N/A"
    releases = repo["releases"]["totalCount"]

    created_at_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.now()
    age_years = (current_date - created_at_date).days / 365
    age_years = round(age_years, 2)

    return [
        name, stars, url, age_years, primary_language, releases
    ]

query_counter = 0
repository_data = []

cursor = None
has_next_page = True

processed_urls = set()

with open("repository_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=';')
    csv_writer.writerow(["name", "stars", "url", "age_years", "primary_language", "releases"])
    
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
                if repo["primaryLanguage"]["name"] == "Java":
                    repo_data = process_repository(repo, processed_urls)
                    if repo_data:
                        csv_writer.writerow(repo_data)
                        query_counter += INCREMENT
        else:
            print("Request error:", response.text)
            break
