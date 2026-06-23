#!/usr/bin/env python3
"""
SIGIC - Sistema Inteligente de Gerenciamento da Infraestrutura da Colonia
Fase IV - Energia para Sobreviver | FIAP 2026
Marcelo Bastianello Baldin - RM568746 - Grupo 13

Execucao: python codigo_fonte.py
Acesso: http://localhost:5050 (usuario: usuario / senha: senha)
"""

import csv
import os
import math
import heapq
from collections import deque
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify)

# ============================================================
# CONFIGURACOES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUX_DIR = os.path.join(BASE_DIR, 'arquivos_auxiliares')

USUARIOS = {
    'usuario': {'senha': 'senha', 'nome': 'Operador SIGIC'}
}


# ============================================================
# 1. ESTRUTURAS DE DADOS - MODULOS DA COLONIA
# ============================================================
# Listas, tuplas, dicionarios e matrizes conforme requisitos

# Tuplas: informacoes fixas dos modulos (nome, tipo, prioridade)
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

# Dicionario: dados operacionais de cada modulo
MODULOS = {
    'HAB': {
        'nome': 'Habitacao',
        'consumo_kwh': 45,
        'prioridade': 1,
        'capacidade_arm_kwh': 100,
        'distancia_hub_m': 50,
        'freq_comunicacao': 'alta',
        'status': 'ativo',
        'descricao': 'Acomodacao da tripulacao e suporte a sobrevivencia',
    },
    'CTR': {
        'nome': 'Centro de Controle',
        'consumo_kwh': 30,
        'prioridade': 2,
        'capacidade_arm_kwh': 50,
        'distancia_hub_m': 30,
        'freq_comunicacao': 'alta',
        'status': 'ativo',
        'descricao': 'Monitoramento e gerenciamento das operacoes',
    },
    'ARM': {
        'nome': 'Armazenamento de Energia',
        'consumo_kwh': 10,
        'prioridade': 3,
        'capacidade_arm_kwh': 500,
        'distancia_hub_m': 0,
        'freq_comunicacao': 'media',
        'status': 'ativo',
        'descricao': 'Armazenamento central de energia (baterias Li-ion)',
    },
    'OXI': {
        'nome': 'Producao de Oxigenio',
        'consumo_kwh': 50,
        'prioridade': 1,
        'capacidade_arm_kwh': 120,
        'distancia_hub_m': 60,
        'freq_comunicacao': 'alta',
        'status': 'ativo',
        'descricao': 'Geracao e distribuicao de oxigenio para a base',
    },
    'COM': {
        'nome': 'Comunicacao',
        'consumo_kwh': 20,
        'prioridade': 4,
        'capacidade_arm_kwh': 30,
        'distancia_hub_m': 40,
        'freq_comunicacao': 'alta',
        'status': 'ativo',
        'descricao': 'Troca de dados entre modulos e comunicacao com a Terra',
    },
    'MED': {
        'nome': 'Suporte Medico',
        'consumo_kwh': 25,
        'prioridade': 3,
        'capacidade_arm_kwh': 40,
        'distancia_hub_m': 45,
        'freq_comunicacao': 'media',
        'status': 'ativo',
        'descricao': 'Atendimento medico e monitoramento da saude',
    },
    'AGR': {
        'nome': 'Agricultura',
        'consumo_kwh': 35,
        'prioridade': 5,
        'capacidade_arm_kwh': 80,
        'distancia_hub_m': 70,
        'freq_comunicacao': 'baixa',
        'status': 'ativo',
        'descricao': 'Producao de alimentos e sustentabilidade',
    },
    'LAB': {
        'nome': 'Laboratorio Cientifico',
        'consumo_kwh': 40,
        'prioridade': 6,
        'capacidade_arm_kwh': 60,
        'distancia_hub_m': 55,
        'freq_comunicacao': 'baixa',
        'status': 'ativo',
        'descricao': 'Pesquisa e analise de materiais marcianos',
    },
}

# Lista: nomes dos modulos para iteracao
LISTA_MODULOS = [cod for cod, _, _, _ in MODULOS_INFO]

# Lista: conexoes da rede (origem, destino, peso em kWh de custo de transmissao)
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


# ============================================================
# 2. REPRESENTACAO DA REDE - GRAFOS
# ============================================================

