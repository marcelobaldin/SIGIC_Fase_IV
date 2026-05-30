# SIGIC - Guia de Instalacao

## Sistema Inteligente de Gerenciamento da Infraestrutura da Colonia
Fase IV - Energia para Sobreviver | FIAP 2026
Marcelo Bastianello Baldin - RM568746 - Grupo 13

---

## Requisitos

- Python 3.10 ou superior
- Sistema operacional: Windows, macOS ou Linux
- Navegador web moderno (Chrome, Firefox, Edge)

## Instalacao Automatica (recomendado)

1. Abra o terminal na pasta do projeto
2. Execute:

```bash
python instalar_sigic.py
```

O instalador cria automaticamente o ambiente virtual, instala as dependencias (Flask e fpdf2) e inicia o sistema.

## Instalacao Manual

1. Crie um ambiente virtual:

```bash
python -m venv venv
```

2. Ative o ambiente:

- **Windows**: `venv\Scripts\activate`
- **macOS/Linux**: `source venv/bin/activate`

3. Instale as dependencias:

```bash
pip install flask fpdf2
```

4. Execute o sistema:

```bash
python codigo_fonte.py
```

## Acesso

- URL: http://localhost:5050
- Usuario: `usuario`
- Senha: `senha`

## Funcionalidades

### Dashboard Web (7 secoes)

1. **Visao Geral** - Status dos 8 modulos da colonia, metricas de energia e ESG
2. **Rede** - Visualizacao do grafo da rede, lista e matriz de adjacencia, metricas
3. **Algoritmos** - BFS, DFS e Dijkstra interativos com selecao de modulos
4. **Energia** - Graficos de geracao solar/eolica vs consumo, SoC, eficiencia
5. **Modelagem** - Funcao quadratica E(t), derivada, ponto critico, integral
6. **Previsao** - Regressao linear (SoC) e logistica (critico/normal), simulador
7. **ESG** - Score ambiental/social/governanca, recomendacoes

### PDFs Gerados

- `rede_colonia.pdf` - Diagrama visual da rede com modulos e custos
- `documentacao_complementar.pdf` - Documentacao tecnica completa

Para gerar os PDFs pela interface web, clique no botao "Gerar PDFs" na secao Visao Geral, ou acesse `/api/gerar-pdfs` no navegador.

## Estrutura dos Arquivos

```
Projeto_Fase_IV/
  codigo_fonte.py                    # Codigo principal (grafos, ML, Flask)
  instalar_sigic.py                  # Instalador automatico
  instalacao_sigic.md                # Este guia
  rede_colonia.pdf                   # Diagrama da rede (gerado)
  documentacao_complementar.pdf      # Documentacao tecnica (gerado)
  link_video.txt                     # Link do video de apresentacao
  arquivos_auxiliares/
    dados_energia.csv                # Telemetria energetica (12 registros)
    historico_cenarios.csv           # Dados para ML (30 cenarios)
    templates/
      login.html                    # Pagina de login
      dashboard.html                # Dashboard SPA principal
```

## Tecnologias Utilizadas

- **Python 3** - Linguagem principal
- **Flask** - Framework web
- **fpdf2** - Geracao de PDF
- **Chart.js** (CDN) - Graficos no dashboard
- **Grafos** - Lista e matriz de adjacencia, BFS, DFS, Dijkstra
- **Calculo** - Funcao quadratica, derivada, integral numerica (trapezio)
- **Regressao Linear** - Eliminacao de Gauss (sem sklearn)
- **Regressao Logistica** - Gradient descent, sigmoid, cross-entropy
- **Analise ESG** - Score composto ambiental/social/governanca

## Encerramento

Para encerrar o sistema, pressione `Ctrl+C` no terminal.
