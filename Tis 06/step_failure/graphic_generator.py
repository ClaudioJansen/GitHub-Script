import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def gerar_grafico_falhas(filename, save_path):
    df = pd.read_csv(filename, delimiter=';')

    df.plot(x='Etapa', y='Contagem de Falhas', kind='bar', legend=False, color='royalblue', width=0.6)

    plt.title('Contagem de Falhas por Etapa')
    plt.xlabel('Etapa')
    plt.ylabel('Número de Falhas')
    plt.xticks(rotation=45)

    max_value = df['Contagem de Falhas'].max()
    plt.yticks(np.arange(0, max_value + 1, 100))

    plt.tight_layout()

    plt.savefig(save_path, format='png')
    print(f"Gráfico salvo como: {save_path}")

    plt.show()

caminho_entrada = "result_step_failure.csv"
caminho_saida = "grafico_falhas.png"

gerar_grafico_falhas(caminho_entrada, caminho_saida)