class GrafoColonia:
    """Grafo ponderado nao-dirigido representando a rede da colonia.

    Vertices = modulos da base marciana
    Arestas = conexoes fisicas (cabos, dutos) com peso = custo energetico
    Representacoes: lista de adjacencia E matriz de adjacencia
    """

    def __init__(self, vertices: list, arestas: list):
        self.vertices = vertices
        self.n = len(vertices)
        self.idx = {v: i for i, v in enumerate(vertices)}

        # Lista de adjacencia (dicionario de listas)
        self.adj_lista: dict[str, list[tuple[str, int]]] = {v: [] for v in vertices}
        for u, v, w in arestas:
            self.adj_lista[u].append((v, w))
            self.adj_lista[v].append((u, w))

        # Matriz de adjacencia (lista de listas)
        self.adj_matriz: list[list[int]] = [[0] * self.n for _ in range(self.n)]
        for u, v, w in arestas:
            i, j = self.idx[u], self.idx[v]
            self.adj_matriz[i][j] = w
            self.adj_matriz[j][i] = w

    # ---------- BFS - Busca em Largura ----------
    def bfs(self, origem: str) -> dict:
        """BFS a partir de um vertice. Retorna ordem de visita e distancias (saltos)."""
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

    # ---------- DFS - Busca em Profundidade ----------
    def dfs(self, origem: str) -> dict:
        """DFS a partir de um vertice. Retorna ordem de visita."""
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

    # ---------- Dijkstra - Caminho Minimo ----------
    def dijkstra(self, origem: str) -> dict:
        """Dijkstra: caminho de menor custo a partir de um vertice."""
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

    def caminho_minimo(self, origem: str, destino: str) -> dict:
        """Retorna o caminho minimo entre dois vertices e seu custo."""
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

    # ---------- Conexoes criticas ----------
    def detectar_pontos_articulacao(self) -> list:
        """Identifica vertices cuja remocao desconecta o grafo (pontos de articulacao)."""
        articulacoes = []
        for v in self.vertices:
            # Remove vertice e verifica conectividade
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

    def arestas_criticas(self) -> list:
        """Identifica arestas cuja remocao desconecta o grafo (pontes)."""
        pontes = []
        arestas = [(u, v, w) for u in self.vertices for v, w in self.adj_lista[u] if u < v]
        for eu, ev, ew in arestas:
            # Remove aresta e verifica conectividade via BFS
            self.adj_lista[eu] = [(v, w) for v, w in self.adj_lista[eu] if v != ev]
            self.adj_lista[ev] = [(v, w) for v, w in self.adj_lista[ev] if v != eu]
            resultado = self.bfs(self.vertices[0])
            if len(resultado['ordem']) < self.n:
                pontes.append((eu, ev, ew))
            self.adj_lista[eu].append((ev, ew))
            self.adj_lista[ev].append((eu, ew))
        return pontes

    def eficiencia_rede(self) -> dict:
        """Analisa eficiencia geral da rede."""
        total_arestas = sum(1 for v in self.vertices for _ in self.adj_lista[v]) // 2
        grau_medio = sum(len(self.adj_lista[v]) for v in self.vertices) / self.n
        densidade = (2 * total_arestas) / (self.n * (self.n - 1)) if self.n > 1 else 0

        # Custo medio de transmissao
        custos = [w for v in self.vertices for _, w in self.adj_lista[v]]
        custo_medio = sum(custos) / len(custos) if custos else 0

        # Diametro do grafo (maior menor caminho)
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


# ============================================================
# 3. LEITURA DE DADOS ENERGETICOS
# ============================================================

def carregar_dados_energia(caminho: str) -> list[dict]:
    """Carrega dados de energia do CSV."""
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


def carregar_historico_cenarios(caminho: str) -> list[dict]:
    """Carrega historico de cenarios para treinamento dos modelos ML."""
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


# ============================================================
# 4. MODELAGEM MATEMATICA E OTIMIZACAO
# ============================================================

class ModelagemMatematica:
    """Modelagem do consumo energetico com calculo diferencial.

    Funcao de consumo: E(t) = a*t^2 + b*t + c  (quadratica)
    Derivada: E'(t) = 2*a*t + b  (taxa de variacao instantanea)
    Ponto critico: t* = -b/(2a)  (ponto de minimo/maximo)
    """

    @staticmethod
    def ajustar_modelo(dados: list[dict]) -> dict:
        """Ajusta modelo quadratico E(t) = at^2 + bt + c por minimos quadrados."""
        n = len(dados)
        horas = [d['hora'] for d in dados]
        consumos = [d['consumo_total'] for d in dados]

        # Sistema normal: X^T X beta = X^T y
        # X = [t^2, t, 1]
        s4 = sum(t**4 for t in horas)
        s3 = sum(t**3 for t in horas)
        s2 = sum(t**2 for t in horas)
        s1 = sum(horas)
        s0 = n
        sy2 = sum(t**2 * y for t, y in zip(horas, consumos))
        sy1 = sum(t * y for t, y in zip(horas, consumos))
        sy0 = sum(consumos)

        # Resolver sistema 3x3 (Cramer)
        det = s4*(s2*s0 - s1*s1) - s3*(s3*s0 - s1*s2) + s2*(s3*s1 - s2*s2)
        if abs(det) < 1e-10:
            return {'a': 0, 'b': 0, 'c': sum(consumos)/n}

        a = (sy2*(s2*s0 - s1*s1) - s3*(sy1*s0 - s1*sy0) + s2*(sy1*s1 - s2*sy0)) / det
        b = (s4*(sy1*s0 - s1*sy0) - sy2*(s3*s0 - s1*s2) + s2*(s3*sy0 - sy1*s2)) / det
        c = (s4*(s2*sy0 - sy1*s1) - s3*(s3*sy0 - sy1*s2) + sy2*(s3*s1 - s2*s2)) / det

        return {'a': round(a, 6), 'b': round(b, 4), 'c': round(c, 2)}

    @staticmethod
    def avaliar(coefs: dict, t: float) -> float:
        """Avalia E(t) = at^2 + bt + c."""
        return coefs['a'] * t**2 + coefs['b'] * t + coefs['c']

    @staticmethod
    def derivada(coefs: dict, t: float) -> float:
        """Calcula E'(t) = 2at + b (taxa de variacao instantanea)."""
        return 2 * coefs['a'] * t + coefs['b']

    @staticmethod
    def ponto_critico(coefs: dict) -> dict:
        """Encontra ponto critico t* = -b/(2a)."""
        if abs(coefs['a']) < 1e-10:
            return {'t_critico': None, 'tipo': 'linear', 'valor': None}
        t_crit = -coefs['b'] / (2 * coefs['a'])
        valor = ModelagemMatematica.avaliar(coefs, t_crit)
        tipo = 'minimo' if coefs['a'] > 0 else 'maximo'
        return {'t_critico': round(t_crit, 2), 'tipo': tipo, 'valor': round(valor, 2)}

    @staticmethod
    def integral_numerica(coefs: dict, t0: float, t1: float, n_passos: int = 100) -> float:
        """Integral numerica (trapezio) - energia total consumida no intervalo."""
        dt = (t1 - t0) / n_passos
        soma = 0.5 * (ModelagemMatematica.avaliar(coefs, t0) +
                       ModelagemMatematica.avaliar(coefs, t1))
        for i in range(1, n_passos):
            soma += ModelagemMatematica.avaliar(coefs, t0 + i * dt)
        return round(soma * dt, 2)

    @staticmethod
    def r_quadrado(dados: list[dict], coefs: dict) -> float:
        """Coeficiente de determinacao R2."""
        consumos = [d['consumo_total'] for d in dados]
        media = sum(consumos) / len(consumos)
        ss_tot = sum((y - media)**2 for y in consumos)
        ss_res = sum((y - ModelagemMatematica.avaliar(coefs, d['hora']))**2
                     for d, y in zip(dados, consumos))
        return round(1 - ss_res / ss_tot, 4) if ss_tot > 0 else 0


