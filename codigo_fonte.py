#!/usr/bin/env python3
# =============================================================================
# SIGIC - Sistema Inteligente de Gerenciamento da Infraestrutura da Colonia
# Fase IV - Energia para Sobreviver | FIAP 2026
# Marcelo Bastianello Baldin - RM568746 - Grupo 13
#
# Arquivo principal - executar: python codigo_fonte.py
# Sem dependencias externas - usa apenas biblioteca padrao do Python.
# =
# ============================================================================

import csv
import os
import math
import heapq
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUX_DIR = os.path.join(BASE_DIR, 'arquivos_auxiliares')


# =============================================================================
# 1. ESTRUTURAS DE DADOS - MODULOS DA COLONIA
# =============================================================================
# Tuplas (dados imutaveis), dicionarios (acesso por chave) e listas (iteracao).
# Cada modulo representa um setor fisico da colonia Aurora Siger em Marte.

# Tuplas: informacoes fixas (codigo, nome completo, tipo, nivel de prioridade)
MODULOS_INFO = (
    ('HAB', 'Habitacao', 'essencial', 1),
    ('CTR', 'Centro de Controle', 'essencial', 2),
    ('ARM', 'Armazenamento de Energia', 'infraestrutura', 3),
    ('OXI', 'Producao de Oxigenio', 'essencial', 1),
    ('COM', 'Comunicacao', 'essencial', 4),
    ('MED', 'Suporte Medico', 'essencial', 3),
    ('AGR', 'Agricultura', 'suporte', 5),
    ('LAB', 'Laboratorio Cientifico', 'operacional', 6),
)

# Dicionario principal: dados operacionais detalhados de cada modulo
MODULOS = {
    'HAB': {
        'nome': 'Habitacao',
        'consumo_kwh': 45,
        'prioridade': 1,
        'capacidade_arm_kwh': 100,
        'distancia_hub_m': 50,
        'status': 'ativo',
        'descricao': 'Acomodacao da tripulacao e suporte a sobrevivencia',
    },
    'CTR': {
        'nome': 'Centro de Controle',
        'consumo_kwh': 30,
        'prioridade': 2,
        'capacidade_arm_kwh': 50,
        'distancia_hub_m': 30,
        'status': 'ativo',
        'descricao': 'Monitoramento e gerenciamento das operacoes',
    },
    'ARM': {
        'nome': 'Armazenamento de Energia',
        'consumo_kwh': 10,
        'prioridade': 3,
        'capacidade_arm_kwh': 500,
        'distancia_hub_m': 0,
        'status': 'ativo',
        'descricao': 'Armazenamento central de energia (baterias Li-ion)',
    },
    'OXI': {
        'nome': 'Producao de Oxigenio',
        'consumo_kwh': 50,
        'prioridade': 1,
        'capacidade_arm_kwh': 120,
        'distancia_hub_m': 60,
        'status': 'ativo',
        'descricao': 'Geracao e distribuicao de oxigenio para a base',
    },
    'COM': {
        'nome': 'Comunicacao',
        'consumo_kwh': 20,
        'prioridade': 4,
        'capacidade_arm_kwh': 30,
        'distancia_hub_m': 40,
        'status': 'ativo',
        'descricao': 'Troca de dados entre modulos e comunicacao com a Terra',
    },
    'MED': {
        'nome': 'Suporte Medico',
        'consumo_kwh': 25,
        'prioridade': 3,
        'capacidade_arm_kwh': 40,
        'distancia_hub_m': 45,
        'status': 'ativo',
        'descricao': 'Atendimento medico e monitoramento da saude',
    },
    'AGR': {
        'nome': 'Agricultura',
        'consumo_kwh': 35,
        'prioridade': 5,
        'capacidade_arm_kwh': 80,
        'distancia_hub_m': 70,
        'status': 'ativo',
        'descricao': 'Producao de alimentos e sustentabilidade',
    },
    'LAB': {
        'nome': 'Laboratorio Cientifico',
        'consumo_kwh': 40,
        'prioridade': 6,
        'capacidade_arm_kwh': 60,
        'distancia_hub_m': 55,
        'status': 'ativo',
        'descricao': 'Pesquisa e analise de materiais marcianos',
    },
}

# Lista de codigos dos modulos para iteracao
LISTA_MODULOS = [cod for cod, _, _, _ in MODULOS_INFO]

# Lista de conexoes da rede: (origem, destino, peso em kWh de custo de transmissao)
CONEXOES = [
    ('ARM', 'HAB', 8),
    ('ARM', 'CTR', 5),
    ('ARM', 'OXI', 10),
    ('ARM', 'COM', 12),
    ('CTR', 'HAB', 6),
    ('CTR', 'COM', 4),
    ('CTR', 'MED', 7),
    ('HAB', 'MED', 9),
    ('HAB', 'AGR', 11),
    ('HAB', 'OXI', 7),
    ('OXI', 'AGR', 15),
    ('COM', 'LAB', 13),
    ('MED', 'LAB', 10),
    ('AGR', 'LAB', 14),
]


# =============================================================================
# 2. REPRESENTACAO DA REDE - GRAFOS
# =============================================================================
# Grafo ponderado nao-dirigido: vertices = modulos, arestas = conexoes fisicas.
# Peso das arestas = custo energetico de transmissao entre modulos (kWh).
# Duas representacoes: lista de adjacencia (dicionario) e matriz de adjacencia.

