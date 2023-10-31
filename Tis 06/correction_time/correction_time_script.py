import csv
import statistics

def ler_tempos_de_correcao(filename):
    tempos = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  
        for row in reader:
            tempos_correcao = eval(row[10]) 
            tempos.extend(tempos_correcao)  
    return tempos

def converter_para_horas(tempos):
    return [abs(t)/3600 for t in tempos]

def calcular_media(tempos):
    return sum(tempos) / len(tempos)

def salvar_resultados(media, mediana):
    with open("result_correction_time.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Média', 'Mediana'])
        writer.writerow([round(media, 2), round(mediana, 2)])

tempos = ler_tempos_de_correcao("../dados_pipelines.csv")

tempos_horas = sorted(converter_para_horas(tempos))

media = calcular_media(tempos_horas)
mediana = statistics.median(tempos_horas)

salvar_resultados(media, mediana)