# ============================================================
# 5. ANALISE E PREVISAO - REGRESSAO LINEAR E LOGISTICA
# ============================================================

class RegressaoLinear:
    """Regressao linear multipla para previsao de autonomia (SoC).

    Forma matricial: beta = (X^T X)^-1 X^T y
    Implementacao sem sklearn para demonstrar o raciocinio.
    """

    @staticmethod
    def _inversa_2x2(m):
        det = m[0][0]*m[1][1] - m[0][1]*m[1][0]
        if abs(det) < 1e-10:
            return None
        return [[m[1][1]/det, -m[0][1]/det], [-m[1][0]/det, m[0][0]/det]]

    @staticmethod
    def treinar(dados: list[dict]) -> dict:
        """Treina regressao linear: SoC = b0 + b1*consumo + b2*geracao."""
        n = len(dados)
        # X = [1, consumo, geracao_total]
        X = []
        y = []
        for d in dados:
            geracao = d.get('geracao_total',
                           d.get('geracao_solar', 0) + d.get('geracao_eolica', 0))
            X.append([1, d['consumo_total'], geracao])
            y.append(d['soc_bateria'])

        # beta = (X^T X)^-1 X^T y  — resolver por eliminacao de Gauss
        k = len(X[0])
        XtX = [[sum(X[i][a]*X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
        Xty = [sum(X[i][a]*y[i] for i in range(n)) for a in range(k)]

        # Eliminacao de Gauss
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

        # R2
        y_pred = [sum(beta[j]*X[i][j] for j in range(k)) for i in range(n)]
        y_med = sum(y) / n
        ss_tot = sum((yi - y_med)**2 for yi in y)
        ss_res = sum((yi - yp)**2 for yi, yp in zip(y, y_pred))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        # RMSE
        rmse = math.sqrt(ss_res / n) if n > 0 else 0

        return {
            'beta': [round(b, 4) for b in beta],
            'r2': round(r2, 4),
            'rmse': round(rmse, 2),
            'variaveis': ['intercepto', 'consumo_total', 'geracao_total'],
            'formula': f"SoC = {beta[0]:.2f} + ({beta[1]:.4f}) * consumo + ({beta[2]:.4f}) * geracao",
        }

    @staticmethod
    def prever(modelo: dict, consumo: float, geracao: float) -> float:
        """Preve SoC com base no modelo treinado."""
        b = modelo['beta']
        return max(0, min(100, round(b[0] + b[1]*consumo + b[2]*geracao, 1)))


class RegressaoLogistica:
    """Regressao logistica para classificacao de cenarios criticos.

    Sigmoid: sigma(z) = 1 / (1 + e^(-z))
    Treinamento por gradient descent na funcao de custo cross-entropy.
    """

    @staticmethod
    def _sigmoid(z: float) -> float:
        z = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z))

    @staticmethod
    def treinar(dados: list[dict], lr: float = 0.5, epocas: int = 5000) -> dict:
        """Treina regressao logistica por gradient descent.

        Features: SoC, consumo, geracao, modulos_ativos, eficiencia
        Target: critico (0 ou 1)
        """
        n = len(dados)
        # Normalizar features (min-max)
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
        mins = [min(features_raw[i][j] for i in range(n)) for j in range(k)]
        maxs = [max(features_raw[i][j] for i in range(n)) for j in range(k)]
        ranges = [maxs[j] - mins[j] if maxs[j] != mins[j] else 1 for j in range(k)]

        X = [[1.0] + [(features_raw[i][j] - mins[j]) / ranges[j]
                       for j in range(k)] for i in range(n)]
        nf = k + 1

        # Inicializar pesos
        w = [0.0] * nf

        # Gradient descent
        historico_custo = []
        for epoca in range(epocas):
            custo = 0
            grad = [0.0] * nf
            for i in range(n):
                z = sum(w[j] * X[i][j] for j in range(nf))
                p = RegressaoLogistica._sigmoid(z)
                erro = p - y[i]
                for j in range(nf):
                    grad[j] += erro * X[i][j]
                # Cross-entropy
                p_clip = max(1e-10, min(1-1e-10, p))
                custo += -(y[i] * math.log(p_clip) + (1-y[i]) * math.log(1-p_clip))

            for j in range(nf):
                w[j] -= lr * grad[j] / n
            if epoca % 100 == 0:
                historico_custo.append(round(custo / n, 4))

        # Acuracia
        acertos = 0
        for i in range(n):
            z = sum(w[j] * X[i][j] for j in range(nf))
            pred = 1 if RegressaoLogistica._sigmoid(z) >= 0.5 else 0
            if pred == y[i]:
                acertos += 1
        acuracia = acertos / n

        # Matriz de confusao
        tp = fp = tn = fn = 0
        for i in range(n):
            z = sum(w[j] * X[i][j] for j in range(nf))
            pred = 1 if RegressaoLogistica._sigmoid(z) >= 0.5 else 0
            if pred == 1 and y[i] == 1: tp += 1
            elif pred == 1 and y[i] == 0: fp += 1
            elif pred == 0 and y[i] == 0: tn += 1
            else: fn += 1

        return {
            'pesos': [round(wj, 4) for wj in w],
            'acuracia': round(acuracia, 4),
            'matriz_confusao': {'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn},
            'normalizacao': {'mins': mins, 'ranges': ranges},
            'variaveis': ['intercepto', 'soc_bateria', 'consumo_total', 'geracao_total', 'modulos_ativos', 'eficiencia_rede'],
            'historico_custo': historico_custo,
        }

    @staticmethod
    def prever(modelo: dict, soc: float, consumo: float, modulos: int,
               geracao: float = 30.0, eficiencia: float = 0.88) -> dict:
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


# ============================================================
# 6. ANALISE ESG E SUSTENTABILIDADE
# ============================================================

class AnaliseESG:
    """Analise de sustentabilidade e governanca da infraestrutura."""

    @staticmethod
    def calcular_metricas(dados: list[dict], grafo: GrafoColonia) -> dict:
        """Calcula metricas ESG da colonia."""
        # Energia renovavel
        total_geracao = sum(d['geracao_solar'] + d['geracao_eolica'] for d in dados)
        total_consumo = sum(d['consumo_total'] for d in dados)
        pct_renovavel = (total_geracao / total_consumo * 100) if total_consumo > 0 else 0

        # Eficiencia media da rede
        efic_media = sum(d['eficiencia_rede'] for d in dados) / len(dados) if dados else 0

        # Perdas na transmissao (estimativa baseada no grafo)
        efic_rede = grafo.eficiencia_rede()
        perda_estimada = (1 - efic_media) * total_consumo

        # Pegada de carbono evitada (vs geradores diesel)
        # Fator emissao diesel: 0.7 kgCO2/kWh
        co2_evitado = total_geracao * 0.7

        # Score ESG composto (0-100)
        score_e = min(100, pct_renovavel)  # Environmental
        score_s = min(100, sum(1 for d in dados if d['modulos_ativos'] >= 6) / len(dados) * 100)  # Social
        score_g = min(100, efic_media * 100)  # Governance
        score_esg = round((score_e * 0.4 + score_s * 0.3 + score_g * 0.3), 1)

        # Prioridade de sistemas criticos
        modulos_essenciais = [c for c, m in MODULOS.items() if m['prioridade'] <= 3]
        consumo_essencial = sum(MODULOS[c]['consumo_kwh'] for c in modulos_essenciais)
        consumo_total_mod = sum(m['consumo_kwh'] for m in MODULOS.values())
        pct_essencial = round(consumo_essencial / consumo_total_mod * 100, 1)

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
            'recomendacoes': AnaliseESG._gerar_recomendacoes(
                pct_renovavel, efic_media, perda_estimada),
        }

    @staticmethod
    def _gerar_recomendacoes(pct_renov, efic, perda):
        recs = []
        if pct_renov < 80:
            recs.append({
                'area': 'Energia Renovavel',
                'acao': f'Aumentar capacidade solar/eolica (atual: {pct_renov:.0f}% renovavel)',
                'impacto': 'alto',
            })
        if efic < 0.90:
            recs.append({
                'area': 'Eficiencia da Rede',
                'acao': f'Otimizar rotas de distribuicao (eficiencia atual: {efic:.1%})',
                'impacto': 'medio',
            })
        if perda > 50:
            recs.append({
                'area': 'Reducao de Perdas',
                'acao': f'Reduzir perdas na transmissao ({perda:.0f} kWh estimados)',
                'impacto': 'medio',
            })
        recs.append({
            'area': 'Expansao Planejada',
            'acao': 'Priorizar conexoes curtas ao expandir, minimizando perdas',
            'impacto': 'alto',
        })
        recs.append({
            'area': 'Governanca',
            'acao': 'Manter sistemas essenciais (prioridade 1-3) com redundancia energetica',
            'impacto': 'alto',
        })
        return recs


# ============================================================
# 7. SISTEMA INTEGRADO
# ============================================================

class SIGIC:
    """Sistema Inteligente de Gerenciamento da Infraestrutura da Colonia."""

    def __init__(self):
        # Grafo da rede
        self.grafo = GrafoColonia(LISTA_MODULOS, CONEXOES)

        # Dados energeticos
        self.dados_energia = carregar_dados_energia(
            os.path.join(AUX_DIR, 'dados_energia.csv'))
        self.historico = carregar_historico_cenarios(
            os.path.join(AUX_DIR, 'historico_cenarios.csv'))

        # Modelagem matematica
        self.coefs_modelo = ModelagemMatematica.ajustar_modelo(self.dados_energia)
        self.r2_modelo = ModelagemMatematica.r_quadrado(self.dados_energia, self.coefs_modelo)

        # Modelos ML
        self.modelo_linear = RegressaoLinear.treinar(self.historico)
        self.modelo_logistico = RegressaoLogistica.treinar(self.historico)

        # ESG
        self.metricas_esg = AnaliseESG.calcular_metricas(self.dados_energia, self.grafo)

    def visao_geral(self) -> dict:
        ultimo = self.dados_energia[-1]
        geracao = ultimo['geracao_solar'] + ultimo['geracao_eolica']
        balanco = geracao - ultimo['consumo_total']

        # Estado de cada modulo
        status_modulos = {}
        for cod, mod in MODULOS.items():
            status_modulos[cod] = {**mod}

        return {
            'modulos': status_modulos,
            'energia': {
                'soc': ultimo['soc_bateria'],
                'geracao_solar': ultimo['geracao_solar'],
                'geracao_eolica': ultimo['geracao_eolica'],
                'geracao_total': geracao,
                'consumo': ultimo['consumo_total'],
                'balanco': round(balanco, 1),
                'eficiencia': ultimo['eficiencia_rede'],
            },
            'rede': self.grafo.eficiencia_rede(),
            'hora_atual': ultimo['hora'],
            'score_esg': self.metricas_esg['score_esg'],
        }

    def dados_rede(self) -> dict:
        adj_lista = {v: [(viz, w) for viz, w in self.grafo.adj_lista[v]]
                     for v in self.grafo.vertices}
        return {
            'vertices': self.grafo.vertices,
            'adj_lista': adj_lista,
            'adj_matriz': self.grafo.adj_matriz,
            'nomes_vertices': [MODULOS[v]['nome'] for v in self.grafo.vertices],
            'eficiencia': self.grafo.eficiencia_rede(),
            'articulacoes': self.grafo.detectar_pontos_articulacao(),
            'conexoes': CONEXOES,
        }

    def executar_bfs(self, origem: str) -> dict:
        return self.grafo.bfs(origem)

    def executar_dfs(self, origem: str) -> dict:
        return self.grafo.dfs(origem)

    def executar_dijkstra(self, origem: str, destino: str) -> dict:
        return self.grafo.caminho_minimo(origem, destino)

    def dados_energia_api(self) -> dict:
        return {
            'horarios': [d['hora'] for d in self.dados_energia],
            'solar': [d['geracao_solar'] for d in self.dados_energia],
            'eolica': [d['geracao_eolica'] for d in self.dados_energia],
            'consumo': [d['consumo_total'] for d in self.dados_energia],
            'soc': [d['soc_bateria'] for d in self.dados_energia],
            'eficiencia': [d['eficiencia_rede'] for d in self.dados_energia],
            'temp': [d['temp_externa'] for d in self.dados_energia],
        }

    def dados_modelagem(self) -> dict:
        coefs = self.coefs_modelo
        pc = ModelagemMatematica.ponto_critico(coefs)
        horas = list(range(0, 25))
        valores = [round(ModelagemMatematica.avaliar(coefs, t), 1) for t in horas]
        derivadas = [round(ModelagemMatematica.derivada(coefs, t), 2) for t in horas]
        integral = ModelagemMatematica.integral_numerica(coefs, 0, 24)

        return {
            'coeficientes': coefs,
            'formula': f"E(t) = {coefs['a']}t^2 + ({coefs['b']})t + {coefs['c']}",
            'derivada_formula': f"E'(t) = {2*coefs['a']:.6f}t + ({coefs['b']})",
            'r2': self.r2_modelo,
            'ponto_critico': pc,
            'horas': horas,
            'valores_modelo': valores,
            'derivadas': derivadas,
            'energia_total_24h': integral,
            'dados_reais': [d['consumo_total'] for d in self.dados_energia],
            'horas_reais': [d['hora'] for d in self.dados_energia],
        }

    def dados_previsao(self) -> dict:
        return {
            'regressao_linear': self.modelo_linear,
            'regressao_logistica': {
                'acuracia': self.modelo_logistico['acuracia'],
                'matriz_confusao': self.modelo_logistico['matriz_confusao'],
                'variaveis': self.modelo_logistico['variaveis'],
                'historico_custo': self.modelo_logistico['historico_custo'],
            },
        }

    def prever_soc(self, consumo: float, geracao: float) -> dict:
        soc_previsto = RegressaoLinear.prever(self.modelo_linear, consumo, geracao)
        estado = RegressaoLogistica.prever(
            self.modelo_logistico, soc_previsto, consumo, 8,
            geracao=geracao, eficiencia=0.88)
        return {
            'soc_previsto': soc_previsto,
            'estado': estado,
            'modelo_linear': self.modelo_linear['formula'],
        }

    def dados_esg(self) -> dict:
        return self.metricas_esg


# ============================================================
# 8. GERACAO DE PDF - REDE DA COLONIA
# ============================================================

def gerar_rede_pdf(sistema: SIGIC, caminho: str) -> bool:
    """Gera diagrama da rede em PDF usando fpdf2."""
    try:
        from fpdf import FPDF
    except ImportError:
        print("  fpdf2 nao instalado. Execute: pip install fpdf2")
        return False

    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'Rede da Colonia Aurora Siger - SIGIC', ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, 'Fase IV - Energia para Sobreviver | FIAP 2026 | Marcelo Baldin RM568746', ln=True, align='C')
    pdf.ln(5)

    # Posicoes dos modulos no diagrama (x, y)
    cx, cy = 148, 120
    posicoes = {
        'ARM': (cx, cy - 55),
        'CTR': (cx - 60, cy - 20),
        'HAB': (cx + 60, cy - 20),
        'OXI': (cx + 90, cy + 30),
        'COM': (cx - 90, cy + 30),
        'MED': (cx - 40, cy + 50),
        'AGR': (cx + 40, cy + 50),
        'LAB': (cx, cy + 80),
    }

    # Desenhar arestas
    pdf.set_draw_color(100, 150, 200)
    pdf.set_line_width(0.4)
    for u, v, w in CONEXOES:
        x1, y1 = posicoes[u]
        x2, y2 = posicoes[v]
        pdf.line(x1, y1, x2, y2)
        mx, my = (x1+x2)/2, (y1+y2)/2
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(150, 100, 50)
        pdf.text(mx-3, my-1, f"{w} kWh")

    # Desenhar vertices
    for cod, (x, y) in posicoes.items():
        mod = MODULOS[cod]
        cor = (34, 197, 94) if mod['prioridade'] <= 2 else \
              (59, 130, 246) if mod['prioridade'] <= 4 else (148, 163, 184)
        pdf.set_fill_color(*cor)
        pdf.set_draw_color(*cor)
        pdf.ellipse(x-12, y-8, 24, 16, style='F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.text(x-10, y-1, cod)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Helvetica', '', 6)
        pdf.text(x-12, y+6, mod['nome'][:18])

    # Legenda
    pdf.ln(100)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 8, 'Legenda', ln=True)
    pdf.set_font('Helvetica', '', 8)
    pdf.cell(0, 5, 'Verde: Prioridade 1-2 (essencial)  |  Azul: Prioridade 3-4  |  Cinza: Prioridade 5-6', ln=True)
    pdf.cell(0, 5, 'Pesos nas arestas: custo energetico de transmissao (kWh)', ln=True)

    # Tabela de modulos
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 8, 'Modulos da Colonia', ln=True)
    pdf.set_font('Helvetica', 'B', 8)
    cols = [30, 45, 25, 20, 25, 80]
    headers = ['Codigo', 'Nome', 'Consumo', 'Prior.', 'Arm.(kWh)', 'Descricao']
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 6, h, border=1)
    pdf.ln()
    pdf.set_font('Helvetica', '', 7)
    for cod in LISTA_MODULOS:
        m = MODULOS[cod]
        vals = [cod, m['nome'][:18], str(m['consumo_kwh']), str(m['prioridade']),
                str(m['capacidade_arm_kwh']), m['descricao'][:40]]
        for i, v in enumerate(vals):
            pdf.cell(cols[i], 5, v, border=1)
        pdf.ln()

    # Matriz de adjacencia
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 8, 'Matriz de Adjacencia', ln=True)
    pdf.set_font('Helvetica', 'B', 7)
    cw = 15
    pdf.cell(cw, 5, '', border=1)
    for v in LISTA_MODULOS:
        pdf.cell(cw, 5, v, border=1, align='C')
    pdf.ln()
    pdf.set_font('Helvetica', '', 7)
    for i, vi in enumerate(LISTA_MODULOS):
        pdf.set_font('Helvetica', 'B', 7)
        pdf.cell(cw, 5, vi, border=1)
        pdf.set_font('Helvetica', '', 7)
        for j in range(len(LISTA_MODULOS)):
            val = sistema.grafo.adj_matriz[i][j]
            pdf.cell(cw, 5, str(val) if val > 0 else '-', border=1, align='C')
        pdf.ln()

    pdf.output(caminho)
    return True


