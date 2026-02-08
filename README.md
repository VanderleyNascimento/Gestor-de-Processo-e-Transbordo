# Streamlit App - Análise de Pacotes

Este é um aplicativo Streamlit para análise de pacotes e classificação de agências (Processo vs Trasbordo).

## Pré-requisitos

Certifique-se de ter o Python instalado. O projeto utiliza um ambiente virtual (`.venv`) para gerenciar as dependências.

## Como Executar

O comando `streamlit` pode não estar no seu PATH global se você não ativou o ambiente virtual. 

Para facilitar, você pode usar o script de execução incluído:

### Opção 1: Usando o script `run.sh` (Recomendado no Linux/Mac)

```bash
./run.sh
```

### Opção 2: Ativando o ambiente virtual manualmente

```bash
source .venv/bin/activate
streamlit run app.py
```

### Opção 3: Executando diretamente do ambiente virtual

```bash
.venv/bin/streamlit run app.py
```

## Estrutura do Projeto

-   `app.py`: Arquivo principal da aplicação.
-   `utils.py`: Funções utilitárias para carregamento e processamento de dados.
-   `run.sh`: Script auxiliar para execução.
