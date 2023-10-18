import requests
import csv
import time
from datetime import datetime

graphql_url = "https://api.github.com/graphql"
headers = {
    "Authorization": "Bearer your_token"
}

INCREMENT = 20
MAX_REPOSITORIES = 200
RETRY_DELAYS = [5, 10, 20]  

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

def execute_query(query):
    """Executa a consulta, gerenciando tentativas e erros."""
    for delay in RETRY_DELAYS:
        try:
            response = requests.post(graphql_url, json={'query': query}, headers=headers)
            response.raise_for_status()  
            return response.json()
        except requests.RequestException as e:
            print(f"Erro: {e}. Nova tentativa em {delay} segundos.")
            time.sleep(delay)
    return None

def parse_date(date_string):
    """Analisa uma string de data, retornando um objeto datetime ou None em caso de falha."""
    try:
        return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
    except (ValueError, TypeError):
        return None

def main():
    """Função principal do script."""
    filtered_repos = []
    seen_repos = set()

    cursor = None 
    has_next_page = True

    while has_next_page and len(filtered_repos) < MAX_REPOSITORIES:
        query = query_template % (INCREMENT, f'"{cursor}"' if cursor else "null")
        data = execute_query(query)

        if data is None:
            print("Falha após várias tentativas; encerrando.")
            break

        try:
            search_data = data["data"]["search"]
            repositories = search_data["nodes"]
            has_next_page = search_data["pageInfo"]["hasNextPage"]
            cursor = search_data["pageInfo"]["endCursor"]

            for repo in repositories:
                repo_name = repo.get('name')
                repo_url = repo.get('url')

                if repo_name in seen_repos:
                    continue  

                prs = repo.get('pullRequests', {}).get('nodes', [])

                for pr in prs:
                    reviews = pr.get('reviews', {}).get('totalCount', 0)

                    if reviews > 0:
                        filtered_repos.append([repo_name, repo_url])
                        seen_repos.add(repo_name)
                        break  

        except KeyError as e:
            print(f"Chave inesperada nos dados: {e}; encerrando.")
            break

        print(f"Progresso: {len(filtered_repos)} repositórios filtrados.")

    with open('filtered_repos.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['repository_name', 'repository_url'])
        writer.writerows(filtered_repos)

    print("Script concluído. Repositórios filtrados escritos em 'filtered_repos.csv'.")

if __name__ == "__main__":
    main()
