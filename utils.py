import json
import logging
import pandas as pd
import streamlit as st

logger = logging.getLogger("xddf.utils")

REQUIRED_COLUMNS = ("agência_destino_anotacao",)
RECOMMENDED_COLUMNS = (
    "seal",
    "package_id",
    "barcode",
    "promised_date",
    "contexto_atual",
)


def _safe_mode(series, default_value):
    """
    Retorna a moda de forma segura, com fallback para valor padrao.
    """
    mode_values = series.dropna().mode()
    if not mode_values.empty:
        return mode_values.iloc[0]
    return default_value


def _log_event(event, **fields):
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))


def validate_dataframe_schema(df):
    """
    Valida colunas obrigatorias e recomendadas para a aplicacao.
    """
    cols = set(df.columns)
    missing_required = [c for c in REQUIRED_COLUMNS if c not in cols]
    missing_recommended = [c for c in RECOMMENDED_COLUMNS if c not in cols]
    return {
        "is_valid": len(missing_required) == 0,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
    }


def deduplicate_packages(df):
    """
    Remove duplicidades entre arquivos usando package_id e/ou barcode.
    Prioriza package_id quando disponivel e usa barcode como fallback.
    """
    dedup_fields = []
    if "package_id" in df.columns:
        dedup_fields.append(("package_id", "pid:"))
    if "barcode" in df.columns:
        dedup_fields.append(("barcode", "bar:"))

    if not dedup_fields:
        return df, {"removed": 0, "strategy": "no_dedup_field"}

    df_work = df.copy()
    dedup_key = pd.Series(pd.NA, index=df_work.index, dtype="object")

    for field, prefix in dedup_fields:
        normalized = df_work[field].where(df_work[field].notna(), "").astype(str).str.strip()
        valid = normalized != ""
        candidate = prefix + normalized
        dedup_key = dedup_key.mask(dedup_key.isna() & valid, candidate)

    df_work["_dedup_key"] = dedup_key
    has_key = df_work["_dedup_key"].notna()

    df_no_key = df_work[~has_key]
    df_with_key = df_work[has_key].drop_duplicates(subset="_dedup_key", keep="first")

    combined = pd.concat([df_no_key, df_with_key], axis=0).sort_index()
    removed = len(df_work) - len(combined)

    combined = combined.drop(columns=["_dedup_key"]).reset_index(drop=True)
    strategy = "+".join([field for field, _ in dedup_fields])
    return combined, {"removed": int(removed), "strategy": strategy}


@st.cache_data
def load_and_combine_data(uploaded_files, deduplicate=True):
    """
    Carrega e combina multiplos CSVs.
    """
    if not uploaded_files:
        return pd.DataFrame()

    all_dfs = []
    read_strategies = [
        ("utf-8", ","),
        ("latin1", ","),
        ("utf-8", ";"),
        ("latin1", ";"),
    ]

    for file in uploaded_files:
        loaded_df = None
        last_error = None
        for encoding, sep in read_strategies:
            try:
                file.seek(0)
                loaded_df = pd.read_csv(file, encoding=encoding, sep=sep)
                _log_event("file_read_ok", file=file.name, encoding=encoding, sep=sep, rows=len(loaded_df))
                break
            except Exception as e:
                last_error = e

        if loaded_df is None:
            _log_event("file_read_error", file=file.name, error_type=type(last_error).__name__, error=str(last_error))
            st.error(f"Erro ao ler o arquivo {file.name}: {last_error}")
            continue

        loaded_df["source_file"] = file.name
        all_dfs.append(loaded_df)

    if not all_dfs:
        return pd.DataFrame()

    try:
        combined_df = pd.concat(all_dfs, ignore_index=True)
    except Exception as e:
        _log_event("combine_error", error_type=type(e).__name__, error=str(e))
        st.error(f"Erro ao combinar arquivos: {e}")
        return pd.DataFrame()

    if deduplicate:
        before = len(combined_df)
        combined_df, dedup_info = deduplicate_packages(combined_df)
        _log_event(
            "dedup_summary",
            before=before,
            after=len(combined_df),
            removed=dedup_info["removed"],
            strategy=dedup_info["strategy"],
        )

    return combined_df


def classify_agency(agency_name, trasbordo_list):
    """
    Classifica uma agencia como Transbordo ou Processo.
    """
    if agency_name in trasbordo_list:
        return "Transbordo"
    return "Processo"


@st.cache_data
def process_data(df, trasbordo_list):
    """
    Aplica classificacao de agencias, trata tipos e extrai dados de veiculo.
    """
    if df.empty:
        return df

    df_processed = df.copy()
    col_agencia = "agência_destino_anotacao"

    if col_agencia in df_processed.columns:
        agency_col = df_processed[col_agencia].fillna("N/A").astype(str)
        df_processed[col_agencia] = agency_col
        trasbordo_set = set(trasbordo_list)
        df_processed["Categoria"] = agency_col.map(
            lambda value: "Transbordo" if value in trasbordo_set else "Processo"
        )

    if "contexto_atual" in df_processed.columns:
        vehicle_data = df_processed["contexto_atual"].apply(parse_vehicle_info)
        df_processed["Tipo_Veiculo"] = [x[0] for x in vehicle_data]
        df_processed["Identificador"] = [x[1] for x in vehicle_data]
    else:
        df_processed["Tipo_Veiculo"] = "Indefinido"
        df_processed["Identificador"] = "-"

    if "promised_date" in df_processed.columns:
        promised = pd.to_datetime(df_processed["promised_date"], errors="coerce", dayfirst=True)
        df_processed["promised_date"] = promised

        hoje = pd.Timestamp.now().normalize()
        delta = (promised.dt.normalize() - hoje).dt.days

        status = pd.Series("No Prazo", index=df_processed.index, dtype="object")
        status = status.mask(promised.isna(), "Sem Data")
        status = status.mask(delta < 0, "Atrasado")
        status = status.mask(delta == 0, "Vence Hoje")
        status = status.mask(delta == 1, "Atenção")

        df_processed["Status_Prazo"] = status

    return df_processed


