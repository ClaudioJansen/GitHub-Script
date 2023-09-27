import requests

token = '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'

params = {
    'q': 'language:java',
    'sort': 'stars',
    'order': 'desc',
    'per_page': 10,
}

url = 'https://api.github.com/search/repositories'

pipelines_info = []

def get_pipeline_info(owner, repo):
    pipeline_url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows'
    headers = {'Authorization': f'token {token}'}
    response = requests.get(pipeline_url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except ValueError:
            pass 
    return None

for page in range(1, 2):
    params['page'] = page
    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            if 'items' in data and isinstance(data['items'], list):
                for repo in data['items']:
                    owner = repo['owner']['login']
                    repo_name = repo['name']
                    pipelines = get_pipeline_info(owner, repo_name)
                    if pipelines:
                        pipelines_info.append({'repo': repo_name, 'owner': owner, 'pipelines': pipelines})
        except ValueError:
            pass 

for repo_info in pipelines_info:
    print(f"Repositório: {repo_info['owner']}/{repo_info['repo']}")
    print(f"Total de pipelines: {repo_info['pipelines']['total_count']}")
    for workflow in repo_info['pipelines']['workflows']:
        print(f"Nome da Pipeline: {workflow['name']}")
        print(f"ID da Workflow: {workflow['id']}")
        print(f"Estado: {workflow['state']}")
        print(f"Link para a Pipeline: {workflow['html_url']}")
        print('-' * 40)
        
       