class GrafoColonia:
    """Grafo ponderado nao-dirigido representando a rede da colonia."""

    def __init__(self, vertices, arestas):
        self.vertices = vertices
        self.n = len(vertices)
        self.idx = {v: i for i, v in enumerate(vertices)}

        # Lista de adjacencia: dicionario onde cada chave aponta para lista de (vizinho, peso)
        self.adj_lista = {v: [] for v in vertices}
        for u, v, w in arestas:
            self.adj_lista[u].append((v, w))
            self.adj_lista[v].append((u, w))

        # Matriz de adjacencia: lista de listas (0 = sem conexao, >0 = peso)
        self.adj_matriz = [[0] * self.n for _ in range(self.n)]
        for u, v, w in arestas:
            i, j = self.idx[u], self.idx[v]
            self.adj_matriz[i][j] = w
            self.adj_matriz[j][i] = w

    # ---- BFS: Busca em Largura ----
    # Usa fila (deque) para explorar a rede nivel a nivel.
    # Complexidade: O(V + E). Encontra caminho com menor numero de saltos.
    def bfs(self, origem):
        visitado = {v: False for v in self.vertices}
        dist = {v: -1 for v in self.vertices}
        pai = {v: None for v in self.vertices}
        ordem = []

        fila = deque()
        fila.append(origem)
        visitado[origem] = True
        dist[origem] = 0

        while fila:
            atual = fila.popleft()
            ordem.append(atual)
            for vizinho, _ in self.adj_lista[atual]:
                if not visitado[vizinho]:
                    visitado[vizinho] = True
                    dist[vizinho] = dist[atual] + 1
                    pai[vizinho] = atual
                    fila.append(vizinho)

        return {'ordem': ordem, 'distancias': dist, 'predecessores': pai}

    # ---- DFS: Busca em Profundidade ----
    # Usa recursao para explorar caminhos ate o fim antes de retroceder.
    # Complexidade: O(V + E). Detecta componentes conectados e ciclos.
    def dfs(self, origem):
        visitado = {v: False for v in self.vertices}
        ordem = []
        pai = {v: None for v in self.vertices}

        def _dfs_rec(v):
            visitado[v] = True
            ordem.append(v)
            for vizinho, _ in self.adj_lista[v]:
                if not visitado[vizinho]:
                    pai[vizinho] = v
                    _dfs_rec(vizinho)

        _dfs_rec(origem)
        return {'ordem': ordem, 'predecessores': pai}

    # ---- Dijkstra: Caminho de Menor Custo ----
    # Usa heap (fila de prioridade) para encontrar o caminho de menor custo.
    # Complexidade: O((V + E) log V). Otimiza rotas de distribuicao de energia.
    def dijkstra(self, origem):
        dist = {v: float('inf') for v in self.vertices}
        pai = {v: None for v in self.vertices}
        dist[origem] = 0
        heap = [(0, origem)]
        visitado = set()

        while heap:
            d, u = heapq.heappop(heap)
            if u in visitado:
                continue
            visitado.add(u)
            for vizinho, peso in self.adj_lista[u]:
                nova_dist = d + peso
                if nova_dist < dist[vizinho]:
                    dist[vizinho] = nova_dist
                    pai[vizinho] = u
                    heapq.heappush(heap, (nova_dist, vizinho))

        return {'distancias': dist, 'predecessores': pai}

    def caminho_minimo(self, origem, destino):
        """Retorna o caminho de menor custo entre dois vertices via Dijkstra."""
        resultado = self.dijkstra(origem)
        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            atual = resultado['predecessores'][atual]
        caminho.reverse()

        custo = resultado['distancias'][destino]
        if custo == float('inf'):
            return {'caminho': [], 'custo': -1, 'existe': False}
        return {'caminho': caminho, 'custo': custo, 'existe': True}

    # ---- Deteccao de vertices criticos (pontos de articulacao) ----
    # Remove cada vertice e verifica se o grafo continua conexo.
    def detectar_pontos_articulacao(self):
        articulacoes = []
        for v in self.vertices:
            restantes = [u for u in self.vertices if u != v]
            if not restantes:
                continue
            visitado = set()
            fila = deque([restantes[0]])
            visitado.add(restantes[0])
            while fila:
                atual = fila.popleft()
                for viz, _ in self.adj_lista[atual]:
                    if viz != v and viz not in visitado:
                        visitado.add(viz)
                        fila.append(viz)
            if len(visitado) < len(restantes):
                articulacoes.append(v)
        return articulacoes

    # ---- Metricas de eficiencia da rede ----
    def eficiencia_rede(self):
        total_arestas = sum(1 for v in self.vertices for _ in self.adj_lista[v]) // 2
        grau_medio = sum(len(self.adj_lista[v]) for v in self.vertices) / self.n
        densidade = (2 * total_arestas) / (self.n * (self.n - 1)) if self.n > 1 else 0

        custos = [w for v in self.vertices for _, w in self.adj_lista[v]]
        custo_medio = sum(custos) / len(custos) if custos else 0

        # Diametro: maior menor caminho no grafo
        diametro = 0
        for v in self.vertices:
            dists = self.dijkstra(v)['distancias']
            max_d = max(d for d in dists.values() if d < float('inf'))
            diametro = max(diametro, max_d)

        return {
            'vertices': self.n,
            'arestas': total_arestas,
            'grau_medio': round(grau_medio, 2),
            'densidade': round(densidade, 4),
            'custo_medio': round(custo_medio, 2),
            'diametro': diametro,
        }


# =============================================================================
# 3. LEITURA DE DADOS ENERGETICOS (CSV)
# =============================================================================
# Dados auxiliares carregados de arquivos CSV na pasta arquivos_auxiliares/.

def carregar_dados_energia(caminho):
    """Carrega serie temporal de energia do CSV (24h de operacao)."""
    dados = []
    with open(caminho, 'r', encoding='utf-8') as f:
        for linha in csv.DictReader(f):
            dados.append({
                'hora': int(linha['hora']),
                'geracao_solar': float(linha['geracao_solar']),
                'geracao_eolica': float(linha['geracao_eolica']),
                'consumo_total': float(linha['consumo_total']),
                'soc_bateria': float(linha['soc_bateria']),
                'temp_externa': float(linha['temp_externa']),
                'modulos_ativos': int(linha['modulos_ativos']),
                'eficiencia_rede': float(linha['eficiencia_rede']),
            })
    return dados


def carregar_historico_cenarios(caminho):
    """Carrega historico de cenarios para treinamento dos modelos de previsao."""
    dados = []
    with open(caminho, 'r', encoding='utf-8') as f:
        for linha in csv.DictReader(f):
            dados.append({
                'soc_bateria': float(linha['soc_bateria']),
                'consumo_total': float(linha['consumo_total']),
                'geracao_total': float(linha['geracao_total']),
                'modulos_ativos': int(linha['modulos_ativos']),
                'temp_externa': float(linha['temp_externa']),
                'eficiencia_rede': float(linha['eficiencia_rede']),
                'critico': int(linha['critico']),
            })
    return dados


# =============================================================================
# 4. MODELAGEM MATEMATICA - CALCULO DIFERENCIAL
# =============================================================================
# Funcao de consumo: E(t) = a*t^2 + b*t + c  (modelo quadratico)
# Derivada: E'(t) = 2a*t + b  (taxa de variacao instantanea)
# Integral numerica pelo metodo dos trapezios (energia total no intervalo)

