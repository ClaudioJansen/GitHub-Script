import csv
import statistics

def processar_linhas(filename):
    linhas_adicionadas = []
    linhas_removidas = []

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader) 

        for row in reader:
            adicionadas = eval(row[11])  
            removidas = eval(row[12])

            linhas_adicionadas.extend(adicionadas)
            linhas_removidas.extend(removidas)

    linhas_adicionadas.sort()  
    linhas_removidas.sort()

    return linhas_adicionadas, linhas_removidas

def calcular_media_mediana(lista):
    media = round(sum(lista) / len(lista), 2)
    mediana = round(statistics.median(lista), 2)
    return media, mediana

def salvar_resultados(media_adicionadas, mediana_adicionadas, media_removidas, mediana_removidas):
    with open("result_changed_lines.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Tipo', 'Média', 'Mediana'])
        writer.writerow(['Adicionadas', media_adicionadas, mediana_adicionadas])
        writer.writerow(['Removidas', media_removidas, mediana_removidas])

linhas_adicionadas, linhas_removidas = processar_linhas("../dados_pipelines.csv")
media_adicionadas, mediana_adicionadas = calcular_media_mediana(linhas_adicionadas)
media_removidas, mediana_removidas = calcular_media_mediana(linhas_removidas)
salvar_resultados(media_adicionadas, mediana_adicionadas, media_removidas, mediana_removidas)
