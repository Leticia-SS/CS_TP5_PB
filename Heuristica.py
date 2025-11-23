import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

matriz_distancias = np.array([
    [0, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    [20, 0, 40, 50, 60, 70, 80, 90, 100, 120],
    [30, 40, 0, 60, 70, 80, 90, 100, 110, 120],
    [40, 50, 60, 0, 80, 90, 100, 110, 120, 130],
    [50, 60, 70, 80, 0, 100, 110, 120, 130, 140],
    [60, 70, 80, 90, 100, 0, 120, 130, 140, 150],
    [70, 80, 90, 100, 110, 120, 0, 140, 150, 160],
    [80, 90, 100, 110, 120, 130, 140, 0, 160, 170],
    [90, 100, 110, 120, 130, 140, 150, 160, 0, 180],
    [100, 110, 120, 130, 140, 150, 160, 170, 180, 0]
])

cidades = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']



def vizinho_mais_proximo(matriz_distancias, cidade_inicial):
    num_cidades = len(matriz_distancias)
    visitadas = [False] * num_cidades
    caminho = [cidade_inicial]
    visitadas[cidade_inicial] = True
    distancia_total = 0

    print("============== ALGORITMO DO VIZINHO MAIS PROXIIMO ==============")
    print(f"Cidade inicial: {cidades[cidade_inicial]}")
    print("\nProcesso de construção de rota:")

    cidade_atual = cidade_inicial

    for etapa in range(num_cidades - 1):
        menor_distancia = float('inf')
        vizinho_mais_proximo = -1

        for vizinho in range(num_cidades):
            if not visitadas[vizinho] and matriz_distancias[cidade_atual][vizinho] < menor_distancia:
                menor_distancia = matriz_distancias[cidade_atual][vizinho]
                vizinho_mais_proximo = vizinho


        caminho.append(vizinho_mais_proximo)
        visitadas[vizinho_mais_proximo] = True
        distancia_total += menor_distancia

        print(f"Etapa {etapa + 1}: {cidades[cidade_atual]} --> {cidades[vizinho_mais_proximo]} (distância: {menor_distancia})")

        cidade_atual = vizinho_mais_proximo

    distancia_volta = matriz_distancias[caminho[-1]][cidade_inicial]
    distancia_total += distancia_volta
    caminho.append(cidade_inicial)

    print(f"Volta para início: {cidades[caminho[-2]]} --> {cidades[cidade_inicial]} (distância: {distancia_volta})")

    return caminho, distancia_total


def plotar_rota(caminho, matriz_distancias):
    G = nx.Graph()

    for cidade in cidades:
        G.add_node(cidade)

    for i in range(len(caminho) - 1):
        cidade_origem = cidades[caminho[i]]
        cidade_destino = cidades[caminho[i + 1]]
        distancia = matriz_distancias[caminho[i]][caminho[i + 1]]
        G.add_edge(cidade_origem, cidade_destino, weight=distancia)

    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    pos = nx.circular_layout(G)

    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    edges = list(G.edges())
    nx.draw_networkx_edges(G, pos, edgelist=edges, width=2, edge_color='red', alpha=0.7)


    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title('Rota Encontrada | Vizinho Mais Próximo')
    plt.axis('off')

    plt.subplot(1, 2, 2)


    x_positions = range(len(caminho))
    y_position = 0

    plt.plot(x_positions, [y_position] * len(caminho), 'ro-', linewidth=3, markersize=10)

    for i, cidade_idx in enumerate(caminho):
        plt.text(i, y_position + 0.1, cidades[cidade_idx],
                 ha='center', va='bottom', fontsize=12, fontweight='bold')

    for i in range(len(caminho) - 1):
        distancia = matriz_distancias[caminho[i]][caminho[i + 1]]
        x_mid = (i + i + 1) / 2
        plt.text(x_mid, y_position - 0.1, f'{distancia}',
                 ha='center', va='top', fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

    plt.title('Sequência de Visita das Cidades')
    plt.xlabel('Ordem de Visitação')
    plt.yticks([])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.show()


cidade_inicial = 0
caminho_encontrado, distancia_total = vizinho_mais_proximo(matriz_distancias, cidade_inicial)

print("==============RESULTADO FINAL ==============\n")

caminho_nomes = [cidades[i] for i in caminho_encontrado]
print(f"Rota encontrada: {' --> '.join(caminho_nomes)}")
print(f"Distsancia total percorrida: {distancia_total}")

print("\nDetalhamento da rota:")
for i in range(len(caminho_encontrado) - 1):
    cidade_origem = caminho_encontrado[i]
    cidade_destino = caminho_encontrado[i + 1]
    distancia_trecho = matriz_distancias[cidade_origem][cidade_destino]
    print(f"  {cidades[cidade_origem]} --> {cidades[cidade_destino]}: {distancia_trecho} km")

plotar_rota(caminho_encontrado, matriz_distancias)


