class ModelagemMatematica:
    """Modelagem do consumo energetico com calculo diferencial."""

    @staticmethod
    def ajustar_modelo(dados):
        """Ajusta E(t) = at^2 + bt + c por minimos quadrados (sistema normal)."""
        n = len(dados)
        horas = [d['hora'] for d in dados]
        consumos = [d['consumo_total'] for d in dados]

        # Montar e resolver o sistema normal X^T X beta = X^T y
        s4 = sum(t**4 for t in horas)
        s3 = sum(t**3 for t in horas)
        s2 = sum(t**2 for t in horas)
        s1 = sum(horas)
        s0 = n
        sy2 = sum(t**2 * y for t, y in zip(horas, consumos))
        sy1 = sum(t * y for t, y in zip(horas, consumos))
        sy0 = sum(consumos)

        # Regra de Cramer para sistema 3x3
        det = s4*(s2*s0 - s1*s1) - s3*(s3*s0 - s1*s2) + s2*(s3*s1 - s2*s2)
        if abs(det) < 1e-10:
            return {'a': 0, 'b': 0, 'c': sum(consumos)/n}

        a = (sy2*(s2*s0 - s1*s1) - s3*(sy1*s0 - s1*sy0) + s2*(sy1*s1 - s2*sy0)) / det
        b = (s4*(sy1*s0 - s1*sy0) - sy2*(s3*s0 - s1*s2) + s2*(s3*sy0 - sy1*s2)) / det
        c = (s4*(s2*sy0 - sy1*s1) - s3*(s3*sy0 - sy1*s2) + sy2*(s3*s1 - s2*s2)) / det

        return {'a': round(a, 6), 'b': round(b, 4), 'c': round(c, 2)}

    @staticmethod
    def avaliar(coefs, t):
        """Avalia E(t) = at^2 + bt + c."""
        return coefs['a'] * t**2 + coefs['b'] * t + coefs['c']

    @staticmethod
    def derivada(coefs, t):
        """Calcula E'(t) = 2at + b (taxa de variacao instantanea do consumo)."""
        return 2 * coefs['a'] * t + coefs['b']

    @staticmethod
    def ponto_critico(coefs):
        """Encontra ponto critico t* = -b/(2a) — minimo ou maximo do consumo."""
        if abs(coefs['a']) < 1e-10:
            return {'t_critico': None, 'tipo': 'linear', 'valor': None}
        t_crit = -coefs['b'] / (2 * coefs['a'])
        valor = ModelagemMatematica.avaliar(coefs, t_crit)
        tipo = 'minimo' if coefs['a'] > 0 else 'maximo'
        return {'t_critico': round(t_crit, 2), 'tipo': tipo, 'valor': round(valor, 2)}

    @staticmethod
    def integral_numerica(coefs, t0, t1, n_passos=100):
        """Integral pelo metodo dos trapezios — energia total consumida no intervalo."""
        dt = (t1 - t0) / n_passos
        soma = 0.5 * (ModelagemMatematica.avaliar(coefs, t0) +
                       ModelagemMatematica.avaliar(coefs, t1))
        for i in range(1, n_passos):
            soma += ModelagemMatematica.avaliar(coefs, t0 + i * dt)
        return round(soma * dt, 2)

    @staticmethod
    def r_quadrado(dados, coefs):
        """Coeficiente de determinacao R2 — qualidade do ajuste."""
        consumos = [d['consumo_total'] for d in dados]
        media = sum(consumos) / len(consumos)
        ss_tot = sum((y - media)**2 for y in consumos)
        ss_res = sum((y - ModelagemMatematica.avaliar(coefs, d['hora']))**2
                     for d, y in zip(dados, consumos))
        return round(1 - ss_res / ss_tot, 4) if ss_tot > 0 else 0


# =============================================================================
# 5. PREVISAO - REGRESSAO LINEAR E LOGISTICA
# =============================================================================
# Regressao linear: preve SoC (estado de carga) a partir de consumo e geracao.
# Regressao logistica: classifica cenarios como critico/normal (binaria).
# Implementacoes manuais sem bibliotecas externas.

