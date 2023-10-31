import csv
import os  

def contar_linguagens(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)

        linguagem_contador = {}
        for row in reader:
            linguagem = row[1]  
            if linguagem in linguagem_contador:
                linguagem_contador[linguagem] += 1
            else:
                linguagem_contador[linguagem] = 1

    return linguagem_contador

def salvar_resultados(contagem, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Linguagem', 'Contagem'])  

        contagem_ordenada = sorted(contagem.items(), key=lambda x: x[1], reverse=True)

        for linguagem, count in contagem_ordenada:
            writer.writerow([linguagem, count])

caminho_entrada = os.path.join('..', 'dados_pipelines.csv')
caminho_saida = "result_languages.csv"

contagem = contar_linguagens(caminho_entrada)
salvar_resultados(contagem, caminho_saida)