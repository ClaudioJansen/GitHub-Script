import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def gerar_grafico_linguagens(filename, save_path):
    df = pd.read_csv(filename, delimiter=';')

    df.plot(x='Linguagem', y='Contagem', kind='bar', legend=False, color='lightcoral', width=0.5)

    plt.title('Contagem de Repositórios por Linguagem')
    plt.xlabel('Linguagem')
    plt.ylabel('Número de Repositórios')
    plt.xticks(rotation=45)

    max_value = df['Contagem'].max()
    plt.yticks(np.arange(0, max_value + 1, 5))

    plt.tight_layout()

    plt.savefig(save_path, format='png')
    print(f"Gráfico salvo como: {save_path}")

    plt.show()

caminho_entrada = "result_languages.csv"
caminho_saida = "grafico_linguagens.png"

gerar_grafico_linguagens(caminho_entrada, caminho_saida)
