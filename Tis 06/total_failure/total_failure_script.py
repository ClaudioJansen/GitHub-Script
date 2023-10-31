import csv
import statistics

def extrair_dados(filename):
    falhas_totais = []
    percentuais_falha = []

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader) 

        for row in reader:
            falhas = int(row[2]) 
            percentual = float(row[9].replace('%', '')) 
            
            falhas_totais.append(falhas)
            percentuais_falha.append(percentual)

    falhas_totais.sort()
    percentuais_falha.sort()

    return falhas_totais, percentuais_falha

def calcular_medidas(dados):
    media = sum(dados) / len(dados)
    mediana = statistics.median(dados)
    
    return media, mediana

def salvar_resultados(falhas_totais, percentuais_falha):
    media_falhas, mediana_falhas = calcular_medidas(falhas_totais)
    media_percentual, mediana_percentual = calcular_medidas(percentuais_falha)

    with open("result_total_failures_percentage.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Tipo", "Média", "Mediana"])
        writer.writerow(["Falhas Totais", "{:.2f}".format(media_falhas), "{:.2f}".format(mediana_falhas)])
        writer.writerow(["Percentual de Falha", "{:.2f}".format(media_percentual), "{:.2f}".format(mediana_percentual)])

falhas_totais, percentuais_falha = extrair_dados("../dados_pipelines.csv")
salvar_resultados(falhas_totais, percentuais_falha)
