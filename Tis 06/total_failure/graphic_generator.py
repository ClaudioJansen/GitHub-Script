import pandas as pd
import matplotlib.pyplot as plt

def gerar_grafico(filename):
    df = pd.read_csv(filename, delimiter=';')

    ax = df.plot(x='Tipo', y=['Média', 'Mediana'], kind='bar', figsize=(10, 6), color=['skyblue', 'salmon'])
    ax.set_ylabel('Valor')
    ax.set_title('Análise das Falhas Totais e Percentual de Falha')
    ax.set_xticklabels(df['Tipo'], rotation=0)

    for p in ax.patches:
        ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
    
    plt.tight_layout()
    plt.savefig("graph_total_failures_percentage.png")
    plt.show()

gerar_grafico("result_total_failures_percentage.csv")
