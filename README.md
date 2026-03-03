
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)



![Setor](https://img.shields.io/badge/Setor-Log%C3%ADstica-orange?style=for-the-badge)
# 🚚 XDDF - Gestor de Processo e Transbordo

Aplicação analítica em **Streamlit** para gestão logística de pacotes, separando fluxos de **Transbordo** e **Processo**, com foco em visibilidade operacional, SLA e tomada de decisão em tempo real.

---
![Foco](https://img.shields.io/badge/Foco-Efici%C3%AAncia%20Operacional-blueviolet?style=for-the-badge)
## 🚀 Funcionalidades Principais

### 1. Dashboard Geral
- KPIs de volume total, transbordo, processo e veículos.
- Filtros por agência, categoria, veículo e arquivo de origem.
- Exportação de relatório consolidado por agência.

### 2. Gestão de Lacres
- Agrupamento por `seal` (lacre).
- Busca por lacre, pacote e barcode.
- Drill-down para visualizar pacotes por lacre.

### 3. Gestão de SLA e Expedição
- Cálculo automático da data limite de expedição (SLO).
- Classificação de prioridade (`Crítico`, `Expedir Hoje`, `Atenção`, `No Prazo`).
- Diagnóstico e ação recomendada por lacre.

### 4. Qualidade e Governança de Dados
- Validação de schema (colunas obrigatórias e recomendadas).
- Deduplicação automática de pacotes por `package_id` e `barcode`.
- Persistência de configuração de transbordo e tempos por agência.

---
![Status](https://img.shields.io/badge/Status-Ativo-success?style=for-the-badge)
## 🛠️ Execução Rápida

### Windows PowerShell
```powershell
.\run.ps1
```

### Windows CMD
```cmd
run.bat
```

### Linux / WSL / Git Bash
```bash
./run.sh
```

Os scripts criam o `.venv`, instalam dependências na primeira execução e iniciam o Streamlit.

---

## 📦 Execução Manual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/WSL/Git Bash
# ou: .\.venv\Scripts\Activate.ps1  # PowerShell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

---
![Testes](https://img.shields.io/badge/Testes-Passando-brightgreen?style=for-the-badge&logo=pytest)
## ✅ Testes
```bash
python -m pytest -q
```

---
![Manutenção](https://img.shields.io/badge/Manuten%C3%A7%C3%A3o-Sim-blue?style=for-the-badge)
## 📁 Estrutura Principal
- `app.py`: interface e fluxos das telas.
- `utils.py`: ingestão, validação, deduplicação e regras de negócio.
- `config_manager.py`: persistência de configurações.
- `agency_config.json`: tempos de SLA e agências de transbordo.

---
![Licença: Restrita](https://img.shields.io/badge/Licen%C3%A7a-Restrita-red?style=for-the-badge)
## 🔐 Licença, Consentimento e Uso

> **AVISO LEGAL:** este software é protegido por direitos autorais e propriedade intelectual.

O uso deste código fonte está sujeito aos termos abaixo:

1. **Uso pessoal/estudo**: permitido para aprendizado e demonstração, mantendo os créditos originais.
2. **Uso comercial**: **proibido** sem autorização prévia e por escrito do proprietário do projeto.
3. **Distribuição/modificação com fins comerciais**: exige consentimento formal do proprietário.
4. **Remoção de créditos/autoria**: configura violação dos termos de uso.

Em resumo: este projeto **não pode ser usado comercialmente sem consentimento explícito do dono**.

---

## 🤝 Créditos

![Autor: Vanderley Nascimento](https://img.shields.io/badge/Autor-Vanderley%20Nascimento-blue?style=for-the-badge&logo=github)
![Projeto: The Sheep Lab](https://img.shields.io/badge/Projeto-The%20Sheep%20Lab-white?style=for-the-badge&logo=icloud&logoColor=black)

**Projeto proprietário** para análise logística e eficiência operacional.

© 2026 Vanderley Nascimento. Todos os direitos reservados.
