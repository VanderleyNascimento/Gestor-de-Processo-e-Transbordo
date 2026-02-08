import pandas as pd
import streamlit as st

@st.cache_data
def load_and_combine_data(uploaded_files):
    """
    Carrega e combina múltiplos arquivos CSV em um único DataFrame via concatenação.
    """
    if not uploaded_files:
        return pd.DataFrame()

    all_dfs = []
    for file in uploaded_files:
        try:
            # Tenta ler com diferentes encodings se utf-8 falhar (comum em arquivos brasileiros)
            try:
                df = pd.read_csv(file, encoding='utf-8', sep=',')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='latin1', sep=',')
            except pd.errors.ParserError:
                # Tenta separador de ponto e vírgula se vírgula falhar
                file.seek(0)
                df = pd.read_csv(file, encoding='utf-8', sep=';')
                
            all_dfs.append(df)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo {file.name}: {e}")
            continue

    if not all_dfs:
        return pd.DataFrame()

    try:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        return combined_df
    except Exception as e:
        st.error(f"Erro ao combinar arquivos: {e}")
        return pd.DataFrame()

def classify_agency(agency_name, trasbordo_list):
    """
    Classifica uma agência como 'Transbordo' ou 'Processos XDDF' baseada na lista fornecida.
    """
    if agency_name in trasbordo_list:
        return "Transbordo"
    return "Processo"

@st.cache_data
def process_data(df, trasbordo_list):
    """
    Aplica a classificação de agências ao DataFrame e garante tipos corretos.
    """
    if df.empty:
        return df
    
    df_processed = df.copy()
    
    # Normalização da coluna de agência
    col_agencia = 'agência_destino_anotacao'
    if col_agencia in df_processed.columns:
        df_processed[col_agencia] = df_processed[col_agencia].fillna('N/A').astype(str)
        
        df_processed['Categoria'] = df_processed[col_agencia].apply(
            lambda x: classify_agency(x, trasbordo_list)
        )
    
    # Tratamento de datas (se existirem)
    if 'promised_date' in df_processed.columns:
        df_processed['promised_date'] = pd.to_datetime(df_processed['promised_date'], errors='coerce', dayfirst=True)
        
        # Lógica de Prazos (SLA)
        hoje = pd.Timestamp.now().normalize()
        
        def definir_status_prazo(row):
            if pd.isnull(row['promised_date']):
                return "Sem Data"
            
            delta = (row['promised_date'] - hoje).days
            
            if delta < 0:
                return "Atrasado"
            elif delta == 0:
                return "Vence Hoje"
            else:
                return "No Prazo"

        df_processed['Status_Prazo'] = df_processed.apply(definir_status_prazo, axis=1)

    return df_processed

@st.cache_data
def parse_vehicle_info(context_str):
    """
    Extrai informações de veículo/origem do contexto atual.
    Retorna uma tupla (Tipo, Identificador).
    """
    if pd.isna(context_str):
        return "Indefinido", "-"
    
    context_str = str(context_str).strip()
    
    # Caso AGP (XDDF COL)
    if "XDDF COL" in context_str:
        return "Agência AGP", context_str
        
    # Caso TRUCK
    if context_str.startswith("TRUCK"):
        parts = context_str.split()
        # Esperado: ["TRUCK", "PLACA", "TRANSFERENCIA"]
        if len(parts) >= 2:
            return "Caminhão", parts[1] # Retorna a Placa
            
    return "Outro", context_str

@st.cache_data
def group_data_by_seal(df):
    """
    Agrupa os dados por Seal (Malote), consolidando informações.
    """
    if 'seal' not in df.columns:
        return pd.DataFrame()

    # Agrupamento
    # Assume que todos os pacotes do mesmo seal têm a mesma agência e contexto (ou pega o primeiro/mais comum)
    df_grouped = df.groupby('seal').agg({
        'package_id': 'count',
        'agência_destino_anotacao': lambda x: x.mode()[0] if not x.mode().empty else "Indefinido",
        'contexto_atual': lambda x: x.mode()[0] if not x.mode().empty else pd.NA,
        'promised_date': 'min' # Data mais crítica (menor)
    }).reset_index()
    
    df_grouped.rename(columns={'package_id': 'Qtd_Pacotes', 'promised_date': 'Data_Promessa_Min'}, inplace=True)
    
    # Enriquecer com info do veículo
    extra_info = df_grouped['contexto_atual'].apply(parse_vehicle_info)
    df_grouped['Tipo_Veiculo'] = [x[0] for x in extra_info]
    df_grouped['Identificador'] = [x[1] for x in extra_info]
    
    return df_grouped

def get_unique_agencies(df):
    """
    Retorna uma lista ordenada e única de agências, garantindo que sejam strings.
    """
    if df.empty or 'agência_destino_anotacao' not in df.columns:
        return []
    
    # Converte para string e trata nulos ANTES de ordenar
    return sorted(df['agência_destino_anotacao'].fillna('N/A').astype(str).unique())

@st.cache_data
def calculate_slo(df, config_dict):
    """
    Calcula a Data Limite de Expedição (SLO) baseada na configuração de cada agência.
    Fórmula: Data Promessa - 1 (Buffer) - Tempo Agência - Tempo Trânsito
    """
    if df.empty or 'promised_date' not in df.columns:
        return df

    df_calc = df.copy()
    
    # Normalizar datas
    df_calc['promised_date'] = pd.to_datetime(df_calc['promised_date'], errors='coerce')
    
    def get_slo(row):
        agency = str(row.get('agência_destino_anotacao', ''))
        
        # Pega config ou padrão (0 dias)
        cfg = config_dict.get(agency, {"transit_time": 0, "agency_time": 0})
        
        transit = cfg.get("transit_time", 0)
        agency_time = cfg.get("agency_time", 0)
        buffer = 1 # 1 dia de folga padrão pedido pelo usuário
        
        total_offset = transit + agency_time + buffer
        
        if pd.isnull(row['promised_date']):
            return pd.NaT
            
        return row['promised_date'] - pd.Timedelta(days=total_offset)

    df_calc['Data_Limite_Expedicao'] = df_calc.apply(get_slo, axis=1)
    
    # Status de Expedição
    hoje = pd.Timestamp.now().normalize()
    
    def status_expedicao(row):
        if pd.isnull(row['Data_Limite_Expedicao']):
            return "Sem Data"
        
        delta = (row['Data_Limite_Expedicao'] - hoje).days
        
        if delta < 0:
            return "Atrasado (Crítico)"
        elif delta == 0:
            return "Expedir Hoje"
        elif delta <= 1:
            return "Atenção"
        else:
            return "No Prazo"
            
    df_calc['Status_Expedicao'] = df_calc.apply(status_expedicao, axis=1)
    
    return df_calc
