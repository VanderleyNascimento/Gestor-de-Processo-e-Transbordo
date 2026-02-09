# 🚚 Loggi - Gestor de Processo e Transbordo

Este é um aplicativo analítico desenvolvido em **Streamlit** para otimizar a gestão logística de pacotes, segregando fluxos de **Transbordo** e **Processo**, monitorando SLAs e rastreando veículos.

A ferramenta centraliza dados de múltiplas fontes CSV, oferecendo visões estratégicas e táticas para tomada de decisão em tempo real.

---

## 🚀 Funcionalidades Principais

### 1. Dashboard Geral
Visão consolidada do volume operacional.
-   **KPIs em Tempo Real**: Volume Total, Transbordo vs. Processo, Veículos Envolvidos.
-   **Filtros Dinâmicos**: Filtre por Agência, Categoria (Transbordo/Processo), Veículo (Placa/ID) e Arquivo de Origem.
-   **Rastreamento de Veículos**: Identificação automática de caminhões e suas cargas.
-   **Exportação de Dados**: Geração de relatórios CSV detalhados por agência, incluindo cálculo automático de participação (% Share) no volume total.

### 2. Gestão de Lacres (Antigo "Malotes")
Foco na unidade de transporte (Seal/Lacre).
-   **Busca Inteligente**: Localize lacres específicos ou filtre por destino e veículo.
-   **Drill-Down**: Clique em um lacre para ver todos os pacotes contidos nele.
-   **Visualização de Frota**: Filtre lacres associados a veículos específicos (ex: Placas reais extraídas do banco de dados).

### 3. Gestão de SLA e Expedição
Monitoramento de prazos e criticidade.
-   **Cálculo de SLO**: Determinação automática da Data Limite de Expedição baseada na promessa de entrega, tempo de trânsito e processamento.
-   **Alertas de Risco**: Identificação visual de lacres Críticos, em Atenção ou Para Expedir Hoje.
-   **Configuração Personalizável**: Ajuste os tempos de trânsito e processamento por agência diretamente na interface.

---

## 🛠️ Tecnologias Utilizadas

-   **Python 3.12+**
-   **Streamlit**: Framework para Web Apps de Dados.
-   **Pandas**: Manipulação e análise de dados de alta performance.
-   **Plotly Express**: Visualizações interativas.
-   **Git/GitHub**: Controle de versão.

---

## 📦 Como Executar

Certifique-se de ter o Python instalado e o ambiente virtual configurado.

### Configuração Inicial (Primeira vez)

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Executando a Aplicação

Para facilitar, utilize o script incluído:

```bash
./run.sh
```

Ou execute manualmente:

```bash
.venv/bin/streamlit run app.py
```

---

## 🤝 Créditos e Desenvolvimento

**Desenvolvido por:** Vanderley Nascimento

Este projeto é uma solução proprietária para análise logística, focada em eficiência operacional e visibilidade de dados.

---
*Atualizado em: Fevereiro de 2026*

---

## 🔒 Licença e Segurança

> **AVISO LEGAL:** Este software é protegido por leis de direitos autorais e propriedade intelectual.

O uso deste código fonte ou da aplicação compilada está sujeito aos seguintes termos:

1.  **Uso Pessoal/Acadêmico**: Permitido apenas para fins de estudo e demonstração pessoal, desde que mantidos os créditos originais ao autor **Vanderley Nascimento**.
2.  **Uso Comercial**: É estritamente **PROIBIDO** o uso comercial sem prévio aviso, venda, distribuição ou modificação deste software sem a prévia autorização por escrito do autor ou aquisição de uma licença comercial.
3.  **Remoção de Créditos**: A remoção ou alteração dos créditos do autor configura violação dos termos de uso.

**Para adquirir uma licença comercial ou solicitar permissão de uso:**
Entre em contato diretamente com o desenvolvedor.

&copy; 2026 Vanderley Nascimento. Todos os direitos reservados.
