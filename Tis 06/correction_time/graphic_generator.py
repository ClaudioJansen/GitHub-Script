import pandas as pd
import matplotlib.pyplot as plt

def gerar_grafico_tempos(caminho_entrada):
    df = pd.read_csv(caminho_entrada, delimiter=';')

    labels = ['Média', 'Mediana']
    values = [df['Média'].iloc[0], df['Mediana'].iloc[0]]

    plt.bar(labels, values, color=['blue', 'green'])

    plt.title('Média e Mediana do Tempo de Correção')
    plt.ylabel('Horas')
    for i, v in enumerate(values):
        plt.text(i, v + 5, str(v), ha='center', va='bottom', fontweight='bold')  

    plt.tight_layout()
    plt.savefig('grafico_tempos_correcao.png', dpi=300) 
    plt.show()

gerar_grafico_tempos("result_correction_time.csv")
