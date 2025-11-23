import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


matriz_distancias = np.array([
    [0, 10, 5, 7, 3, 2],
    [10, 0, 8, 1, 4, 9],
    [5, 8, 0, 2, 1, 3],
    [7, 1, 2, 0, 5, 6],
    [3, 4, 1, 5, 0, 4],
    [2, 9, 3, 6, 4, 0]
])


cidades = ['A', 'B', 'C', 'D', 'E', 'F']


def dijkstra(grafo, inicio):
    n = len(grafo)
    distancias = [float('inf')] * n
    distancias[inicio] = 0
    visitados = [False] * n
    anteriores = [-1] * n

    for _ in range(n):
        menor_distancia = float('inf')
        indice_menor = -1

        for i in range(n):
            if not visitados[i] and distancias[i] < menor_distancia:
                menor_distancia = distancias[i]
                indice_menor = i

        if indice_menor == -1:
            break

        visitados[indice_menor] = True

        for vizinho in range(n):
            if (grafo[indice_menor][vizinho] > 0 and
                    not visitados[vizinho] and
                    distancias[indice_menor] + grafo[indice_menor][vizinho] < distancias[vizinho]):
                distancias[vizinho] = distancias[indice_menor] + grafo[indice_menor][vizinho]
                anteriores[vizinho] = indice_menor

    return distancias, anteriores


def obter_caminhos_mais_curtos(anteriores, inicio):
    caminhos = {}
    n = len(anteriores)

    for i in range(n):
        if i == inicio:
            caminhos[i] = [inicio]
            continue

        caminho = []
        atual = i

        while atual != -1:
            caminho.append(atual)
            atual = anteriores[atual]

        caminho.reverse()
        caminhos[i] = caminho

    return caminhos

def construir_arvore_geradora(anteriores, grafo):
    G = nx.Graph()
    n = len(anteriores)

    for i in range(n):
        G.add_node(cidades[i])

    for i in range(n):
        if anteriores[i] != -1:
            peso = int(grafo[anteriores[i]][i])
            G.add_edge(cidades[anteriores[i]], cidades[i], weight=peso)

    return G



cidade_inicial = 0
distancias_curtas, anteriores = dijkstra(matriz_distancias, cidade_inicial)
caminhos = obter_caminhos_mais_curtos(anteriores, cidade_inicial)

arvore_geradora = construir_arvore_geradora(anteriores, matriz_distancias)

print("================== RESULTADOS DO ALGORITMO DE DIJKSTRA ==================\n")
print(f"Cidade de origem: {cidades[cidade_inicial]}\n")

print("Distancia mais curtas a partir de A: ")
for i, cidade in enumerate(cidades):
    print(f"{cidades[cidade_inicial]} -> {cidade}: {distancias_curtas[i]}")

print("\nCaminhos mais curtos: ")
for i, cidade in enumerate(cidades):
    caminho_str = ' -> '.join([cidades[no] for no in caminhos[i]])
    print(f"{cidades[cidade_inicial]} -> {cidade}: {caminho_str}")

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
pos = nx.spring_layout(arvore_geradora)
rotulos_arestas = nx.get_edge_attributes(arvore_geradora, 'weight')


nx.draw(arvore_geradora, pos, with_labels=True, node_size=800,
        node_color='lightblue', font_size=12, font_weight='bold')
nx.draw_networkx_edge_labels(arvore_geradora, pos, edge_labels=rotulos_arestas)


plt.title('Arvore Geradora | Caminhos Mais Curtos a partir de A')

plt.subplot(1, 2, 2)
grafo_completo = nx.Graph()

for i in range(len(cidades)):
    for j in range(i + 1, len(cidades)):
        if matriz_distancias[i][j] > 0:
            peso = int(matriz_distancias[i][j])
            grafo_completo.add_edge(cidades[i], cidades[j], weight=peso)


pos_completo = nx.spring_layout(grafo_completo)
rotulos_arestas_completo = nx.get_edge_attributes(grafo_completo, 'weight')


nx.draw(grafo_completo, pos_completo, with_labels=True, node_size=800,
        node_color='lightgreen', font_size=12, font_weight='bold')
nx.draw_networkx_edge_labels(grafo_completo, pos_completo, edge_labels=rotulos_arestas_completo)


plt.title('Grafo Completo | Todas as Conexões')

plt.tight_layout()
plt.show()

print("\n================== INFORMAÇÕES DA ARVORE GERADORA ==================")
print(f"Numero de arestas na arvore: {arvore_geradora.number_of_edges()}")
print(f"Numero de nós na arvore: {arvore_geradora.number_of_nodes()}")
print(f"Arestas da arvore geradora: {list(arvore_geradora.edges(data=True))}")


















