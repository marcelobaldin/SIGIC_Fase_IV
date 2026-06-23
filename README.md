# SIGIC - Sistema Inteligente de Gerenciamento da Infraestrutura da Colonia

Fase IV - Energia para Sobreviver | FIAP 2026 | Ciencias da Computacao

**Marcelo Bastianello Baldin - RM568746 - Grupo 13**

## Sobre

Sistema de terminal para gerenciamento da infraestrutura energetica da colonia Aurora Siger em Marte. A rede de distribuicao de energia e modelada como um grafo ponderado nao-dirigido, permitindo otimizar rotas de transmissao entre os 8 modulos da base. O sistema integra algoritmos de grafos, calculo diferencial, regressao linear/logistica e analise de sustentabilidade (ESG).

Sem dependencias externas — usa apenas a biblioteca padrao do Python.

## Execucao

```bash
python codigo_fonte.py
```

O menu interativo sera exibido no terminal com 10 opcoes de navegacao.

## Funcionalidades

| Opcao | Funcionalidade | Descricao |
|-------|---------------|-----------|
| 1 | Visao geral | Resumo da colonia: energia, rede, modelos, ESG |
| 2 | Visualizar rede | Lista e matriz de adjacencia, metricas, diagrama |
| 3 | Consultar modulo | Dados detalhados de cada modulo + rota otima de energia |
| 4 | Caminho minimo | Dijkstra entre dois modulos com detalhamento de trechos |
| 5 | BFS e DFS | Busca em largura e profundidade a partir de qualquer vertice |
| 6 | Dados energeticos | Tabela de geracao vs consumo ao longo de 24h |
| 7 | Modelagem matematica | Funcao quadratica E(t), derivada, ponto critico, integral |
| 8 | Previsao | Regressao linear (SoC) e logistica (critico/normal) com entrada interativa |
| 9 | Simulacao | 5 cenarios: falha ARM, emergencia MED, tempestade, expansao, envio de energia |
| 10 | ESG | Score ambiental/social/governanca com recomendacoes |

## Exemplo de uso

Ao selecionar a opcao 4 (Caminho minimo), o sistema calcula via Dijkstra a rota de menor custo energetico. Por exemplo, para enviar energia de ARM (Armazenamento) para MED (Centro Medico):

```
  Origem:  ARM (Armazenamento de Energia)
  Destino: MED (Suporte Medico)
  Caminho: ARM -> CTR -> MED
  Custo total: 12 kWh
```

## Estrutura de arquivos

```
codigo_fonte.py                # Arquivo principal do sistema
arquivos_auxiliares/
  dados_energia.csv            # Telemetria energetica (12 registros, 24h)
  historico_cenarios.csv       # Dados para treinamento dos modelos (30 cenarios)
rede_colonia.pdf               # Diagrama visual da rede (grafo)
documentacao_complementar.pdf  # Documentacao tecnica (7 paginas)
link_video.txt                 # Link do video de apresentacao (YouTube)
```

## Algoritmos implementados

- **BFS** (Busca em Largura): exploracao nivel a nivel com fila (deque) — O(V+E)
- **DFS** (Busca em Profundidade): exploracao recursiva — O(V+E)
- **Dijkstra**: caminho de menor custo com heap (heapq) — O((V+E) log V)
- **Deteccao de pontos de articulacao**: vertices cuja remocao desconecta o grafo
- **Regressao linear multipla**: minimos quadrados com eliminacao de Gauss
- **Regressao logistica**: gradient descent com cross-entropy loss
- **Modelagem quadratica**: ajuste por sistema normal, derivada e integral numerica (trapezios)

## Estruturas de dados

- **Tuplas**: dados imutaveis dos modulos (codigo, nome, tipo, prioridade)
- **Dicionarios**: dados operacionais com acesso O(1) por chave
- **Listas**: series temporais, conexoes, matriz de adjacencia
- **Lista de adjacencia**: representacao do grafo como dicionario de listas
- **Matriz de adjacencia**: representacao do grafo como lista de listas
- **Heap (heapq)**: fila de prioridade para o algoritmo de Dijkstra
- **Deque**: fila eficiente para BFS

## Rede da colonia

8 modulos conectados por 14 arestas com peso = custo energetico de transmissao (kWh):

```
                [ARM] Armazenamento de Energia
               / | \  \
            5/  8|  10\ 12\
            /   |    \   \
     [CTR]---6--[HAB]  [OXI] [COM]
      |  \       |  \     |     |
     4|  7\     9| 11\  15|   13|
      |    \    |    \   |     |
    [COM] [MED] |  [AGR]       |
      |     |   |     |        |
     13\  10|   |   14|        |
        \   |   |    /         |
         [LAB]-----/-----------/
```

## Video de apresentacao

https://youtu.be/fEMgbNp3IjA

## Tecnologias

Python 3 (biblioteca padrao) | Grafos | Dijkstra | BFS/DFS | Calculo Diferencial | Regressao Linear | Regressao Logistica | Analise ESG
