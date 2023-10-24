import requests
import csv
import time
import datetime
import re
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

token = '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'
headers = {'Authorization': f'token {token}'}
total_repositorios = 0
repositorios_com_falha = 0
page_num = 1
num_repositorios = 1000
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

    if response_jobs.status_code == 200:
        jobs_data = response_jobs.json()

        jobs = jobs_data.get('jobs', [])  

        if isinstance(jobs, list): 
            for job in jobs:
                if job['conclusion'] == 'failure':
                    return job.get('name', 'Desconhecido')
    return 'Desconhecido'

def obter_estatisticas_linhas(session, headers, repo_name, commit_id):
    commit_url = f"https://api.github.com/repos/{repo_name}/commits/{commit_id}"
    response = session.get(commit_url, headers=headers)

    if response.status_code == 200:
        stats = response.json().get('stats', {})
        return stats.get('additions', 0), stats.get('deletions', 0)

    return 0, 0

def obter_tempo_correcao(runs, indice_falha):
    if indice_falha < 0 or indice_falha >= len(runs):
        return None

    formato_data = "%Y-%m-%dT%H:%M:%SZ" 
    run_falha = runs[indice_falha]

    data_inicio_falha = run_falha.get('run_started_at')
    if data_inicio_falha:
        inicio_falha = datetime.strptime(data_inicio_falha, formato_data)
    else:
        return None 

    for i in range(indice_falha + 1, len(runs)):
        run_atual = runs[i]
        if run_atual['conclusion'] == 'success':
            data_inicio_sucesso = run_atual.get('run_started_at')
            if data_inicio_sucesso:
                inicio_sucesso = datetime.strptime(data_inicio_sucesso, formato_data)
                tempos_correcao = inicio_sucesso - inicio_falha
                return tempos_correcao.total_seconds()

    return None


def obter_detalhes_falha(session, repo_name, headers):
    url_runs = f'https://api.github.com/repos/{repo_name}/actions/runs'
    response_runs = session.get(url_runs, headers=headers)

    total_pipelines = 0
    falhas_totais = 0
    falhas_build = 0
    falhas_teste = 0
    falhas_lint = 0
    falhas_deploy = 0
    linhas_adicionadas_list = []
    linhas_removidas_list = []
    tempos_correcao = []
    etapas_falha = []

    if response_runs.status_code == 200:
        runs = response_runs.json()['workflow_runs']

        total_pipelines = len(runs)

        with open('save.csv', mode='w', newline='', encoding='utf-8') as filee:
            writer = csv.writer(filee)
            writer.writerow([runs])

        for indice, run in enumerate(runs):
            if run['conclusion'] == 'failure':
                falhas_totais += 1
                jobs_url = run.get('jobs_url')
                etapa_falha = obter_etapa_falha(session, jobs_url, headers)
                etapas_falha.append(etapa_falha)
                tempo_correcao = obter_tempo_correcao(runs, indice)

                if tempo_correcao is not None:  
                    tempos_correcao.append(tempo_correcao) 

                    if 'head_commit' in run and 'id' in run['head_commit']:
                        commit_id = run['head_commit']['id']
                        linhas_adicionadas, linhas_removidas = obter_estatisticas_linhas(session, headers, repo_name, commit_id)

                        linhas_adicionadas_list.append(linhas_adicionadas)
                        linhas_removidas_list.append(linhas_removidas)

                response_jobs = session.get(jobs_url, headers=headers)
                if response_jobs.status_code == 200:
                    jobs = response_jobs.json().get('jobs', [])
                    for job in jobs:
                        if job['conclusion'] == 'failure':
                            job_name_lower = job.get('name', '').lower()
                            if 'build' in job_name_lower:
                                falhas_build += 1
                            elif 'test' in job_name_lower:
                                falhas_teste += 1
                            elif 'lint' in job_name_lower:
                                falhas_lint += 1
                            elif 'deploy' in job_name_lower:
                                falhas_deploy += 1
    
    if falhas_totais == 0: 
        return None

    percentual_falha = (falhas_totais / total_pipelines) * 100 if total_pipelines > 0 else 0

    if falhas_totais == 0:
        return None

    return falhas_totais, etapas_falha, falhas_build, falhas_teste, falhas_lint, falhas_deploy, total_pipelines, percentual_falha, tempos_correcao, linhas_adicionadas_list, linhas_removidas_list

with open('dados_pipelines.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['nome_do_repositorio', 'linguagem', 'falhas_totais', 'etapas_falha', 'falhas_build', 'falhas_teste', 'falhas_lint', 'falhas_deploy', 'total_pipelines', 'percentual_falha', 'linhas_adicionadas', 'linhas_removidas'])
    
    while repositorios_com_falha < num_repositorios:
        total_repositorios += 1
        try:
            url = f'https://api.github.com/search/repositories?q=stars:>1&s=stars&o=desc&page={page_num}&per_page={repos_por_pagina}'
            response = session.get(url, headers=headers)

            if response.status_code == 200:
                repositories = response.json()['items']

                for repo in repositories:
                    repo_name = repo['full_name']
                    print("Lendo repositório " + repo_name)
                    detalhes_falha = obter_detalhes_falha(session, repo_name, headers)

                    if detalhes_falha is not None:  
                        repositorios_com_falha += 1  
                        falhas_totais, etapas_falha, falhas_build, falhas_teste, falhas_lint, falhas_deploy, total_pipelines, percentual_falha, tempos_correcao, linhas_adicionadas, linhas_removidas = detalhes_falha

                        writer.writerow([repo_name, repo['language'] or 'Não especificado', falhas_totais, etapas_falha, falhas_build, falhas_teste, falhas_lint, falhas_deploy, total_pipelines, f"{percentual_falha:.2f}%", tempos_correcao, linhas_adicionadas, linhas_removidas])

                    if repositorios_com_falha >= num_repositorios:
                        break
            else:
                print(f'Erro ao buscar repositórios na página {page_num}: {response.content}')
        
        except requests.exceptions.RequestException as e:
            print(f'Exceção capturada ao buscar repositórios na página {page_num}: {str(e)}')
            time.sleep(10)

        page_num += 1

    writer.writerow('Total de repositórios lidos: ', total_repositorios)


session.close()
