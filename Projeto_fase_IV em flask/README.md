# SIGIC - Sistema Inteligente de Gerenciamento da Infraestrutura da Colonia

Fase IV - Energia para Sobreviver | FIAP 2026 | Ciencias da Computacao

**Marcelo Bastianello Baldin - RM568746 - Grupo 13**

## Sobre

Sistema web para gerenciamento da infraestrutura energetica de uma colonia em Marte (Aurora Siger). Integra grafos, calculo diferencial, regressao linear/logistica e analise ESG em um dashboard interativo.

## Execucao Rapida

```bash
python instalar_sigic.py
```

Acesse http://localhost:5050 (usuario: `usuario` / senha: `senha`)

## Funcionalidades

- **Grafos**: rede de 8 modulos e 14 conexoes com BFS, DFS e Dijkstra
- **Modelagem**: funcao quadratica E(t), derivada, ponto critico, integral numerica
- **Regressao Linear**: previsao de SoC da bateria (eliminacao de Gauss)
- **Regressao Logistica**: classificacao de cenarios criticos (gradient descent)
- **Analise ESG**: score ambiental/social/governanca com recomendacoes
- **Dashboard Web**: 7 secoes interativas com graficos (Chart.js)

## Estrutura

```
codigo_fonte.py              # Sistema principal
instalar_sigic.py            # Instalador automatico
rede_colonia.pdf             # Diagrama da rede
documentacao_complementar.pdf # Documentacao tecnica
arquivos_auxiliares/
  dados_energia.csv          # Telemetria (12 registros, 24h)
  historico_cenarios.csv     # Dados ML (30 cenarios)
  templates/
    login.html               # Pagina de login
    dashboard.html            # Dashboard SPA
```

## Tecnologias

Python 3 | Flask | fpdf2 | Chart.js | Grafos | Calculo Diferencial | Regressao Linear/Logistica | ESG
