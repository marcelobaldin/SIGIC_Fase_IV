#!/usr/bin/env python3
"""Gera relatorio tecnico do SIGIC em PDF."""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_SITE = os.path.join(BASE_DIR, 'venv', 'lib')
for root, dirs, files in os.walk(VENV_SITE):
    if 'site-packages' in dirs:
        sys.path.insert(0, os.path.join(root, 'site-packages'))
        break

from fpdf import FPDF

class Relatorio(FPDF):
    cor_titulo = (0, 70, 140)
    cor_sub = (30, 100, 160)
    cor_accent = (200, 120, 0)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5, 'SIGIC - Relatório Técnico | Fase IV - FIAP 2026', align='L')
            self.cell(0, 5, f'Página {self.page_no()}', align='R', ln=True)
            self.ln(2)
            self.set_draw_color(180, 180, 180)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, 'Marcelo Bastianello Baldin - RM568746 - Grupo 13', align='C')

    def titulo_secao(self, num, texto):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(*self.cor_titulo)
        self.cell(0, 10, f'{num}. {texto}', ln=True)
        self.set_draw_color(*self.cor_titulo)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def subtitulo(self, texto):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.cor_sub)
        self.cell(0, 7, texto, ln=True)
        self.ln(1)
        self.set_text_color(0, 0, 0)

    def corpo(self, texto):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 5, texto)
        self.ln(2)

    def destaque(self, texto):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.cor_accent)
        self.multi_cell(0, 5, texto)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def item(self, texto):
        self.set_font('Helvetica', '', 10)
        self.cell(5, 5, '-')
        self.multi_cell(0, 5, texto)
        self.ln(1)

    def tabela(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 // len(headers)] * len(headers)
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(0, 70, 140)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6, h, border=1, fill=True, align='C')
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', '', 8)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(240, 245, 250)
            else:
                self.set_fill_color(255, 255, 255)
            for i, val in enumerate(row):
                self.cell(col_widths[i], 5, str(val), border=1, fill=True, align='C')
            self.ln()
        self.ln(3)

    def formula_box(self, formula):
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(180, 180, 180)
        self.set_font('Courier', 'B', 11)
        w = self.get_string_width(formula) + 20
        x = (210 - w) / 2
        self.set_x(x)
        self.cell(w, 8, formula, border=1, fill=True, align='C', ln=True)
        self.set_font('Helvetica', '', 10)
        self.ln(3)


