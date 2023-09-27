import csv
import subprocess
import os
import time
import statistics
import pandas as pd

#
# Script para ler o arquivo de repositórios e clonar
# OBS: Só funciona se rodar dentro da pasta do CK
#

def extract_metrics(repo_name):
    data = pd.read_csv("class.csv")

    metrics = data[["loc", "cbo", "dit", "lcom"]]

    totals = metrics.sum()
    means = metrics.mean()
    medians = metrics.median()

    if totals.isnull().any():
        totals.fillna(0, inplace=True)
    if means.isnull().any():
        means.fillna(0, inplace=True)
    if medians.isnull().any():
        medians.fillna(0, inplace=True)

    results = pd.DataFrame({
        "repo_name": [repo_name],
        "loc_total": [totals["loc"]],
        "loc_media": [means["loc"]],
        "loc_mediana": [medians["loc"]],
        "cbo_total": [totals["cbo"]],
        "cbo_media": [means["cbo"]],
        "cbo_mediana": [medians["cbo"]],
        "dit_total": [totals["dit"]],
        "dit_media": [means["dit"]],
        "dit_mediana": [medians["dit"]],
        "lcom_total": [totals["lcom"]],
        "lcom_media": [means["lcom"]],
        "lcom_mediana": [medians["lcom"]]
    })
    with open("results.csv", mode="a", newline="") as file:
        results.to_csv(file, header=False, index=False, sep=";", float_format="%.2f")

def clone_repository(repo_url, target_folder, repo_name):
    try:
        subprocess.run(["git", "clone", repo_url, target_folder], check=True)
        print(f"Repositório clonado em: {target_folder}")
        
        time.sleep(1)

        os.system('java -jar target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar "{}"'.format(target_folder))

        time.sleep(1)

        extract_metrics(repo_name)

        time.sleep(1)

        os.system('rmdir /S /Q "{}"'.format(target_folder))
        print(f"Pasta do repositório {target_folder} apagada localmente.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao clonar repositório {repo_url}: {e}")

def create_header_result():
    header = [
        "repo_name",
        "loc_total",
        "loc_media",
        "loc_mediana",
        "cbo_total",
        "cbo_media",
        "cbo_mediana",
        "dit_total",
        "dit_media",
        "dit_mediana",
        "lcom_total",
        "lcom_media",
        "lcom_mediana"
    ]
    with open("results.csv", mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(header)



csv_file = "repository_data.csv"
clone_folder = "cloned_repositories"
create_header_result()

if not os.path.exists(clone_folder):
    os.makedirs(clone_folder)

with open(csv_file, newline="", encoding="utf-8") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    next(csv_reader)

    for row in csv_reader:
        name, stars, url, age_years, primary_language, releases = row
        repo_url = url + ".git"
        repo_name = name

        target_folder = os.path.join(clone_folder, repo_name)

        try:
            clone_repository(repo_url, target_folder, repo_name)
        except:
            print("Falha na leitura de dados")