class RegressaoLinear:
    """Regressao linear multipla: SoC = b0 + b1*consumo + b2*geracao."""

    @staticmethod
    def treinar(dados):
        """Treina por minimos quadrados — resolve o sistema (X^T X) beta = X^T y."""
        n = len(dados)
        X = []
        y = []
        for d in dados:
            geracao = d.get('geracao_total',
                           d.get('geracao_solar', 0) + d.get('geracao_eolica', 0))
            X.append([1, d['consumo_total'], geracao])
            y.append(d['soc_bateria'])

        k = len(X[0])
        XtX = [[sum(X[i][a]*X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
        Xty = [sum(X[i][a]*y[i] for i in range(n)) for a in range(k)]

        # Eliminacao de Gauss para resolver o sistema
        aug = [XtX[i][:] + [Xty[i]] for i in range(k)]
        for col in range(k):
            max_row = max(range(col, k), key=lambda r: abs(aug[r][col]))
            aug[col], aug[max_row] = aug[max_row], aug[col]
            if abs(aug[col][col]) < 1e-10:
                continue
            for row in range(k):
                if row == col:
                    continue
                fator = aug[row][col] / aug[col][col]
                for j in range(k + 1):
                    aug[row][j] -= fator * aug[col][j]

        beta = [aug[i][k] / aug[i][i] if abs(aug[i][i]) > 1e-10 else 0 for i in range(k)]

        # Metricas de qualidade
        y_pred = [sum(beta[j]*X[i][j] for j in range(k)) for i in range(n)]
        y_med = sum(y) / n
        ss_tot = sum((yi - y_med)**2 for yi in y)
        ss_res = sum((yi - yp)**2 for yi, yp in zip(y, y_pred))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        rmse = math.sqrt(ss_res / n) if n > 0 else 0

        return {
            'beta': [round(b, 4) for b in beta],
            'r2': round(r2, 4),
            'rmse': round(rmse, 2),
            'variaveis': ['intercepto', 'consumo_total', 'geracao_total'],
            'formula': "SoC = {:.2f} + ({:.4f}) * consumo + ({:.4f}) * geracao".format(
                beta[0], beta[1], beta[2]),
        }

    @staticmethod
    def prever(modelo, consumo, geracao):
        """Preve SoC (0-100%) com base no modelo treinado."""
        b = modelo['beta']
        return max(0, min(100, round(b[0] + b[1]*consumo + b[2]*geracao, 1)))


class RegressaoLogistica:
    """Regressao logistica para classificacao de cenarios criticos.

    Sigmoid: sigma(z) = 1 / (1 + e^(-z))
    Treinamento por gradient descent com cross-entropy loss.
    """

    @staticmethod
    def _sigmoid(z):
        z = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z))

    @staticmethod
    def treinar(dados, lr=0.5, epocas=5000):
        """Treina com gradient descent. Features: SoC, consumo, geracao, modulos, eficiencia."""
        n = len(dados)
        features_raw = []
        y = []
        for d in dados:
            geracao = d.get('geracao_total',
                           d.get('geracao_solar', 0) + d.get('geracao_eolica', 0))
            features_raw.append([d['soc_bateria'], d['consumo_total'],
                                 geracao, float(d['modulos_ativos']),
                                 d['eficiencia_rede']])
            y.append(d['critico'])

        k = len(features_raw[0])

        # Normalizacao min-max das features
        mins = [min(features_raw[i][j] for i in range(n)) for j in range(k)]
        maxs = [max(features_raw[i][j] for i in range(n)) for j in range(k)]
        ranges = [maxs[j] - mins[j] if maxs[j] != mins[j] else 1 for j in range(k)]

        X = [[1.0] + [(features_raw[i][j] - mins[j]) / ranges[j]
                       for j in range(k)] for i in range(n)]
        nf = k + 1

        # Pesos iniciais zerados
        w = [0.0] * nf

        # Gradient descent
        for epoca in range(epocas):
            grad = [0.0] * nf
            for i in range(n):
                z = sum(w[j] * X[i][j] for j in range(nf))
                p = RegressaoLogistica._sigmoid(z)
                erro = p - y[i]
                for j in range(nf):
                    grad[j] += erro * X[i][j]
            for j in range(nf):
                w[j] -= lr * grad[j] / n

        # Acuracia e matriz de confusao
        tp = fp = tn = fn = 0
        for i in range(n):
            z = sum(w[j] * X[i][j] for j in range(nf))
            pred = 1 if RegressaoLogistica._sigmoid(z) >= 0.5 else 0
            if pred == 1 and y[i] == 1: tp += 1
            elif pred == 1 and y[i] == 0: fp += 1
            elif pred == 0 and y[i] == 0: tn += 1
            else: fn += 1

        acuracia = (tp + tn) / n

        return {
            'pesos': [round(wj, 4) for wj in w],
            'acuracia': round(acuracia, 4),
            'matriz_confusao': {'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn},
            'normalizacao': {'mins': mins, 'ranges': ranges},
            'variaveis': ['intercepto', 'soc_bateria', 'consumo_total',
                          'geracao_total', 'modulos_ativos', 'eficiencia_rede'],
        }

    @staticmethod
    def prever(modelo, soc, consumo, modulos, geracao=30.0, eficiencia=0.88):
        """Preve probabilidade de cenario critico."""
        norm = modelo['normalizacao']
        x_norm = [
            1.0,
            (soc - norm['mins'][0]) / norm['ranges'][0],
            (consumo - norm['mins'][1]) / norm['ranges'][1],
            (geracao - norm['mins'][2]) / norm['ranges'][2],
            (modulos - norm['mins'][3]) / norm['ranges'][3],
            (eficiencia - norm['mins'][4]) / norm['ranges'][4],
        ]
        z = sum(modelo['pesos'][j] * x_norm[j] for j in range(len(modelo['pesos'])))
        prob = RegressaoLogistica._sigmoid(z)
        return {
            'probabilidade_critico': round(prob, 4),
            'classificacao': 'CRITICO' if prob >= 0.5 else 'NORMAL',
            'confianca': round(abs(prob - 0.5) * 2, 4),
        }


# =============================================================================
# 6. ANALISE ESG E SUSTENTABILIDADE
# =============================================================================
# Calcula metricas ambientais, sociais e de governanca da colonia.

class AnaliseESG:
    """Analise de sustentabilidade e governanca."""

    @staticmethod
    def calcular_metricas(dados, grafo):
        total_geracao = sum(d['geracao_solar'] + d['geracao_eolica'] for d in dados)
        total_consumo = sum(d['consumo_total'] for d in dados)
        pct_renovavel = (total_geracao / total_consumo * 100) if total_consumo > 0 else 0

        efic_media = sum(d['eficiencia_rede'] for d in dados) / len(dados) if dados else 0
        perda_estimada = (1 - efic_media) * total_consumo

        # CO2 evitado comparado com geradores diesel (0.7 kgCO2/kWh)
        co2_evitado = total_geracao * 0.7

        # Score ESG composto (0-100)
        score_e = min(100, pct_renovavel)
        score_s = min(100, sum(1 for d in dados if d['modulos_ativos'] >= 6) / len(dados) * 100)
        score_g = min(100, efic_media * 100)
        score_esg = round((score_e * 0.4 + score_s * 0.3 + score_g * 0.3), 1)

        modulos_essenciais = [c for c, m in MODULOS.items() if m['prioridade'] <= 3]
        consumo_essencial = sum(MODULOS[c]['consumo_kwh'] for c in modulos_essenciais)
        consumo_total_mod = sum(m['consumo_kwh'] for m in MODULOS.values())
        pct_essencial = round(consumo_essencial / consumo_total_mod * 100, 1)

        recomendacoes = []
        if pct_renovavel < 80:
            recomendacoes.append(('ALTO', 'Energia Renovavel',
                'Aumentar capacidade solar/eolica (atual: {:.0f}%)'.format(pct_renovavel)))
        if efic_media < 0.90:
            recomendacoes.append(('MEDIO', 'Eficiencia da Rede',
                'Otimizar rotas de distribuicao (eficiencia: {:.1%})'.format(efic_media)))
        if perda_estimada > 50:
            recomendacoes.append(('MEDIO', 'Reducao de Perdas',
                'Reduzir perdas na transmissao ({:.0f} kWh estimados)'.format(perda_estimada)))
        recomendacoes.append(('ALTO', 'Expansao Planejada',
            'Priorizar conexoes curtas ao expandir, minimizando perdas'))
        recomendacoes.append(('ALTO', 'Governanca',
            'Manter sistemas essenciais (prioridade 1-3) com redundancia energetica'))

        return {
            'total_geracao_kwh': round(total_geracao, 1),
            'total_consumo_kwh': round(total_consumo, 1),
            'pct_renovavel': round(pct_renovavel, 1),
            'eficiencia_media': round(efic_media, 4),
            'perda_estimada_kwh': round(perda_estimada, 1),
            'co2_evitado_kg': round(co2_evitado, 1),
            'score_esg': score_esg,
            'score_e': round(score_e, 1),
            'score_s': round(score_s, 1),
            'score_g': round(score_g, 1),
            'modulos_essenciais': modulos_essenciais,
            'pct_consumo_essencial': pct_essencial,
            'recomendacoes': recomendacoes,
        }


# =============================================================================
# 7. CLASSE PRINCIPAL DO SISTEMA (SIGIC)
# =============================================================================
# Integra todos os modulos: grafo, dados energeticos, modelagem e previsao.

class SIGIC:
    """Sistema Inteligente de Gerenciamento da Infraestrutura da Colonia."""

    def __init__(self):
        print("  Inicializando SIGIC...")

        # Construir grafo da rede
        self.grafo = GrafoColonia(LISTA_MODULOS, CONEXOES)

        # Carregar dados de energia do CSV
        self.dados_energia = carregar_dados_energia(
            os.path.join(AUX_DIR, 'dados_energia.csv'))
        self.historico = carregar_historico_cenarios(
            os.path.join(AUX_DIR, 'historico_cenarios.csv'))

        # Ajustar modelo matematico (quadratico)
        self.coefs_modelo = ModelagemMatematica.ajustar_modelo(self.dados_energia)
        self.r2_modelo = ModelagemMatematica.r_quadrado(self.dados_energia, self.coefs_modelo)

        # Treinar modelos de previsao
        self.modelo_linear = RegressaoLinear.treinar(self.historico)
        self.modelo_logistico = RegressaoLogistica.treinar(self.historico)

        # Calcular metricas ESG
        self.metricas_esg = AnaliseESG.calcular_metricas(self.dados_energia, self.grafo)

        print("  Sistema inicializado com sucesso.\n")


# =============================================================================
# 8. FUNCOES DE EXIBICAO NO TERMINAL
# =============================================================================
# Cada funcao exibe uma secao do sistema de forma clara e organizada.

def linha(char='=', tamanho=70):
    print(char * tamanho)


def titulo(texto):
    print()
    linha()
    print("  " + texto)
    linha()


def listar_modulos_menu():
    """Exibe lista numerada de modulos para selecao pelo usuario."""
    print()
    for i, cod in enumerate(LISTA_MODULOS, 1):
        m = MODULOS[cod]
        print("    {}. {} ({}) - {}".format(i, m['nome'], cod, m['descricao'][:45]))
    print()


def selecionar_modulo(mensagem="Escolha o modulo"):
    """Solicita que o usuario selecione um modulo da lista."""
    listar_modulos_menu()
    while True:
        try:
            escolha = input("  {} (1-{}): ".format(mensagem, len(LISTA_MODULOS)))
            idx = int(escolha) - 1
            if 0 <= idx < len(LISTA_MODULOS):
                return LISTA_MODULOS[idx]
            print("  Opcao invalida. Tente novamente.")
        except ValueError:
            print("  Digite um numero valido.")


# ---- 1. Visao geral ----
def exibir_visao_geral(sistema):
    titulo("VISAO GERAL DA COLONIA AURORA SIGER")
    ultimo = sistema.dados_energia[-1]
    geracao = ultimo['geracao_solar'] + ultimo['geracao_eolica']
    rede = sistema.grafo.eficiencia_rede()

    print()
    print("  Colonia: Aurora Siger")
    print("  Localizacao: Acidalia Planitia, Marte")
    print("  Modulos operacionais: {}".format(len(MODULOS)))
    print()
    print("  --- Energia (ultima leitura - {}h) ---".format(ultimo['hora']))
    print("  Geracao solar:    {:.0f} kWh".format(ultimo['geracao_solar']))
    print("  Geracao eolica:   {:.0f} kWh".format(ultimo['geracao_eolica']))
    print("  Geracao total:    {:.0f} kWh".format(geracao))
    print("  Consumo total:    {:.0f} kWh".format(ultimo['consumo_total']))
    print("  Balanco:          {:+.0f} kWh".format(geracao - ultimo['consumo_total']))
    print("  Bateria (SoC):    {:.0f}%".format(ultimo['soc_bateria']))
    print("  Eficiencia rede:  {:.1%}".format(ultimo['eficiencia_rede']))
    print()
    print("  --- Rede ---")
    print("  Vertices: {}  |  Arestas: {}".format(rede['vertices'], rede['arestas']))
    print("  Grau medio: {}  |  Densidade: {}".format(rede['grau_medio'], rede['densidade']))
    print("  Diametro: {} kWh  |  Custo medio: {} kWh".format(rede['diametro'], rede['custo_medio']))
    print()
    print("  --- Modelos ---")
    print("  Modelagem R2: {}".format(sistema.r2_modelo))
    print("  Regressao Linear R2: {}".format(sistema.modelo_linear['r2']))
    print("  Regressao Logistica Acuracia: {:.1%}".format(sistema.modelo_logistico['acuracia']))
    print("  Score ESG: {}/100".format(sistema.metricas_esg['score_esg']))
    print()


# ---- 2. Visualizar rede (grafo) ----
def exibir_rede(sistema):
    titulo("REDE DA COLONIA - REPRESENTACAO EM GRAFOS")

    # Lista de adjacencia
    print("\n  Lista de adjacencia:")
    print("  " + "-" * 60)
    for v in LISTA_MODULOS:
        vizinhos = sistema.grafo.adj_lista[v]
        viz_str = ", ".join("{} ({}kWh)".format(viz, w) for viz, w in vizinhos)
        print("  {} [{}]: {}".format(v, MODULOS[v]['nome'], viz_str))

    # Matriz de adjacencia
    print("\n  Matriz de adjacencia:")
    print("  " + "-" * 60)
    header = "       " + "  ".join("{:>4}".format(v) for v in LISTA_MODULOS)
    print(header)
    for i, vi in enumerate(LISTA_MODULOS):
        row = "  {:>4} ".format(vi)
        for j in range(len(LISTA_MODULOS)):
            val = sistema.grafo.adj_matriz[i][j]
            row += "  {:>4}".format(val if val > 0 else '-')
        print(row)

    # Metricas
    efic = sistema.grafo.eficiencia_rede()
    print("\n  Metricas da rede:")
    print("  Vertices: {}  |  Arestas: {}".format(efic['vertices'], efic['arestas']))
    print("  Grau medio: {}  |  Densidade: {}".format(efic['grau_medio'], efic['densidade']))
    print("  Diametro: {} kWh  |  Custo medio: {} kWh".format(efic['diametro'], efic['custo_medio']))

    # Pontos de articulacao (vertices criticos)
    articulacoes = sistema.grafo.detectar_pontos_articulacao()
    if articulacoes:
        nomes = ", ".join("{} ({})".format(v, MODULOS[v]['nome']) for v in articulacoes)
        print("\n  Pontos de articulacao (vertices criticos): {}".format(nomes))
    else:
        print("\n  Nenhum ponto de articulacao — rede robusta.")

    # Mapa visual em texto
    print("\n  Diagrama da rede (texto):")
    print("  " + "-" * 60)
    print("                    [ARM] Armazenamento de Energia")
    print("                   / | \\  \\")
    print("                5/  8|  10\\ 12\\")
    print("                /   |    \\   \\")
    print("         [CTR]---6--[HAB]  [OXI] [COM]")
    print("          |  \\       |  \\     |     |")
    print("         4|  7\\     9| 11\\  15|   13|")
    print("          |    \\    |    \\   |     |")
    print("        [COM] [MED] |  [AGR]       |")
    print("          |     |   |     |         |")
    print("         13\\  10|   |   14|         |")
    print("            \\   |   |    /          |")
    print("             [LAB]-----/------------/")
    print("  " + "-" * 60)
    print("  Pesos = custo energetico de transmissao (kWh)")
    print()


# ---- 3. Consultar modulos ----
def consultar_modulo(sistema):
    titulo("CONSULTAR MODULO")
    cod = selecionar_modulo("Selecione o modulo para consultar")
    m = MODULOS[cod]

    print()
    linha('-', 50)
    print("  Modulo: {} ({})".format(m['nome'], cod))
    linha('-', 50)
    print("  Descricao:     {}".format(m['descricao']))
    print("  Consumo:       {} kWh/h".format(m['consumo_kwh']))
    print("  Prioridade:    {} ({})".format(m['prioridade'],
        'essencial' if m['prioridade'] <= 2 else 'importante' if m['prioridade'] <= 4 else 'operacional'))
    print("  Armazenamento: {} kWh".format(m['capacidade_arm_kwh']))
    print("  Dist. ao hub:  {} m".format(m['distancia_hub_m']))
    print("  Status:        {}".format(m['status'].upper()))

    # Conexoes deste modulo no grafo
    vizinhos = sistema.grafo.adj_lista[cod]
    print("\n  Conexoes na rede:")
    for viz, peso in vizinhos:
        print("    -> {} ({}) — custo {} kWh".format(viz, MODULOS[viz]['nome'], peso))

    # Caminho minimo ate Armazenamento de Energia
    if cod != 'ARM':
        resultado = sistema.grafo.caminho_minimo('ARM', cod)
        if resultado['existe']:
            caminho_str = " -> ".join(resultado['caminho'])
            print("\n  Rota otima de energia (ARM -> {}):".format(cod))
            print("    Caminho: {}".format(caminho_str))
            print("    Custo total: {} kWh".format(resultado['custo']))
    print()


# ---- 4. Caminho minimo (Dijkstra) ----
def executar_caminho_minimo(sistema):
    titulo("CAMINHO MINIMO - ALGORITMO DE DIJKSTRA")
    print("\n  O algoritmo de Dijkstra encontra a rota de menor custo energetico")
    print("  entre dois modulos da colonia.\n")

    print("  Selecione a ORIGEM:")
    origem = selecionar_modulo("Modulo de origem")

    print("  Selecione o DESTINO:")
    destino = selecionar_modulo("Modulo de destino")

    if origem == destino:
        print("\n  Origem e destino sao o mesmo modulo.")
        return

    resultado = sistema.grafo.caminho_minimo(origem, destino)

    print()
    linha('-', 50)
    if resultado['existe']:
        caminho_str = " -> ".join(resultado['caminho'])
        print("  Origem:  {} ({})".format(origem, MODULOS[origem]['nome']))
        print("  Destino: {} ({})".format(destino, MODULOS[destino]['nome']))
        print("  Caminho: {}".format(caminho_str))
        print("  Custo total: {} kWh".format(resultado['custo']))
        print("  Saltos: {}".format(len(resultado['caminho']) - 1))

        # Detalhar cada trecho
        print("\n  Detalhamento do caminho:")
        cam = resultado['caminho']
        for i in range(len(cam) - 1):
            u, v = cam[i], cam[i + 1]
            peso = 0
            for viz, w in sistema.grafo.adj_lista[u]:
                if viz == v:
                    peso = w
                    break
            print("    {} -> {}: {} kWh".format(u, v, peso))
    else:
        print("  Nao existe caminho entre {} e {}.".format(origem, destino))
    linha('-', 50)

    # Mostrar tambem todos os custos a partir da origem (tabela Dijkstra)
    djk = sistema.grafo.dijkstra(origem)
    print("\n  Custos minimos a partir de {} ({}):".format(origem, MODULOS[origem]['nome']))
    print("  {:>6} | {:>25} | {:>10}".format("Codigo", "Nome", "Custo (kWh)"))
    print("  " + "-" * 48)
    for v in LISTA_MODULOS:
        custo = djk['distancias'][v]
        custo_str = str(custo) if custo < float('inf') else "---"
        print("  {:>6} | {:>25} | {:>10}".format(v, MODULOS[v]['nome'], custo_str))
    print()


# ---- 5. BFS e DFS ----
def executar_bfs_dfs(sistema):
    titulo("BUSCA EM LARGURA (BFS) E PROFUNDIDADE (DFS)")

    print("  Selecione o vertice de origem:")
    origem = selecionar_modulo("Vertice de origem")

    # BFS
    res_bfs = sistema.grafo.bfs(origem)
    print("\n  --- BFS (Busca em Largura) a partir de {} ---".format(origem))
    print("  Ordem de visita: {}".format(" -> ".join(res_bfs['ordem'])))
    print("  Distancias (numero de saltos):")
    for v in res_bfs['ordem']:
        pred = res_bfs['predecessores'][v]
        pred_str = pred if pred else "-"
        print("    {} ({}): {} salto(s), predecessor: {}".format(
            v, MODULOS[v]['nome'], res_bfs['distancias'][v], pred_str))

    # DFS
    res_dfs = sistema.grafo.dfs(origem)
    print("\n  --- DFS (Busca em Profundidade) a partir de {} ---".format(origem))
    print("  Ordem de visita: {}".format(" -> ".join(res_dfs['ordem'])))
    print("  Predecessores:")
    for v in res_dfs['ordem']:
        pred = res_dfs['predecessores'][v]
        pred_str = pred if pred else "-"
        print("    {} ({}): predecessor: {}".format(v, MODULOS[v]['nome'], pred_str))
    print()


# ---- 6. Dados energeticos ----
def exibir_energia(sistema):
    titulo("DADOS ENERGETICOS - SERIE TEMPORAL 24H")

    print("\n  {:>5} | {:>7} | {:>7} | {:>7} | {:>7} | {:>6} | {:>5} | {:>5}".format(
        "Hora", "Solar", "Eolica", "Total G", "Consumo", "Bal.", "SoC%", "Efic"))
    print("  " + "-" * 70)

    for d in sistema.dados_energia:
        geracao = d['geracao_solar'] + d['geracao_eolica']
        balanco = geracao - d['consumo_total']
        print("  {:>4}h | {:>5.0f}kW | {:>5.0f}kW | {:>5.0f}kW | {:>5.0f}kW | {:>+5.0f} | {:>4.0f}% | {:.0%}".format(
            d['hora'], d['geracao_solar'], d['geracao_eolica'],
            geracao, d['consumo_total'], balanco,
            d['soc_bateria'], d['eficiencia_rede']))

    # Resumo
    total_ger = sum(d['geracao_solar'] + d['geracao_eolica'] for d in sistema.dados_energia)
    total_con = sum(d['consumo_total'] for d in sistema.dados_energia)
    print()
    print("  Geracao total (24h):  {:.0f} kWh".format(total_ger))
    print("  Consumo total (24h):  {:.0f} kWh".format(total_con))
    print("  Balanco diario:       {:+.0f} kWh".format(total_ger - total_con))
    print("  SoC inicial: {:.0f}%  |  SoC final: {:.0f}%".format(
        sistema.dados_energia[0]['soc_bateria'],
        sistema.dados_energia[-1]['soc_bateria']))
    print()


# ---- 7. Modelagem matematica ----
def exibir_modelagem(sistema):
    titulo("MODELAGEM MATEMATICA - CALCULO DIFERENCIAL")
    coefs = sistema.coefs_modelo

    print("\n  Funcao ajustada de consumo:")
    print("    E(t) = {:.6f} * t^2 + ({:.4f}) * t + {:.2f}".format(
        coefs['a'], coefs['b'], coefs['c']))
    print("\n  Derivada (taxa de variacao instantanea):")
    print("    E'(t) = {:.6f} * t + ({:.4f})".format(2*coefs['a'], coefs['b']))

    pc = ModelagemMatematica.ponto_critico(coefs)
    if pc['t_critico'] is not None:
        print("\n  Ponto critico: t* = {:.2f}h ({})".format(pc['t_critico'], pc['tipo']))
        print("    E(t*) = {:.2f} kWh".format(pc['valor']))

    print("\n  R2 (qualidade do ajuste): {}".format(sistema.r2_modelo))

    integral = ModelagemMatematica.integral_numerica(coefs, 0, 24)
    print("  Energia total consumida em 24h (integral): {} kWh".format(integral))

    # Tabela: hora x valor real x valor modelo x derivada
    print("\n  {:>6} | {:>12} | {:>12} | {:>12} | {:>8}".format(
        "Hora", "Consumo Real", "Modelo E(t)", "Erro", "E'(t)"))
    print("  " + "-" * 58)
    for d in sistema.dados_energia:
        t = d['hora']
        real = d['consumo_total']
        modelo = ModelagemMatematica.avaliar(coefs, t)
        deriv = ModelagemMatematica.derivada(coefs, t)
        erro = real - modelo
        print("  {:>4}h  | {:>10.1f}kW | {:>10.1f}kW | {:>+10.1f}  | {:>+7.2f}".format(
            t, real, modelo, erro, deriv))
    print()


# ---- 8. Previsao (regressao linear e logistica) ----
def exibir_previsao(sistema):
    titulo("PREVISAO E CLASSIFICACAO")

    # Regressao linear
    ml = sistema.modelo_linear
    print("\n  --- Regressao Linear (Previsao de SoC) ---")
    print("  Formula: {}".format(ml['formula']))
    print("  R2: {}  |  RMSE: {}".format(ml['r2'], ml['rmse']))
    print("  Variaveis: {}".format(", ".join(ml['variaveis'])))

    # Regressao logistica
    mlog = sistema.modelo_logistico
    mc = mlog['matriz_confusao']
    print("\n  --- Regressao Logistica (Classificacao Critico/Normal) ---")
    print("  Acuracia: {:.1%}".format(mlog['acuracia']))
    print("  Matriz de confusao:")
    print("                   Previsto")
    print("                  Normal  Critico")
    print("    Real Normal  |  {:>3}   |  {:>3}  |".format(mc['tn'], mc['fp']))
    print("    Real Critico |  {:>3}   |  {:>3}  |".format(mc['fn'], mc['tp']))
    print("  Variaveis: {}".format(", ".join(mlog['variaveis'][1:])))

    # Previsao interativa
    print("\n  --- Previsao Interativa ---")
    try:
        consumo = float(input("  Informe o consumo total (kWh, ex: 180): "))
        geracao = float(input("  Informe a geracao total (kWh, ex: 40): "))

        soc_prev = RegressaoLinear.prever(ml, consumo, geracao)
        estado = RegressaoLogistica.prever(
            mlog, soc_prev, consumo, 8, geracao=geracao, eficiencia=0.88)

        print("\n  Resultado da previsao:")
        print("    SoC previsto:   {:.1f}%".format(soc_prev))
        print("    Classificacao:  {}".format(estado['classificacao']))
        print("    Probabilidade de ser critico: {:.1%}".format(estado['probabilidade_critico']))
        print("    Confianca: {:.1%}".format(estado['confianca']))
    except ValueError:
        print("  Valor invalido. Retornando ao menu.")
    print()


# ---- 9. Simulacao operacional ----
def simular_operacao(sistema):
    titulo("SIMULACAO OPERACIONAL")

    print("\n  Cenarios de simulacao disponiveis:")
    print("    1. Falha no Armazenamento de Energia (ARM desativado)")
    print("    2. Demanda critica no Centro Medico (MED)")
    print("    3. Tempestade solar (geracao reduzida)")
    print("    4. Expansao da colonia (novo modulo)")
    print("    5. Simular envio de energia a um modulo especifico")

    try:
        opcao = input("\n  Selecione o cenario (1-5): ")
    except (EOFError, KeyboardInterrupt):
        return

    if opcao == '1':
        # Simulacao: ARM desativado — recalcular rotas sem ARM
        titulo("SIMULACAO: FALHA NO ARMAZENAMENTO DE ENERGIA")
        print("\n  Cenario: O modulo ARM (Armazenamento de Energia) sofreu uma falha.")
        print("  O sistema precisa redistribuir energia sem passar por ARM.\n")

        vertices_sem_arm = [v for v in LISTA_MODULOS if v != 'ARM']
        arestas_sem_arm = [(u, v, w) for u, v, w in CONEXOES if u != 'ARM' and v != 'ARM']
        grafo_temp = GrafoColonia(vertices_sem_arm, arestas_sem_arm)

        print("  Rede sem ARM: {} vertices, {} arestas".format(
            grafo_temp.n, sum(1 for v in grafo_temp.vertices for _ in grafo_temp.adj_lista[v]) // 2))

        # Verificar conectividade
        bfs_res = grafo_temp.bfs(vertices_sem_arm[0])
        conectados = len(bfs_res['ordem'])
        if conectados < len(vertices_sem_arm):
            print("  ALERTA: Rede DESCONECTADA! {} de {} modulos alcancaveis.".format(
                conectados, len(vertices_sem_arm)))
        else:
            print("  Rede permanece conexa ({} modulos alcancaveis).".format(conectados))

        # Novos caminhos
        print("\n  Novos caminhos de distribuicao (sem ARM):")
        for dest in vertices_sem_arm:
            if dest == 'CTR':
                continue
            res = grafo_temp.caminho_minimo('CTR', dest)
            if res['existe']:
                print("    CTR -> {}: {} (custo: {} kWh)".format(
                    dest, " -> ".join(res['caminho']), res['custo']))
            else:
                print("    CTR -> {}: SEM ROTA DISPONIVEL".format(dest))

    elif opcao == '2':
        # Simulacao: demanda critica no Centro Medico
        titulo("SIMULACAO: DEMANDA CRITICA NO CENTRO MEDICO")
        print("\n  Cenario: Emergencia medica! MED precisa de energia urgente.")
        print("  Encontrando a rota mais eficiente de ARM para MED.\n")

        resultado = sistema.grafo.caminho_minimo('ARM', 'MED')
        if resultado['existe']:
            print("  Rota otima: {}".format(" -> ".join(resultado['caminho'])))
            print("  Custo: {} kWh".format(resultado['custo']))
            print("  Consumo atual do MED: {} kWh/h".format(MODULOS['MED']['consumo_kwh']))
            print("  Consumo emergencial estimado: {} kWh/h".format(
                MODULOS['MED']['consumo_kwh'] * 2))
            print("\n  Acao: priorizar rota ARM -> MED, reduzir modulos nao-essenciais.")

            # Modulos que podem ser reduzidos
            print("\n  Modulos candidatos a reducao de consumo:")
            for cod in LISTA_MODULOS:
                m = MODULOS[cod]
                if m['prioridade'] >= 5:
                    print("    {} ({}) — {} kWh/h (prioridade {})".format(
                        cod, m['nome'], m['consumo_kwh'], m['prioridade']))

    elif opcao == '3':
        # Simulacao: tempestade solar
        titulo("SIMULACAO: TEMPESTADE SOLAR")
        print("\n  Cenario: Tempestade solar reduz geracao em 60%.")
        print("  Analisando impacto no balanco energetico.\n")

        consumo_total = sum(m['consumo_kwh'] for m in MODULOS.values())
        print("  Consumo total da colonia: {} kWh/h".format(consumo_total))

        for d in sistema.dados_energia:
            ger_original = d['geracao_solar'] + d['geracao_eolica']
            ger_reduzida = ger_original * 0.4
            deficit = ger_reduzida - d['consumo_total']
            status = "OK" if deficit >= 0 else "DEFICIT"
            print("    {:>2}h: geracao {:.0f}->{:.0f} kWh | consumo {:.0f} | balanco {:+.0f} | {}".format(
                d['hora'], ger_original, ger_reduzida, d['consumo_total'], deficit, status))

        print("\n  Recomendacao: ativar protocolo de economia e desligar modulos de prioridade >= 5.")

    elif opcao == '4':
        # Simulacao: expansao com novo modulo
        titulo("SIMULACAO: EXPANSAO DA COLONIA")
        print("\n  Cenario: Adicionar modulo 'Estacao de Reciclagem' (REC).")
        print("  Novo modulo: consumo 20 kWh, prioridade 4.\n")

        novos_vertices = LISTA_MODULOS + ['REC']
        novas_arestas = CONEXOES + [('AGR', 'REC', 8), ('LAB', 'REC', 6)]
        grafo_exp = GrafoColonia(novos_vertices, novas_arestas)

        efic_antes = sistema.grafo.eficiencia_rede()
        efic_depois = grafo_exp.eficiencia_rede()

        print("  Comparacao antes/depois da expansao:")
        print("  {:>20} | {:>10} | {:>10}".format("Metrica", "Antes", "Depois"))
        print("  " + "-" * 46)
        print("  {:>20} | {:>10} | {:>10}".format("Vertices", efic_antes['vertices'], efic_depois['vertices']))
        print("  {:>20} | {:>10} | {:>10}".format("Arestas", efic_antes['arestas'], efic_depois['arestas']))
        print("  {:>20} | {:>10} | {:>10}".format("Grau medio", efic_antes['grau_medio'], efic_depois['grau_medio']))
        print("  {:>20} | {:>10} | {:>10}".format("Densidade", efic_antes['densidade'], efic_depois['densidade']))
        print("  {:>20} | {:>10} | {:>10}".format("Diametro (kWh)", efic_antes['diametro'], efic_depois['diametro']))

        # Caminho ARM -> REC
        res = grafo_exp.caminho_minimo('ARM', 'REC')
        if res['existe']:
            print("\n  Rota otima ARM -> REC: {}".format(" -> ".join(res['caminho'])))
            print("  Custo: {} kWh".format(res['custo']))

    elif opcao == '5':
        # Simulacao: envio de energia a modulo especifico (exemplo do enunciado)
        titulo("SIMULACAO: ENVIO DE ENERGIA A MODULO ESPECIFICO")
        print("\n  Selecione o modulo de DESTINO para envio de energia a partir de ARM:")
        destino = selecionar_modulo("Modulo destino")

        if destino == 'ARM':
            print("  ARM ja e a origem de energia. Selecione outro modulo.")
        else:
            resultado = sistema.grafo.caminho_minimo('ARM', destino)
            print()
            linha('-', 55)
            print("  Envio de energia: ARM -> {} ({})".format(destino, MODULOS[destino]['nome']))
            linha('-', 55)

            if resultado['existe']:
                caminho_str = " -> ".join(resultado['caminho'])
                print("  Algoritmo: Dijkstra (caminho de menor custo)")
                print("  Rota encontrada: {}".format(caminho_str))
                print("  Custo de transmissao: {} kWh".format(resultado['custo']))
                print("  Numero de saltos: {}".format(len(resultado['caminho']) - 1))
                print("  Consumo do modulo destino: {} kWh/h".format(MODULOS[destino]['consumo_kwh']))

                # Detalhar cada trecho
                print("\n  Trechos da rota:")
                cam = resultado['caminho']
                for i in range(len(cam) - 1):
                    u, v = cam[i], cam[i + 1]
                    peso = 0
                    for viz, w in sistema.grafo.adj_lista[u]:
                        if viz == v:
                            peso = w
                            break
                    print("    {} ({}) -> {} ({}): {} kWh".format(
                        u, MODULOS[u]['nome'], v, MODULOS[v]['nome'], peso))
            else:
                print("  Nao ha rota disponivel de ARM para {}.".format(destino))
    else:
        print("  Opcao invalida.")
    print()


# ---- 10. Sustentabilidade e ESG ----
def exibir_esg(sistema):
    titulo("SUSTENTABILIDADE E GOVERNANCA (ESG)")
    esg = sistema.metricas_esg

    print("\n  Score ESG: {}/100".format(esg['score_esg']))
    print("    Environmental (E): {}/100".format(esg['score_e']))
    print("    Social (S):        {}/100".format(esg['score_s']))
    print("    Governance (G):    {}/100".format(esg['score_g']))

    print("\n  --- Metricas Energeticas ---")
    print("  Geracao total (24h):     {:.1f} kWh".format(esg['total_geracao_kwh']))
    print("  Consumo total (24h):     {:.1f} kWh".format(esg['total_consumo_kwh']))
    print("  % Energia renovavel:     {:.1f}%".format(esg['pct_renovavel']))
    print("  CO2 evitado:             {:.1f} kg".format(esg['co2_evitado_kg']))
    print("  Eficiencia media rede:   {:.1%}".format(esg['eficiencia_media']))
    print("  Perdas estimadas:        {:.1f} kWh".format(esg['perda_estimada_kwh']))

    print("\n  --- Sistemas Essenciais ---")
    print("  Modulos essenciais (prioridade 1-3): {}".format(
        ", ".join(esg['modulos_essenciais'])))
    print("  Consumo essencial: {:.1f}% do total".format(esg['pct_consumo_essencial']))

    print("\n  --- Recomendacoes ---")
    for impacto, area, acao in esg['recomendacoes']:
        print("  [{}] {}: {}".format(impacto, area, acao))

    print("\n  --- Reflexao sobre Sustentabilidade e Governanca ---")
    print("  A colonia Aurora Siger depende de fontes renovaveis (solar e eolica)")
    print("  para toda sua operacao em Marte. A governanca e garantida por um")
    print("  sistema de prioridades que protege modulos essenciais (suporte a vida,")
    print("  oxigenio, controle) mesmo em cenarios de crise energetica. A rede de")
    print("  distribuicao em grafo permite otimizar rotas e identificar pontos")
    print("  criticos, garantindo resiliencia e eficiencia na alocacao de recursos.")
    print()


# =============================================================================
# 9. MENU PRINCIPAL
# =============================================================================

def exibir_menu():
    """Exibe o menu principal do sistema."""
    print()
    linha('=')
    print("  SIGIC - Menu Principal")
    linha('=')
    print("   1. Visao geral da colonia")
    print("   2. Visualizar rede (grafo)")
    print("   3. Consultar modulo")
    print("   4. Caminho minimo (Dijkstra)")
    print("   5. BFS e DFS")
    print("   6. Dados energeticos (24h)")
    print("   7. Modelagem matematica")
    print("   8. Previsao e classificacao")
    print("   9. Simulacao operacional")
    print("  10. Sustentabilidade e ESG")
    print("   0. Sair")
    linha('=')


def main():
    """Funcao principal — inicializa o sistema e exibe o menu interativo."""

    print()
    print("#" * 70)
    print("#" + " " * 68 + "#")
    print("#   SIGIC - Sistema Inteligente de Gerenciamento da Infraestrutura  #")
    print("#                     da Colonia Aurora Siger                       #")
    print("#   Fase IV - Energia para Sobreviver | FIAP 2026                   #")
    print("#   Marcelo Bastianello Baldin - RM568746 - Grupo 13                #")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    print()

    # Inicializar sistema (carrega dados, treina modelos)
    sistema = SIGIC()

    while True:
        exibir_menu()

        try:
            opcao = input("\n  Escolha uma opcao (0-10): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Encerrando SIGIC. Ate a proxima!")
            break

        if opcao == '1':
            exibir_visao_geral(sistema)
        elif opcao == '2':
            exibir_rede(sistema)
        elif opcao == '3':
            consultar_modulo(sistema)
        elif opcao == '4':
            executar_caminho_minimo(sistema)
        elif opcao == '5':
            executar_bfs_dfs(sistema)
        elif opcao == '6':
            exibir_energia(sistema)
        elif opcao == '7':
            exibir_modelagem(sistema)
        elif opcao == '8':
            exibir_previsao(sistema)
        elif opcao == '9':
            simular_operacao(sistema)
        elif opcao == '10':
            exibir_esg(sistema)
        elif opcao == '0':
            print("\n  Encerrando SIGIC. Ate a proxima!\n")
            break
        else:
            print("\n  Opcao invalida. Tente novamente.")

        input("  Pressione ENTER para continuar...")


if __name__ == '__main__':
    main()