def main():
    pdf = Relatorio()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ========== CAPA ==========
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(0, 70, 140)
    pdf.cell(0, 14, 'SIGIC', ln=True, align='C')
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 9, 'Sistema Inteligente de Gerenciamento', ln=True, align='C')
    pdf.cell(0, 9, 'da Infraestrutura da Colônia', ln=True, align='C')
    pdf.ln(8)
    pdf.set_draw_color(200, 120, 0)
    pdf.set_line_width(0.8)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(8)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(200, 120, 0)
    pdf.cell(0, 8, 'Relatório Técnico', ln=True, align='C')
    pdf.ln(15)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, 'Fase IV - Energia para Sobreviver', ln=True, align='C')
    pdf.cell(0, 7, 'FIAP 2026 - Ciências da Computação', ln=True, align='C')
    pdf.ln(6)
    pdf.cell(0, 7, 'Marcelo Bastianello Baldin', ln=True, align='C')
    pdf.cell(0, 7, 'RM568746 - Grupo 13', ln=True, align='C')
    pdf.ln(30)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 5, 'Maio 2026', ln=True, align='C')

    # ========== 1. INTRODUÇÃO ==========
    pdf.add_page()
    pdf.titulo_secao(1, 'Introdução')

    pdf.corpo(
        'O SIGIC (Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia) é uma '
        'plataforma computacional desenvolvida para simular o gerenciamento energético de uma '
        'colônia marciana. O sistema integra conceitos de estruturas de dados, teoria dos grafos, '
        'cálculo diferencial, aprendizado de máquina e análise de sustentabilidade (ESG) em uma '
        'aplicação web interativa.'
    )
    pdf.corpo(
        'O objetivo principal é demonstrar como técnicas computacionais e estatísticas podem ser '
        'aplicadas para otimizar a distribuição de energia, prever cenários críticos e garantir a '
        'sobrevivência de uma base extraterrestre em condições adversas.'
    )

    pdf.subtitulo('1.1 Objetivos Específicos')
    pdf.item('Modelar a rede de distribuição energética como um grafo ponderado não-dirigido')
    pdf.item('Aplicar algoritmos de busca (BFS, DFS) e caminho mínimo (Dijkstra) para otimizar rotas')
    pdf.item('Construir modelo matemático quadrático do consumo energético com cálculo diferencial')
    pdf.item('Implementar regressão linear para previsão do estado de carga (SoC) da bateria')
    pdf.item('Implementar regressão logística para classificação de cenários críticos')
    pdf.item('Avaliar a sustentabilidade da operação com métricas ESG')

    # ========== 2. CENÁRIO SIMULADO ==========
    pdf.add_page()
    pdf.titulo_secao(2, 'Cenário Simulado')

    pdf.subtitulo('2.1 A Colônia Aurora Siger')
    pdf.corpo(
        'A simulação modela a colônia Aurora Siger, uma base marciana composta por 8 módulos '
        'interconectados por uma rede de distribuição de energia. A base opera em um ambiente '
        'hostil, com temperaturas externas variando de -30°C a -65°C, e depende exclusivamente '
        'de fontes renováveis (solar e eólica) para gerar energia.'
    )
    pdf.corpo(
        'Cada módulo possui função específica, consumo energético diferenciado, capacidade de '
        'armazenamento local e nível de prioridade que define a ordem de corte em caso de '
        'emergência. A energia é gerada centralmente e distribuída pela rede, com custos de '
        'transmissão proporcionais à distância e ao tipo de conexão.'
    )

    pdf.subtitulo('2.2 Módulos da Colônia')
    pdf.tabela(
        ['Código', 'Nome', 'Consumo (kWh)', 'Prioridade', 'Arm. (kWh)', 'Tipo'],
        [
            ['HAB', 'Habitação', '45', '1', '100', 'essencial'],
            ['CTR', 'Centro de Controle', '30', '2', '50', 'essencial'],
            ['ARM', 'Armazenamento', '10', '3', '500', 'infraestrutura'],
            ['OXI', 'Prod. Oxigênio', '50', '1', '120', 'essencial'],
            ['COM', 'Comunicação', '20', '4', '30', 'essencial'],
            ['MED', 'Suporte Médico', '25', '3', '40', 'essencial'],
            ['AGR', 'Agricultura', '35', '5', '80', 'suporte'],
            ['LAB', 'Laboratório', '40', '6', '60', 'operacional'],
        ],
        [20, 35, 28, 22, 22, 28]
    )
    pdf.corpo(
        'O consumo total dos 8 módulos é de 255 kWh. Os módulos essenciais (prioridade 1-3) '
        'representam 62,7% do consumo total e são os últimos a serem desligados em emergências.'
    )

    pdf.subtitulo('2.3 Dados de Telemetria')
    pdf.corpo(
        'A simulação utiliza dois conjuntos de dados. O primeiro (dados_energia.csv) contém 12 '
        'registros de telemetria energética coletados a cada 2 horas ao longo de um ciclo de 24 '
        'horas, incluindo: geração solar, geração eólica, consumo total, estado de carga (SoC) da '
        'bateria, temperatura externa, módulos ativos e eficiência da rede.'
    )
    pdf.corpo(
        'O segundo conjunto (historico_cenarios.csv) contém 30 cenários históricos usados para '
        'treinamento dos modelos de aprendizado de máquina, com rotulação binária (0 = normal, '
        '1 = crítico). Dos 30 cenários, 17 são normais e 13 são críticos.'
    )

    # ========== 3. ESTRUTURAS DE DADOS ==========
    pdf.add_page()
    pdf.titulo_secao(3, 'Estruturas de Dados')

    pdf.corpo(
        'O sistema utiliza as quatro estruturas de dados fundamentais exigidas: listas, tuplas, '
        'dicionários e matrizes (listas de listas).'
    )

    pdf.subtitulo('3.1 Tuplas')
    pdf.corpo(
        'Informações imutáveis dos módulos são armazenadas em tuplas (MODULOS_INFO), garantindo '
        'que dados como código, nome, tipo e prioridade não sejam alterados durante a execução. '
        'Exemplo: ("HAB", "Habitacao", "essencial", 1).'
    )

    pdf.subtitulo('3.2 Dicionários')
    pdf.corpo(
        'Dados operacionais de cada módulo são armazenados no dicionário MODULOS, permitindo '
        'acesso O(1) por código. Cada entrada contém consumo, prioridade, capacidade de '
        'armazenamento, distância ao hub, frequência de comunicação e status.'
    )

    pdf.subtitulo('3.3 Listas')
    pdf.corpo(
        'Listas são usadas para: iteração sobre módulos (LISTA_MODULOS), definição de conexões '
        '(CONEXOES como lista de tuplas), armazenamento de dados temporais e representação de '
        'adjacência no grafo.'
    )

    pdf.subtitulo('3.4 Matrizes (Listas de Listas)')
    pdf.corpo(
        'A matriz de adjacência do grafo é implementada como lista de listas (8x8), onde '
        'adj_matriz[i][j] armazena o custo de transmissão entre os módulos i e j, ou 0 se não '
        'há conexão direta.'
    )

    # ========== 4. GRAFOS ==========
    pdf.add_page()
    pdf.titulo_secao(4, 'Modelagem em Grafos')

    pdf.subtitulo('4.1 Representação da Rede')
    pdf.corpo(
        'A rede da colônia é modelada como um grafo ponderado não-dirigido G = (V, E), onde:'
    )
    pdf.item('V = {HAB, CTR, ARM, OXI, COM, MED, AGR, LAB} (8 vértices = módulos)')
    pdf.item('E = 14 arestas ponderadas (conexões físicas com custo em kWh)')
    pdf.item('Peso w(u,v) = custo energético de transmissão entre módulos u e v')
    pdf.ln(2)
    pdf.corpo(
        'O grafo utiliza duas representações simultâneas: lista de adjacência (dicionário de '
        'listas) para eficiência nas travessias, e matriz de adjacência (lista de listas 8x8) '
        'para verificação rápida de existência de arestas.'
    )

    pdf.subtitulo('4.2 Métricas da Rede')
    pdf.tabela(
        ['Métrica', 'Valor', 'Interpretação'],
        [
            ['Vértices', '8', 'Módulos da colônia'],
            ['Arestas', '14', 'Conexões físicas'],
            ['Grau médio', '3,50', 'Média de conexões por módulo'],
            ['Densidade', '0,50', '50% das conexões possíveis existem'],
            ['Custo médio', '9,36 kWh', 'Custo médio de transmissão'],
            ['Diâmetro', '26 kWh', 'Maior menor caminho (peso total)'],
        ],
        [35, 30, 90]
    )
    pdf.corpo(
        'A densidade de 0,50 indica que metade de todas as conexões possíveis entre módulos '
        'existem, proporcionando boa redundância sem custo excessivo. A ausência de pontos de '
        'articulação confirma que nenhum módulo é isolável pela falha de um único nó.'
    )

    pdf.subtitulo('4.3 Conexões da Rede')
    pdf.tabela(
        ['Origem', 'Destino', 'Custo (kWh)'],
        [
            ['ARM', 'HAB', '8'], ['ARM', 'CTR', '5'], ['ARM', 'OXI', '10'],
            ['ARM', 'COM', '12'], ['CTR', 'HAB', '6'], ['CTR', 'COM', '4'],
            ['CTR', 'MED', '7'], ['HAB', 'MED', '9'], ['HAB', 'AGR', '11'],
            ['HAB', 'OXI', '7'], ['OXI', 'AGR', '15'], ['COM', 'LAB', '13'],
            ['MED', 'LAB', '10'], ['AGR', 'LAB', '14'],
        ],
        [40, 40, 40]
    )

    # ========== 5. ALGORITMOS DE GRAFOS ==========
    pdf.add_page()
    pdf.titulo_secao(5, 'Algoritmos de Grafos')

    pdf.subtitulo('5.1 BFS - Busca em Largura')
    pdf.corpo(
        'O BFS (Breadth-First Search) explora o grafo nível a nível, utilizando uma fila (deque) '
        'como estrutura auxiliar. A complexidade é O(V+E) = O(8+14) = O(22).'
    )
    pdf.destaque('Propósito no SIGIC:')
    pdf.item('Verificar alcançabilidade: confirmar que todos os módulos são acessíveis a partir de qualquer ponto')
    pdf.item('Encontrar caminho com menor número de saltos (hops) entre módulos')
    pdf.item('Diagnosticar a conectividade da rede após falhas')

    pdf.destaque('Resultado - BFS a partir de ARM:')
    pdf.corpo(
        'Ordem de visita: ARM -> HAB -> CTR -> OXI -> COM -> MED -> AGR -> LAB\n'
        'Distâncias (saltos): ARM=0, HAB=1, CTR=1, OXI=1, COM=1, MED=2, AGR=2, LAB=2\n\n'
        'Interpretação: ARM alcança 4 módulos em 1 salto (HAB, CTR, OXI, COM) e os demais '
        'em 2 saltos, confirmando posição central na rede.'
    )

    pdf.subtitulo('5.2 DFS - Busca em Profundidade')
    pdf.corpo(
        'O DFS (Depth-First Search) explora o grafo indo o mais fundo possível antes de retroceder, '
        'usando recursão (pilha implícita). Complexidade O(V+E).'
    )
    pdf.destaque('Propósito no SIGIC:')
    pdf.item('Detectar componentes conectados - identificar se a rede está fragmentada')
    pdf.item('Identificar ciclos - rotas alternativas de distribuição')
    pdf.item('Base para detecção de pontos de articulação e pontes')

    pdf.destaque('Resultado - DFS a partir de ARM:')
    pdf.corpo(
        'Ordem de visita: ARM -> HAB -> CTR -> COM -> LAB -> MED -> AGR -> OXI\n\n'
        'Interpretação: o DFS segue o caminho ARM-HAB-CTR-COM-LAB antes de retroceder, '
        'revelando a estrutura de profundidade da rede. Todos os 8 módulos foram visitados, '
        'confirmando que o grafo é conexo.'
    )

    pdf.subtitulo('5.3 Dijkstra - Caminho de Menor Custo')
    pdf.corpo(
        'O algoritmo de Dijkstra encontra o caminho de menor custo (peso total) entre dois '
        'vértices, usando um heap mínimo (heapq). Complexidade O((V+E) log V).'
    )
    pdf.destaque('Propósito no SIGIC:')
    pdf.item('Otimizar a rota de distribuição de energia entre quaisquer dois módulos')
    pdf.item('Minimizar perdas na transmissão identificando o caminho mais eficiente')
    pdf.item('Planejamento de contingência: rotas alternativas quando uma conexão falha')

    pdf.destaque('Resultado - Dijkstra de ARM a LAB:')
    pdf.corpo(
        'Caminho ótimo: ARM -> CTR -> COM -> LAB (custo total: 22 kWh)\n'
        'Rota: ARM -(5)-> CTR -(4)-> COM -(13)-> LAB\n\n'
        'Interpretação: embora existam múltiplos caminhos (ex: ARM-HAB-MED-LAB = 27 kWh), '
        'o Dijkstra identifica que passar pelo Centro de Controle e Comunicação é 5 kWh '
        'mais eficiente.'
    )

    # ========== 6. MODELAGEM MATEMÁTICA ==========
    pdf.add_page()
    pdf.titulo_secao(6, 'Modelagem Matemática')

    pdf.subtitulo('6.1 Função de Consumo Energético')
    pdf.corpo(
        'O consumo energético da colônia ao longo do dia é modelado por uma função quadrática '
        'ajustada pelo método dos mínimos quadrados sobre os 12 pontos de telemetria:'
    )
    pdf.formula_box('E(t) = -0,393357t^2 + 9,2832t + 151,73')
    pdf.corpo(
        'Onde E(t) é o consumo em kWh e t é a hora do dia (0 a 24). Os coeficientes foram '
        'obtidos resolvendo o sistema normal X^T.X.beta = X^T.y pela regra de Cramer, sem uso '
        'de bibliotecas externas.'
    )

    pdf.subtitulo('6.2 Derivada - Taxa de Variação')
    pdf.corpo(
        'A derivada primeira indica a taxa de variação instantânea do consumo:'
    )
    pdf.formula_box("E'(t) = -0,786714t + 9,2832")
    pdf.corpo(
        "Quando E'(t) > 0, o consumo está crescendo; quando E'(t) < 0, está decrescendo. "
        "Esta informação é essencial para antecipar picos de demanda e ajustar a geração."
    )

    pdf.subtitulo('6.3 Ponto Crítico')
    pdf.corpo(
        "O ponto crítico ocorre quando E'(t) = 0:"
    )
    pdf.formula_box("t* = -b/(2a) = -9,2832 / (2 x -0,393357) = 11,80h")
    pdf.corpo(
        'Em t* = 11,80h (aprox. 11h48), o consumo atinge seu valor máximo de 206,5 kWh. '
        'Como a < 0 (parábola côncava), trata-se de um ponto de máximo. Isso indica que o '
        'pico de demanda ocorre próximo ao meio-dia, coincidindo com o período de maior '
        'atividade dos módulos.'
    )

    pdf.subtitulo('6.4 Integral Numérica - Energia Total')
    pdf.corpo(
        'A energia total consumida em 24h é calculada pela integral numérica (método dos '
        'trapézios com 100 subintervalos):'
    )
    pdf.formula_box('Integral de E(t) dt [0,24] = 4.502,4 kWh')
    pdf.corpo(
        'Este valor representa o consumo acumulado ao longo de um dia completo e é '
        'fundamental para dimensionar a capacidade de geração e armazenamento.'
    )

    pdf.subtitulo('6.5 Qualidade do Ajuste')
    pdf.corpo(
        'O coeficiente de determinação R2 = 0,529 indica que o modelo quadrático explica '
        '52,9% da variabilidade observada nos dados. Embora moderado, este valor é esperado '
        'para dados reais com variação estocástica, e o modelo captura corretamente a tendência '
        'geral de consumo com pico diurno.'
    )

    # ========== 7. REGRESSÃO LINEAR ==========
    pdf.add_page()
    pdf.titulo_secao(7, 'Regressão Linear Múltipla')

    pdf.subtitulo('7.1 Objetivo')
    pdf.corpo(
        'A regressão linear múltipla é utilizada para prever o Estado de Carga (SoC) da bateria '
        'da colônia com base no consumo total e na geração de energia. A previsão do SoC permite '
        'antecipar períodos de escassez e tomar decisões preventivas.'
    )

    pdf.subtitulo('7.2 Formulação')
    pdf.corpo('O modelo possui a forma:')
    pdf.formula_box('SoC = b0 + b1 * consumo + b2 * geracao')
    pdf.corpo(
        'Os coeficientes são estimados pelo método dos mínimos quadrados ordinários (OLS), '
        'resolvendo o sistema beta = (X^T.X)^(-1) . X^T.y por eliminação de Gauss. A '
        'implementação não utiliza bibliotecas como sklearn, demonstrando o raciocínio '
        'matemático por trás da regressão.'
    )

    pdf.subtitulo('7.3 Resultados')
    pdf.corpo('Modelo treinado com 30 cenários históricos:')
    pdf.formula_box('SoC = 113,35 + (-0,4105) * consumo + (0,4589) * geracao')
    pdf.ln(1)
    pdf.tabela(
        ['Métrica', 'Valor', 'Interpretação'],
        [
            ['R2', '0,6516', '65,16% da variância explicada pelo modelo'],
            ['RMSE', '11,1 kWh', 'Erro médio de previsão de 11,1% de SoC'],
            ['b0 (intercepto)', '113,35', 'SoC base sem consumo nem geração'],
            ['b1 (consumo)', '-0,4105', 'Cada kWh de consumo reduz 0,41% do SoC'],
            ['b2 (geração)', '0,4589', 'Cada kWh gerado aumenta 0,46% do SoC'],
        ],
        [35, 30, 90]
    )
    pdf.corpo(
        'Interpretação: o coeficiente b1 negativo confirma que maior consumo reduz o SoC, '
        'enquanto b2 positivo indica que maior geração o eleva. O R2 de 0,65 indica ajuste '
        'razoável, e o RMSE de 11,1 mostra erro médio aceitável para decisões operacionais.'
    )

    pdf.subtitulo('7.4 Exemplo de Previsão')
    pdf.tabela(
        ['Cenário', 'Consumo', 'Geração', 'SoC Previsto'],
        [
            ['Normal', '150 kWh', '60 kWh', '79,3%'],
            ['Moderado', '180 kWh', '30 kWh', '53,2%'],
            ['Crítico', '230 kWh', '5 kWh', '21,2%'],
        ],
        [40, 35, 35, 35]
    )

    # ========== 8. REGRESSÃO LOGÍSTICA ==========
    pdf.add_page()
    pdf.titulo_secao(8, 'Regressão Logística')

    pdf.subtitulo('8.1 Objetivo')
    pdf.corpo(
        'A regressão logística classifica cenários operacionais como NORMAL (0) ou CRÍTICO (1). '
        'Um cenário crítico indica risco iminente de falha energética e dispara protocolos de '
        'emergência, como desligamento de módulos de baixa prioridade.'
    )

    pdf.subtitulo('8.2 Formulação')
    pdf.corpo('O modelo utiliza a função sigmoide para mapear combinações lineares em probabilidades:')
    pdf.formula_box('P(critico) = 1 / (1 + e^(-z))')
    pdf.corpo('Onde z = w0 + w1*SoC + w2*consumo + w3*geracao + w4*modulos + w5*eficiencia')
    pdf.ln(1)
    pdf.corpo(
        'O treinamento é feito por gradient descent, minimizando a função de custo cross-entropy '
        'binária ao longo de 5.000 épocas com taxa de aprendizado 0,5. Todas as features são '
        'normalizadas (min-max) antes do treinamento para garantir convergência estável.'
    )

    pdf.subtitulo('8.3 Features Utilizadas')
    pdf.tabela(
        ['Feature', 'Descrição', 'Justificativa'],
        [
            ['soc_bateria', 'Estado de carga (%)', 'Indicador direto de reserva energética'],
            ['consumo_total', 'Consumo em kWh', 'Demanda atual do sistema'],
            ['geracao_total', 'Geração em kWh', 'Oferta de energia renovável'],
            ['modulos_ativos', 'Quantidade ativa', 'Carga operacional'],
            ['eficiencia_rede', 'Eficiência (0-1)', 'Qualidade da distribuição'],
        ],
        [30, 40, 85]
    )

    pdf.subtitulo('8.4 Resultados')
    pdf.tabela(
        ['Métrica', 'Valor'],
        [
            ['Acurácia', '100,0%'],
            ['Custo final (cross-entropy)', '0,0418'],
            ['Épocas de treinamento', '5.000'],
            ['Taxa de aprendizado', '0,5'],
        ],
        [80, 60]
    )

    pdf.destaque('Matriz de Confusão:')
    pdf.tabela(
        ['', 'Predito Normal', 'Predito Crítico'],
        [
            ['Real Normal', 'VN = 17', 'FP = 0'],
            ['Real Crítico', 'FN = 0', 'VP = 13'],
        ],
        [50, 50, 50]
    )
    pdf.corpo(
        'O modelo atingiu 100% de acurácia nos dados de treinamento, classificando corretamente '
        'todos os 17 cenários normais e 13 cenários críticos. A curva de custo mostra convergência '
        'rápida, caindo de 0,6931 (aleatório) para 0,0418 nas 5.000 épocas.'
    )

    pdf.subtitulo('8.5 Convergência do Treinamento')
    pdf.corpo(
        'Evolução do custo cross-entropy a cada 100 épocas:\n'
        'Época 0: 0,6931 (equivalente a classificação aleatória)\n'
        'Época 100: 0,2565 (queda de 63%)\n'
        'Época 500: 0,1194 (modelo já acertando a maioria)\n'
        'Época 1000: 0,0856\n'
        'Época 2000: 0,0621\n'
        'Época 3000: 0,0504\n'
        'Época 4000: 0,0434\n'
        'Época 4900: 0,0418 (convergido)\n\n'
        'A convergência suave sem oscilações confirma que a taxa de aprendizado de 0,5 é '
        'adequada para este dataset.'
    )

    # ========== 9. ANÁLISE ESG ==========
    pdf.add_page()
    pdf.titulo_secao(9, 'Análise de Sustentabilidade (ESG)')

    pdf.subtitulo('9.1 Métricas Calculadas')
    pdf.corpo(
        'A análise ESG avalia a sustentabilidade da operação em três dimensões: Environmental '
        '(ambiental), Social e Governance (governança).'
    )
    pdf.tabela(
        ['Dimensão', 'Score', 'Peso', 'Métrica Principal'],
        [
            ['Environmental (E)', '18,2', '40%', '18,2% de energia renovável'],
            ['Social (S)', '100,0', '30%', '100% dos registros com 6+ módulos ativos'],
            ['Governance (G)', '89,3', '30%', '89,3% de eficiência média da rede'],
        ],
        [35, 20, 20, 80]
    )
    pdf.formula_box('Score ESG = 0,4 x E + 0,3 x S + 0,3 x G = 64,1 / 100')

    pdf.subtitulo('9.2 Indicadores Detalhados')
    pdf.tabela(
        ['Indicador', 'Valor', 'Análise'],
        [
            ['Geração total (24h)', '409,0 kWh', 'Geração solar + eólica'],
            ['Consumo total (24h)', '2.250,0 kWh', 'Demanda dos 8 módulos'],
            ['Energia renovável', '18,2%', 'Déficit significativo'],
            ['CO2 evitado', '286,3 kg', 'vs. geradores diesel (0,7 kg/kWh)'],
            ['Perdas estimadas', '240,0 kWh', '10,7% do consumo total'],
            ['Consumo essencial', '62,7%', 'Prioridade 1-3 (5 módulos)'],
        ],
        [40, 30, 85]
    )

    pdf.subtitulo('9.3 Recomendações')
    pdf.item('[ALTO] Energia Renovável: aumentar capacidade solar/eólica (atual 18% renovável) '
             '- a colônia depende fortemente de armazenamento, o que é insustentável a longo prazo')
    pdf.item('[MÉDIO] Eficiência da Rede: otimizar rotas de distribuição (eficiência atual 89,3%) '
             '- o Dijkstra pode auxiliar na seleção de caminhos ótimos')
    pdf.item('[MÉDIO] Redução de Perdas: reduzir as 240 kWh estimadas de perda na transmissão '
             '- modernizar conexões de alto custo como OXI-AGR (15 kWh)')
    pdf.item('[ALTO] Expansão Planejada: priorizar conexões curtas ao expandir a rede, '
             'minimizando perdas em novas arestas do grafo')
    pdf.item('[ALTO] Governança: manter sistemas essenciais (prioridade 1-3) com redundância '
             'energética e rotas alternativas confirmadas pelo BFS')

    # ========== 10. DASHBOARD WEB ==========
    pdf.add_page()
    pdf.titulo_secao(10, 'Dashboard Web Interativo')

    pdf.corpo(
        'O sistema é acessado via navegador web em http://localhost:5050, protegido por '
        'autenticação (usuário: usuario / senha: senha). O dashboard é uma SPA (Single Page '
        'Application) com 7 seções interativas.'
    )

    pdf.subtitulo('10.1 Seções do Dashboard')
    pdf.item('Visão Geral: status de todos os módulos, métricas de energia e score ESG')
    pdf.item('Rede: visualização interativa do grafo em canvas, lista e matriz de adjacência')
    pdf.item('Algoritmos: execução interativa de BFS, DFS e Dijkstra com seleção de vértices')
    pdf.item("Energia: gráficos de geração vs consumo, SoC ao longo do dia, eficiência")
    pdf.item("Modelagem: curva quadrática E(t), derivada E'(t), ponto crítico")
    pdf.item('Previsão: resultados da regressão linear/logística e simulador de cenários')
    pdf.item('ESG: barras de score E/S/G, distribuição de consumo, recomendações')

    pdf.subtitulo('10.2 Tecnologias')
    pdf.tabela(
        ['Componente', 'Tecnologia', 'Função'],
        [
            ['Backend', 'Flask (Python)', 'Rotas, API REST, autenticação'],
            ['Frontend', 'HTML/CSS/JS', 'Dashboard SPA responsivo'],
            ['Gráficos', 'Chart.js (CDN)', 'Visualização de dados interativa'],
            ['PDFs', 'fpdf2', 'Geração de rede_colonia.pdf e documentação'],
            ['Dados', 'CSV', 'Armazenamento de telemetria e cenários'],
        ],
        [30, 40, 85]
    )

    # ========== 11. CONCLUSÃO ==========
    pdf.add_page()
    pdf.titulo_secao(11, 'Conclusão')

    pdf.corpo(
        'O SIGIC demonstra a integração de múltiplas disciplinas computacionais em um sistema '
        'coerente e funcional:'
    )
    pdf.ln(2)
    pdf.item('Grafos: a modelagem da rede como grafo ponderado permitiu aplicar BFS, DFS e '
             'Dijkstra para otimizar rotas e detectar vulnerabilidades estruturais')
    pdf.item('Cálculo diferencial: a função quadrática com derivada e ponto crítico identificou '
             'o pico de consumo em t* = 11,8h, informação crucial para planejamento energético')
    pdf.item('Regressão linear: o modelo de previsão de SoC (R2 = 0,65) quantificou o impacto '
             'do consumo e da geração no estado de carga da bateria')
    pdf.item('Regressão logística: o classificador de cenários críticos (100% acurácia) demonstrou '
             'a capacidade de identificar situações de risco com alta confiança')
    pdf.item('Análise ESG: o score de 64,1/100 revelou que a principal fragilidade da colônia é '
             'a baixa geração renovável (18,2%), indicando necessidade de expansão solar/eólica')
    pdf.ln(2)
    pdf.corpo(
        'O dashboard web interativo consolida todos estes resultados em uma interface acessível, '
        'permitindo que operadores da colônia visualizem, simulem cenários e tomem decisões '
        'informadas sobre o gerenciamento energético da base marciana.'
    )

    # ========== SALVAR ==========
    caminho = os.path.join(BASE_DIR, 'Relatorio_Tecnico_SIGIC.pdf')
    pdf.output(caminho)
    print(f'Relatório gerado: {caminho}')
    print(f'Total de páginas: {pdf.page_no()}')


if __name__ == '__main__':
    main()
