import csv
import ast  
import os  

def contar_falhas_etapas(filename):
    contadores = {
        "lint": 0,
        "build": 0,
        "test": 0,
        "deploy": 0,
        "outro": 0  
    }

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader) 

        for row in reader:
            etapas_falha = ast.literal_eval(row[3])
            for etapa in etapas_falha:
                etapa = etapa.lower()
                encontrou = False  
                for chave in contadores:
                    if chave in etapa:
                        contadores[chave] += 1
                        encontrou = True
                        break  

                if not encontrou:
                    contadores["outro"] += 1

    return contadores

def salvar_contagem_falhas(contagem, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Etapa', 'Contagem de Falhas']) 
        
        contagem_ordenada = sorted(contagem.items(), key=lambda x: x[1], reverse=True)

        for etapa, count in contagem_ordenada:
            writer.writerow([etapa, count])

caminho_entrada = os.path.join('..', 'dados_pipelines.csv')
caminho_saida = "result_step_failure.csv"

contagem = contar_falhas_etapas(caminho_entrada)
salvar_contagem_falhas(contagem, caminho_saida)
