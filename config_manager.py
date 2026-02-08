import json
import os
import pandas as pd

CONFIG_FILE = "agency_config.json"

def load_config():
    """
    Carrega as configurações do arquivo JSON. Se não existir, retorna um dicionário vazio.
    """
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar config: {e}")
        return {}

def save_config(config_data):
    """
    Salva o dicionário de configurações no arquivo JSON.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar config: {e}")
        return False

def get_agency_config_df(current_agencies):
    """
    Gera um DataFrame para edição no Streamlit, mesclando agências atuais com o salvo.
    """
    saved_config = load_config()
    
    data = []
    for agency in current_agencies:
        # Valores padrão: Trânsito=0, Processo=0
        cfg = saved_config.get(agency, {"transit_time": 0, "agency_time": 0})
        data.append({
            "Agência": agency,
            "Tempo Trânsito (Dias)": cfg.get("transit_time", 0),
            "Tempo Agência (Dias)": cfg.get("agency_time", 0)
        })
        
    return pd.DataFrame(data).sort_values("Agência")

def update_config_from_df(edited_df):
    """
    Atualiza o JSON baseado no DataFrame editado pelo usuário.
    """
    new_config = load_config()
    
    for index, row in edited_df.iterrows():
        agency = row["Agência"]
        new_config[agency] = {
            "transit_time": int(row["Tempo Trânsito (Dias)"]),
            "agency_time": int(row["Tempo Agência (Dias)"])
        }
        
    save_config(new_config)
    return new_config
