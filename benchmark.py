import matplotlib.pyplot as plt

contador_linhas = 0

def hanoi_benchmark(n, origem, destino, auxiliar):
    global contador_linhas
    contador_linhas += 1 
    
    if n > 0:
        hanoi_benchmark(n - 1, origem, auxiliar, destino)
        
        contador_linhas += 1 
        
        hanoi_benchmark(n - 1, auxiliar, destino, origem)

def rodar_bateria_testes(n_maximo):
    global contador_linhas
    valores_n = list(range(1, n_maximo + 1))
    historico_linhas = []

    print("Iniciando bateria de testes...")
    for n in valores_n:
        contador_linhas = 0
        hanoi_benchmark(n, 'A', 'C', 'B')
        historico_linhas.append(contador_linhas)
        print(f"Discos (n): {n:02d} | Linhas/Operações executadas: {contador_linhas}")

    plt.figure(figsize=(10, 6))
    plt.plot(valores_n, historico_linhas, marker='o', linestyle='-', color='#BF616A', linewidth=2)
    
    plt.title('Análise de Desempenho - Torre de Hanói', fontsize=14, fontweight='bold')
    plt.xlabel('Número de Discos (n)', fontsize=12)
    plt.ylabel('Quantidade de Linhas Executadas', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(valores_n)
    
    plt.show()

if __name__ == "__main__":
    rodar_bateria_testes(15)