@st.cache_data
def parse_vehicle_info(context_str):
    """
    Extrai informacoes de veiculo/origem do contexto atual.
    Retorna uma tupla (Tipo, Identificador).
    """
    if pd.isna(context_str):
        return "Indefinido", "-"

    context_str = str(context_str).strip()

    if "XDDF COL" in context_str:
        return "Agência AGP", context_str

    if context_str.startswith("TRUCK"):
        parts = context_str.split()
        if len(parts) >= 2:
            return "Caminhão", parts[1]

    return "Outro", context_str


@st.cache_data
def group_data_by_seal(df):
    """
    Agrupa por seal de forma robusta mesmo com colunas opcionais ausentes.
    """
    if "seal" not in df.columns or df.empty:
        return pd.DataFrame()

    df_grouped = df.groupby("seal").size().reset_index(name="Qtd_Pacotes")

    mode_defaults = {
        "agência_destino_anotacao": "Indefinido",
        "contexto_atual": pd.NA,
        "Tipo_Veiculo": "Indefinido",
        "Identificador": "-",
    }

    for col_name, default_value in mode_defaults.items():
        if col_name in df.columns:
            df_mode = (
                df.groupby("seal")[col_name]
                .agg(lambda x: _safe_mode(x, default_value))
                .reset_index(name=col_name)
            )
            df_grouped = df_grouped.merge(df_mode, on="seal", how="left")

    if "promised_date" in df.columns:
        date_series = pd.to_datetime(df["promised_date"], errors="coerce", dayfirst=True)
        df_dates = date_series.groupby(df["seal"]).min().reset_index(name="Data_Promessa_Min")
        df_grouped = df_grouped.merge(df_dates, on="seal", how="left")
    else:
        df_grouped["Data_Promessa_Min"] = pd.NaT

    if "Tipo_Veiculo" not in df_grouped.columns:
        if "contexto_atual" in df_grouped.columns:
            extra_info = df_grouped["contexto_atual"].apply(parse_vehicle_info)
        else:
            extra_info = pd.Series([("Indefinido", "-")] * len(df_grouped))

        df_grouped["Tipo_Veiculo"] = [x[0] for x in extra_info]
        df_grouped["Identificador"] = [x[1] for x in extra_info]

    return df_grouped


def get_unique_agencies(df):
    """
    Retorna lista ordenada de agencias unicas.
    """
    if df.empty or "agência_destino_anotacao" not in df.columns:
        return []
    return sorted(df["agência_destino_anotacao"].fillna("N/A").astype(str).unique())


@st.cache_data
def calculate_slo(df, config_dict):
    """
    Calcula data limite de expedicao (SLO):
    Data Promessa - 1 (Buffer) - Tempo Agencia - Tempo Transito.
    """
    if df.empty or "promised_date" not in df.columns:
        return df

    df_calc = df.copy()
    promised = pd.to_datetime(df_calc["promised_date"], errors="coerce", dayfirst=True)
    df_calc["promised_date"] = promised

    if "agência_destino_anotacao" in df_calc.columns:
        agencies = df_calc["agência_destino_anotacao"].fillna("").astype(str)
    else:
        agencies = pd.Series("", index=df_calc.index, dtype="object")

    transit_map = {}
    agency_map = {}
    for agency_name, cfg in config_dict.items():
        if isinstance(cfg, dict):
            transit_map[str(agency_name)] = int(cfg.get("transit_time", 0))
            agency_map[str(agency_name)] = int(cfg.get("agency_time", 0))

    transit_days = agencies.map(transit_map).fillna(0).astype(int)
    agency_days = agencies.map(agency_map).fillna(0).astype(int)
    total_offset = transit_days + agency_days + 1

    df_calc["Data_Limite_Expedicao"] = promised - pd.to_timedelta(total_offset, unit="D")

    hoje = pd.Timestamp.now().normalize()
    delta = (df_calc["Data_Limite_Expedicao"].dt.normalize() - hoje).dt.days

    status = pd.Series("No Prazo", index=df_calc.index, dtype="object")
    status = status.mask(df_calc["Data_Limite_Expedicao"].isna(), "Sem Data")
    status = status.mask(delta < 0, "Atrasado (Crítico)")
    status = status.mask(delta == 0, "Expedir Hoje")
    status = status.mask((delta > 0) & (delta <= 1), "Atenção")

    df_calc["Status_Expedicao"] = status
    return df_calc