def gerar_documentacao_pdf(sistema: SIGIC, caminho: str) -> bool:
    """Gera documentacao complementar em PDF."""
    try:
        from fpdf import FPDF
    except ImportError:
        return False

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    larg = 170

    def titulo(t):
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(0, 80, 160)
        pdf.cell(0, 10, t, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    def txt(t, bold=False):
        pdf.set_font('Helvetica', 'B' if bold else '', 10)
        pdf.multi_cell(larg, 5, t)
        pdf.ln(1)

    # Capa
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 22)
    pdf.ln(40)
    pdf.cell(0, 12, 'SIGIC', ln=True, align='C')
    pdf.set_font('Helvetica', '', 14)
    pdf.cell(0, 8, 'Sistema Inteligente de Gerenciamento', ln=True, align='C')
    pdf.cell(0, 8, 'da Infraestrutura da Colonia', ln=True, align='C')
    pdf.ln(15)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, 'Fase IV - Energia para Sobreviver', ln=True, align='C')
    pdf.cell(0, 7, 'FIAP 2026 - Ciencias da Computacao', ln=True, align='C')
    pdf.ln(8)
    pdf.cell(0, 7, 'Marcelo Bastianello Baldin - RM568746 - Grupo 13', ln=True, align='C')

    # Infraestrutura
    pdf.add_page()
    titulo('1. Infraestrutura da Colonia')
    txt('A colonia Aurora Siger possui 8 modulos criticos organizados em uma '
        'rede de distribuicao energetica. Cada modulo tem consumo, prioridade '
        'e capacidade de armazenamento definidos.')
    for cod in LISTA_MODULOS:
        m = MODULOS[cod]
        txt(f"{cod} - {m['nome']}: consumo {m['consumo_kwh']} kWh, "
            f"prioridade {m['prioridade']}, {m['descricao']}")

    # Grafos
    pdf.add_page()
    titulo('2. Representacao em Grafos')
    txt('A rede e representada como grafo ponderado nao-dirigido:')
    txt('- Vertices: 8 modulos da colonia')
    txt(f'- Arestas: {len(CONEXOES)} conexoes com peso = custo energetico (kWh)')
    txt('- Representacoes: lista de adjacencia (dicionario) e matriz de adjacencia (lista de listas)')
    efic = sistema.grafo.eficiencia_rede()
    txt(f'Metricas: grau medio {efic["grau_medio"]}, densidade {efic["densidade"]}, '
        f'diametro {efic["diametro"]} kWh, custo medio {efic["custo_medio"]} kWh')

    # Algoritmos
    pdf.add_page()
    titulo('3. Algoritmos de Redes')
    txt('3.1 BFS (Busca em Largura)', bold=True)
    txt('Explora a rede nivel a nivel usando fila (deque). Complexidade O(V+E). '
        'Usado para verificar alcancabilidade e encontrar caminho com menor numero de saltos.')
    txt('3.2 DFS (Busca em Profundidade)', bold=True)
    txt('Explora em profundidade usando recursao/pilha. Complexidade O(V+E). '
        'Usado para detectar componentes conectados e ciclos.')
    txt('3.3 Dijkstra (Caminho Minimo)', bold=True)
    txt('Encontra caminho de menor custo usando heap (heapq). Complexidade O((V+E) log V). '
        'Usado para otimizar rotas de distribuicao de energia entre modulos.')

    # Modelagem
    pdf.add_page()
    titulo('4. Modelagem Matematica')
    coefs = sistema.coefs_modelo
    txt(f'Funcao de consumo: E(t) = {coefs["a"]}t^2 + ({coefs["b"]})t + {coefs["c"]}')
    txt(f'Derivada: E\'(t) = {2*coefs["a"]:.6f}t + ({coefs["b"]})')
    pc = ModelagemMatematica.ponto_critico(coefs)
    if pc['t_critico']:
        txt(f'Ponto critico: t* = {pc["t_critico"]}h ({pc["tipo"]}, E = {pc["valor"]} kWh)')
    txt(f'R2 do ajuste: {sistema.r2_modelo}')
    integral = ModelagemMatematica.integral_numerica(coefs, 0, 24)
    txt(f'Energia total consumida em 24h (integral): {integral} kWh')

    # Previsao
    pdf.add_page()
    titulo('5. Previsao e Classificacao')
    txt('5.1 Regressao Linear (Previsao de SoC)', bold=True)
    ml = sistema.modelo_linear
    txt(f'Formula: {ml["formula"]}')
    txt(f'R2: {ml["r2"]}, RMSE: {ml["rmse"]}')
    txt('5.2 Regressao Logistica (Classificacao Critico/Normal)', bold=True)
    mlog = sistema.modelo_logistico
    txt(f'Acuracia: {mlog["acuracia"]:.1%}')
    mc = mlog['matriz_confusao']
    txt(f'Matriz de confusao: VP={mc["tp"]} FP={mc["fp"]} VN={mc["tn"]} FN={mc["fn"]}')

    # ESG
    pdf.add_page()
    titulo('6. Sustentabilidade e ESG')
    esg = sistema.metricas_esg
    txt(f'Score ESG: {esg["score_esg"]}/100')
    txt(f'Energia renovavel: {esg["pct_renovavel"]:.1f}%')
    txt(f'CO2 evitado: {esg["co2_evitado_kg"]:.1f} kg')
    txt(f'Eficiencia media: {esg["eficiencia_media"]:.1%}')
    for rec in esg['recomendacoes']:
        txt(f'- [{rec["impacto"].upper()}] {rec["area"]}: {rec["acao"]}')

    pdf.output(caminho)
    return True


