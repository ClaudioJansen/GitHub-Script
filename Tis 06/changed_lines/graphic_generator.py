import pandas as pd
import matplotlib.pyplot as plt

def plotar_grafico(filename):
    df = pd.read_csv(filename, delimiter=';')

    plt.figure(figsize=(10, 6))
    
    barWidth = 0.35
    r1 = range(len(df['Tipo']))
    r2 = [x + barWidth for x in r1]

    bars1 = plt.bar(r1, df['Média'], width=barWidth, color='blue', edgecolor='grey', label='Média')
    bars2 = plt.bar(r2, df['Mediana'], width=barWidth, color='red', edgecolor='grey', label='Mediana')
    
    def add_value_labels(bars):
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 5, round(yval, 2), ha='center', va='bottom')

    add_value_labels(bars1)
    add_value_labels(bars2)
    
    plt.xlabel('Tipo', fontweight='bold')
    plt.xticks([r + barWidth for r in range(len(df['Tipo']))], df['Tipo'])

    plt.legend()
    plt.title('Média e Mediana de Linhas Adicionadas e Removidas')
    
    plt.savefig("grafico_linhas.png")

    plt.show()

plotar_grafico("result_changed_lines.csv")
