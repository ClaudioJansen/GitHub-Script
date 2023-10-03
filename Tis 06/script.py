import requests
import csv
from datetime import datetime

# Adicionar token
token = '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'

params = {
    'q': 'language:java',
    'sort': 'stars',
    'order': 'desc',
    'per_page': 100,
}

url = 'https://api.github.com/search/repositories'
headers = {'Authorization': f'token {token}'}

pipelines_info = []

def get_pipeline_info(owner, repo):
    pipeline_url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows'
    response = requests.get(pipeline_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_failed_runs(owner, repo, workflow_id):
    runs_url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs'
    response = requests.get(runs_url, headers=headers)
    if response.status_code == 200:
        runs_data = response.json()
        return [run for run in runs_data['workflow_runs'] if run['conclusion'] == 'failure']
    return []

def get_time_to_fix(owner, repo, workflow_id, failed_run_id):
    runs_url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs'
    response = requests.get(runs_url, headers=headers)
    if response.status_code == 200:
        runs_data = response.json()
        found_error = False
        error_time = None
        for run in runs_data['workflow_runs']:
            if run['id'] == failed_run_id:
                found_error = True
                error_time = run['created_at']
            elif found_error and run['conclusion'] == 'success':
                success_time = run['created_at']
                FMT = '%Y-%m-%dT%H:%M:%SZ'
                tdelta = datetime.strptime(success_time, FMT) - datetime.strptime(error_time, FMT)
                return str(tdelta)
    return None

for page in range(1, 6):
    params['page'] = page
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for repo in data['items']:
            owner = repo['owner']['login']
            repo_name = repo['name']
            pipelines = get_pipeline_info(owner, repo_name)
            if pipelines:
                pipelines_info.append({'repo': repo_name, 'owner': owner, 'pipelines': pipelines})

with open('pipelines.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['repository_name', 'pipeline_name', 'logs_url', 'fix_time'])

    for repo_info in pipelines_info:
        for workflow in repo_info['pipelines']['workflows']:
            failed_runs = get_failed_runs(repo_info['owner'], repo_info['repo'], workflow['id'])
            for run in failed_runs:
                fix_time = get_time_to_fix(repo_info['owner'], repo_info['repo'], workflow['id'], run['id'])
                if fix_time:
                    writer.writerow([
                        f"{repo_info['owner']}/{repo_info['repo']}",
                        workflow['name'],
                        run['logs_url'],
                        fix_time
                    ])