# ============================================================
# 9. APLICACAO FLASK
# ============================================================

app = Flask(__name__, template_folder=os.path.join(AUX_DIR, 'templates'))
app.secret_key = 'sigic-fase4-2026-fiap-rm568746'

sistema: SIGIC | None = None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usr = request.form.get('usuario', '')
        pwd = request.form.get('senha', '')
        if usr in USUARIOS and USUARIOS[usr]['senha'] == pwd:
            session['usuario'] = usr
            session['nome'] = USUARIOS[usr]['nome']
            return redirect(url_for('dashboard'))
        return render_template('login.html', erro='Credenciais invalidas')
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', nome=session.get('nome'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------- API ----------

@app.route('/api/visao-geral')
@login_required
def api_visao_geral():
    return jsonify(sistema.visao_geral())


@app.route('/api/rede')
@login_required
def api_rede():
    return jsonify(sistema.dados_rede())


@app.route('/api/bfs/<origem>')
@login_required
def api_bfs(origem):
    if origem not in LISTA_MODULOS:
        return jsonify({'erro': 'Modulo invalido'}), 400
    return jsonify(sistema.executar_bfs(origem))


@app.route('/api/dfs/<origem>')
@login_required
def api_dfs(origem):
    if origem not in LISTA_MODULOS:
        return jsonify({'erro': 'Modulo invalido'}), 400
    return jsonify(sistema.executar_dfs(origem))


