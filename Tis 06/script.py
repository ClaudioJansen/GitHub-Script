import requests
import csv
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

token = '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'
headers = {'Authorization': f'token {token}'}
num_repositorios = 10  
repos_por_pagina = 1
num_paginas = num_repositorios // repos_por_pagina

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)

session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

def obter_etapa_falha(session, jobs_url, headers):
    response_jobs = session.get(jobs_url, headers=headers)

    # TODO retomar nesse ponto, validar se a etapa de falha de cada pipeline esta voltando certo (só mandar printar o run ali em baixo e ver qq pega)

    if response_jobs.status_code == 200:
        jobs_data = response_jobs.json()

        jobs = jobs_data.get('jobs', [])  

        if isinstance(jobs, list): 
            for job in jobs:
                if job['conclusion'] == 'failure':
                    return job.get('name', 'Desconhecido')
    return 'Desconhecido'

def obter_detalhes_falha(session, repo_name, headers):
    url_runs = f'https://api.github.com/repos/{repo_name}/actions/runs'
    response_runs = session.get(url_runs, headers=headers)

    falhas_totais = 0
    etapas_falha = []

    if response_runs.status_code == 200:
        runs = response_runs.json()['workflow_runs']

        for run in runs:
            if run['conclusion'] == 'failure':
                falhas_totais += 1
                jobs_url = run.get('jobs_url')
                etapa_falha = obter_etapa_falha(session, jobs_url, headers)
                etapas_falha.append(etapa_falha)

    return falhas_totais, etapas_falha

with open('dados_pipelines.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['nome_do_repositorio', 'linguagem', 'falhas_totais', 'etapa_falha'])

    for page_num in range(1, num_paginas + 1):
        try:
            url = f'https://api.github.com/search/repositories?q=stars:>1&s=stars&o=desc&page={page_num}&per_page={repos_por_pagina}'
            response = session.get(url, headers=headers)
        
            if response.status_code == 200:
                repositories = response.json()['items']

                for repo in repositories:
                    repo_name = repo['full_name']
                    repo_language = repo['language'] or 'Não especificado'

                    falhas_totais, etapas_falha = obter_detalhes_falha(session, repo_name, headers)

                    # TODO continuar buscando os dados que faltam

                    for etapa in etapas_falha:
                        writer.writerow([repo_name, repo_language, falhas_totais, etapa])

            else:
                print(f'Erro ao buscar repositórios na página {page_num}: {response.content}')
        
        except requests.exceptions.RequestException as e:
            print(f'Exceção capturada ao buscar repositórios na página {page_num}: {str(e)}')
            time.sleep(10)

session.close()
