import requests
import csv
import time
from datetime import datetime


GITHUB_TOKEN = "your_token"
GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
CSV_FILE = 'filtered_repos.csv'
OUTPUT_FILE = 'pr_details.csv'
SLEEP_INTERVAL = 5  


PR_DETAILS_QUERY = """
query($owner: String!, $name: String!, $prCount: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: $prCount, after: $cursor) {
      edges {
        node {
          files {
            totalCount
          }
          additions
          deletions
          createdAt
          closedAt
          body
          participants {
            totalCount
          }
          comments {
            totalCount
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

def send_query(query, variables):
    try:
        response = requests.post(GRAPHQL_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar consulta: {e}")
        return None

def process_repository(repo_owner, repo_name, writer):
    cursor = None
    hasNextPage = True

    while hasNextPage:
        variables = {
            "owner": repo_owner,
            "name": repo_name,
            "prCount": 100, 
            "cursor": cursor
        }

        data = send_query(PR_DETAILS_QUERY, variables)
        if not data:
            break

        repository = data.get("data", {}).get("repository", {})
        pullRequests = repository.get("pullRequests", {})

        for edge in pullRequests.get("edges", []):
            pr = edge["node"]

            createdAt = datetime.strptime(pr["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
            closedAt = datetime.strptime(pr["closedAt"], '%Y-%m-%dT%H:%M:%SZ') if pr["closedAt"] else datetime.utcnow()
            review_time = (closedAt - createdAt).total_seconds()

            writer.writerow([
                f"{repo_owner}/{repo_name}",
                pr["files"]["totalCount"],
                pr["additions"],
                pr["deletions"],
                review_time,
                len(pr["body"]),
                pr["participants"]["totalCount"],
                pr["comments"]["totalCount"]
            ])

        pageInfo = pullRequests.get("pageInfo", {})
        cursor = pageInfo.get("endCursor")
        hasNextPage = pageInfo.get("hasNextPage", False)

        time.sleep(SLEEP_INTERVAL)  

def main():
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(["repositorio", "arquivos", "adicoes", "remocoes", "tempo_analise_segundos", "descricao_tamanho", "participantes", "comentarios"])

        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter=';')
            next(reader, None)  
            for row in reader:
                repo_url = row[1]
                owner, name = repo_url.strip().split('/')[-2:]
                print(f"Processando repositório: {owner}/{name}")

                try:
                    process_repository(owner, name, writer)
                    outfile.flush()  
                except Exception as e:
                    print(f"Erro ao processar {owner}/{name}: {e}")

    print(f"Script concluído. Detalhes dos PRs escritos em '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