@app.route('/api/dijkstra/<origem>/<destino>')
@login_required
def api_dijkstra(origem, destino):
    if origem not in LISTA_MODULOS or destino not in LISTA_MODULOS:
        return jsonify({'erro': 'Modulo invalido'}), 400
    return jsonify(sistema.executar_dijkstra(origem, destino))


@app.route('/api/energia')
@login_required
def api_energia():
    return jsonify(sistema.dados_energia_api())


@app.route('/api/modelagem')
@login_required
def api_modelagem():
    return jsonify(sistema.dados_modelagem())


@app.route('/api/previsao')
@login_required
def api_previsao():
    return jsonify(sistema.dados_previsao())


@app.route('/api/prever', methods=['POST'])
@login_required
def api_prever():
    dados = request.get_json()
    consumo = float(dados.get('consumo', 180))
    geracao = float(dados.get('geracao', 30))
    return jsonify(sistema.prever_soc(consumo, geracao))


@app.route('/api/esg')
@login_required
def api_esg():
    return jsonify(sistema.dados_esg())


@app.route('/api/gerar-pdfs')
@login_required
def api_gerar_pdfs():
    ok1 = gerar_rede_pdf(sistema, os.path.join(BASE_DIR, 'rede_colonia.pdf'))
    ok2 = gerar_documentacao_pdf(sistema, os.path.join(BASE_DIR, 'documentacao_complementar.pdf'))
    if ok1 and ok2:
        return jsonify({'status': 'ok', 'mensagem': 'PDFs gerados com sucesso'})
    return jsonify({'status': 'erro', 'mensagem': 'fpdf2 nao instalado'}), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    sistema = SIGIC()

    print()
    print('=' * 60)
    print('  SIGIC - Gerenciamento da Infraestrutura da Colonia')
    print('  Fase IV - Energia para Sobreviver | FIAP 2026')
    print('=' * 60)
    print()

    visao = sistema.visao_geral()
    print(f'  Modulos: {len(MODULOS)} configurados')
    print(f'  Conexoes: {len(CONEXOES)} arestas no grafo')
    print(f'  SoC bateria: {visao["energia"]["soc"]}%')
    print(f'  Score ESG: {visao["score_esg"]}/100')
    print()

    rede = sistema.grafo.eficiencia_rede()
    print(f'  Rede: {rede["vertices"]} vertices, {rede["arestas"]} arestas')
    print(f'  Grau medio: {rede["grau_medio"]}, Densidade: {rede["densidade"]}')
    print(f'  Diametro: {rede["diametro"]} kWh')
    print()

    print(f'  Regressao Linear R2: {sistema.modelo_linear["r2"]}')
    print(f'  Regressao Logistica Acuracia: {sistema.modelo_logistico["acuracia"]:.1%}')
    print(f'  Modelagem R2: {sistema.r2_modelo}')
    print()
    print('  Acesse: http://localhost:5050')
    print('  Usuario: usuario | Senha: senha')
    print('  Para encerrar: Ctrl+C')
    print()

    app.run(host='0.0.0.0', port=5050, debug=False)
