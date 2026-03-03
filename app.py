import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import utils
import config_manager
from streamlit_option_menu import option_menu
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("xddf.app")

# Configuração da página
st.set_page_config(
    page_title="XDDF Transbordo e Processos",
    page_icon=":material/local_shipping:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para alinhar com a marca (Azul Loggi) e Dark/Light mode
def inject_custom_css():
    st.markdown("""
    <style>
        /* Global Styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Sidebar Styling - FIXED XDDF NAVY */
        section[data-testid="stSidebar"] {
            background-color: #0d1b2a !important; /* Azul Scuro Profissional */
            border-right: 1px solid rgba(0, 132, 255, 0.2);
        }

        /* Sidebar Toggle Button - Force White (Robust Fix) */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarExpandButton"] {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebarCollapseButton"] svg, 
        [data-testid="stSidebarExpandButton"] svg {
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }

        [data-testid="stSidebarCollapseButton"] svg path, 
        [data-testid="stSidebarExpandButton"] svg path {
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }
        
        /* Sidebar Text Fix - Always Light */
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown {
            color: #e0e0e0 !important;
        }

        /* Sidebar Headers - Reduced Size */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            font-size: 1.2rem !important; /* Tamanho ajustado/menor */
            font-weight: 700 !important;
            color: #ffffff !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: 0.5px !important;
        }

        /* File Uploader - Label & General Text (Uploaded Files) -> WHITE */
        section[data-testid="stSidebar"] .stFileUploader label,
        section[data-testid="stSidebar"] .stFileUploader div,
        section[data-testid="stSidebar"] .stFileUploader span,
        section[data-testid="stSidebar"] .stFileUploader small {
             color: #e0e0e0 !important;
             caret-color: #e0e0e0 !important;
        }

        /* File Uploader - Internal Text Dark (Dropzone ONLY) -> DARK */
        section[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] label,
        section[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] div,
        section[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] span,
        section[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] small {
             color: #31333F !important;
        }
        
        /* Help Text (Markdown) - White */
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
             color: #e0e0e0 !important;
        }

        /* Sidebar Expander (Configurar Transbordo) - Force Navy Background & White Text */
        /* Sidebar Expander (Configurar Transbordo) - BRUTE FORCE FIX */
        section[data-testid="stSidebar"] details {
            background-color: #0d1b2a !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
        }

        section[data-testid="stSidebar"] details > summary {
            background-color: #0d1b2a !important;
            color: #ffffff !important;
            border: 1px solid rgba(0, 132, 255, 0.2) !important;
        }

        section[data-testid="stSidebar"] details > summary:hover {
             color: #0084FF !important;
             border-color: #0084FF !important;
        }

        /* Force ALL children of summary (icons, text, pointers) to be white/current */
        section[data-testid="stSidebar"] details > summary * {
            color: inherit !important;
            fill: inherit !important;
            stroke: inherit !important;
        }
        
        /* Fallback for older Streamlit versions */
        section[data-testid="stSidebar"] .streamlit-expanderHeader {
            background-color: #0d1b2a !important;
            color: #ffffff !important;
        }
        
        /* Metric Cards */
        .stMetric {
            background-color: var(--background-color);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--secondary-background-color);
        }
        
        /* Loggi Blue Accents */
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
        }
        
        h1, h2, h3 {
            color: #0084FF !important;
            font-family: 'Inter', sans-serif;
        }
        
        /* Custom info box */
        .info-box {
            padding: 1rem;
            background-color: var(--secondary-background-color);
            border-left: 5px solid #0084FF;
            border-radius: 4px;
            margin-bottom: 1rem;
            color: var(--text-color);
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    inject_custom_css()

    with st.sidebar:
        page = option_menu(
            "Navegacao",
            ["Dashboard Geral", "Detalhamento e KPIs", "Gestao de Lacres", "Gestao de SLA"],
            icons=['speedometer2', 'bar-chart-line', 'box-seam', 'exclamation-triangle'],
            menu_icon="compass",
            default_index=0,
            styles={
                "container": {"padding": "0 !important", "background-color": "#0d1b2a", "border-radius": "0 !important"},
                "icon": {"color": "#0084FF", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#1c2e40", "color": "#e0e0e0", "border-radius": "0px"},
                "nav-link-selected": {"background-color": "#0084FF", "font-weight": "600", "color": "#ffffff", "border-radius": "0px"},
                "menu-title": {"color": "#ffffff", "font-weight": "700", "font-size": "1.2rem", "margin-bottom": "0.5rem"},
            }
        )
    st.sidebar.markdown("---")

    st.sidebar.header("Carregar Dados", divider="gray")
    deduplicate_data = st.sidebar.checkbox(
        "Deduplicar pacotes automaticamente",
        value=True,
        help="Remove duplicidade entre arquivos usando package_id e barcode."
    )
    uploaded_files = st.sidebar.file_uploader(
        "Arquivos CSV",
        type=["csv"],
        accept_multiple_files=True,
        help="Carregue um ou mais arquivos de remessa."
    )

    if not uploaded_files:
        render_home()
        return

    df = utils.load_and_combine_data(uploaded_files, deduplicate=deduplicate_data)
    if df.empty:
        st.warning("Nenhum dado valido encontrado nos arquivos.")
        return

    schema_report = utils.validate_dataframe_schema(df)
    if not schema_report["is_valid"]:
        missing_required = ", ".join(schema_report["missing_required"])
        st.error(f"Erro de schema: colunas obrigatorias ausentes: {missing_required}")
        logger.error("schema_validation_failed missing_required=%s", schema_report["missing_required"])
        return

    if schema_report["missing_recommended"]:
        missing_recommended = ", ".join(schema_report["missing_recommended"])
        st.warning(
            f"Colunas recomendadas ausentes: {missing_recommended}. Algumas visoes podem ficar limitadas."
        )
        logger.warning("schema_missing_recommended missing=%s", schema_report["missing_recommended"])

    todas_agencias = utils.get_unique_agencies(df)
    persisted_trasbordo = [
        agency for agency in config_manager.load_transbordo_agencies()
        if agency in todas_agencias
    ]
    with st.sidebar.expander("Configurar Transbordo", expanded=False, icon=":material/settings:"):
        lista_trasbordo = st.multiselect(
            "Agencias de Transbordo:",
            options=todas_agencias,
            default=persisted_trasbordo
        )

    if set(lista_trasbordo) != set(persisted_trasbordo):
        config_manager.save_transbordo_agencies(lista_trasbordo)
        logger.info("transbordo_saved count=%s", len(lista_trasbordo))

    df_processed = utils.process_data(df, lista_trasbordo)

    if page == "Dashboard Geral":
        render_dashboard_geral(df_processed)
    elif page == "Detalhamento e KPIs":
        render_detalhamento_kpis(df_processed)
    elif page in ["Gestao de Lacres", "Gestão de Lacres"]:
        render_gestao_lacres(df_processed)
    elif page in ["Gestao de SLA", "Gestão de SLA"]:
        render_sla_expedicao(df_processed)

# ... (Existing functions)

def render_gestao_lacres(df):
    st.title("Gestao de Lacres", anchor=False)
    st.markdown("#### :material/package_2: Visao agrupada por Lacres, vinculando agencias e veiculos.")
    st.markdown("---")
    
    if 'seal' not in df.columns:
        st.error("Erro: Coluna 'seal' não encontrada nos dados.")
        return

    # Processar agrupamento
    df_seals = utils.group_data_by_seal(df)
    
    # --- Filtros Avançados ---
    st.markdown("### :material/search: Filtros")
    
    # Layout de Filtros (5 colunas para acomodar busca de pacote)
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
    
    with f_col1:
        search_seal = st.text_input("Buscar Lacre (Seal)", placeholder="Ex: CJ2...")
    
    with f_col2:
        with st.form(key='search_form', clear_on_submit=False, border=False):
            search_package_input = st.text_input("Buscar Pacote/Barcode", placeholder="Digite ID + Enter")
            # Botão de busca explícito para melhorar UX
            submitted = st.form_submit_button("Buscar Pacote", use_container_width=True)
            
        # O valor é atualizado quando submete ou quando aperta enter dentro do form
        search_package = search_package_input
        
    with f_col3:
        filtro_agencia = st.multiselect("Destino", options=sorted(df_seals['agência_destino_anotacao'].unique()))
    
    with f_col4:
        # Filtro de Veículo (Identificador Real - Placa)
        if 'Identificador' in df_seals.columns:
            veiculos_reais = sorted([v for v in df_seals['Identificador'].dropna().unique() if v not in ['-', 'Indefinido', '']])
            filtro_veiculo = st.multiselect("Veículo/Placa", options=veiculos_reais)
        else:
            filtro_veiculo = []

    with f_col5:
        # Filtro de Data Promessa
        min_date = pd.to_datetime(df_seals['Data_Promessa_Min']).min()
        max_date = pd.to_datetime(df_seals['Data_Promessa_Min']).max()
        if pd.notna(min_date) and pd.notna(max_date):
            date_range = st.date_input("Intervalo de Promessa", value=(min_date, max_date))
        else:
            date_range = None
        
    df_view = df_seals.copy()
    
    # Aplicação dos Filtros
    
    # Lógica de Busca Reversa (Pacote -> Seal)
    found_packages_list = [] # Armazenar IDs encontrados para destacar depois
    
    if search_package:
        # Normalizar entrada: separar por vírgula ou espaço e remover vazios
        search_terms = [t.strip() for t in search_package.replace(',', ' ').split() if t.strip()]
        
        if search_terms:
            # Procurar no DataFrame original (nível pacote)
            mask_package = pd.Series(False, index=df.index)
            
            for term in search_terms:
                if 'package_id' in df.columns:
                     mask_package |= df['package_id'].astype(str).str.contains(term, case=False, na=False)
                if 'barcode' in df.columns:
                     mask_package |= df['barcode'].astype(str).str.contains(term, case=False, na=False)
            
            # Identificar quais pacotes foram encontrados (para destaque)
            # Vamos salvar os IDs ou Barcodes que deram match
            df_matches = df[mask_package]
            found_seals = df_matches['seal'].unique()
            
            # Guardar lista de IDs/Barcodes encontrados para uso no highlight
            if 'package_id' in df_matches.columns:
                found_packages_list.extend(df_matches['package_id'].astype(str).tolist())
            if 'barcode' in df_matches.columns:
                found_packages_list.extend(df_matches['barcode'].astype(str).tolist())
            
            if len(found_seals) > 0:
                st.success(f"Encontrado(s) {len(df_matches)} pacote(s) em {len(found_seals)} lacre(s): {', '.join(found_seals)}")
                # Filtrar a visão consolidada para mostrar apenas esses seals
                df_view = df_view[df_view['seal'].isin(found_seals)]
            else:
                st.warning(f"Nenhum pacote encontrado para os termos: {', '.join(search_terms)}")
                df_view = df_view[df_view['seal'] == 'NENHUM'] # Hack para esvaziar
        
    # Guardar estado da busca para usar no drill-down
    st.session_state['highlight_packages'] = found_packages_list
    
    if search_seal:
        df_view = df_view[df_view['seal'].str.contains(search_seal, case=False, na=False)]
    if filtro_agencia:
        df_view = df_view[df_view['agência_destino_anotacao'].isin(filtro_agencia)]
    if filtro_veiculo:
        df_view = df_view[df_view['Identificador'].isin(filtro_veiculo)]
    if date_range and len(date_range) == 2:
         df_view['Data_Promessa_Min'] = pd.to_datetime(df_view['Data_Promessa_Min'])
         df_view = df_view[
             (df_view['Data_Promessa_Min'] >= pd.to_datetime(date_range[0])) & 
             (df_view['Data_Promessa_Min'] <= pd.to_datetime(date_range[1]))
         ]

    # KPIs Rápidos
    k1, k2, k3 = st.columns(3)
    k1.metric("Total de Lacres", len(df_view))
    k2.metric("Total de Pacotes", f"{df_view['Qtd_Pacotes'].sum():,}".replace(",", "."))
    k3.metric("Veículos Distintos", df_view['Identificador'].nunique())
    
    st.markdown("### Lista de Lacres")
    
    # Exibir Tabela Interativa
    event = st.dataframe(
        df_view[['seal', 'agência_destino_anotacao', 'Tipo_Veiculo', 'Identificador', 'Qtd_Pacotes', 'Data_Promessa_Min']],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        column_config={
             "Data_Promessa_Min": st.column_config.DateColumn("Data Promessa (Min)", format="DD/MM/YYYY")
        }
    )
    
    # Drill-down (Detalhes do Lacre Selecionado)
    selected_indices = event.selection.rows
    
    # Gerenciamento de Estado de Visualização (Lacres)
    if 'last_selected_lacres' not in st.session_state:
        st.session_state['last_selected_lacres'] = None
    if 'show_details_lacres' not in st.session_state:
        st.session_state['show_details_lacres'] = False
        
    # Lógica de Detecção de Mudança
    if selected_indices != st.session_state['last_selected_lacres']:
        st.session_state['last_selected_lacres'] = selected_indices
        st.session_state['show_details_lacres'] = True if selected_indices else False

    if st.session_state['show_details_lacres'] and selected_indices:
        selected_index = selected_indices[0]
        # Validar índice
        if selected_index < len(df_view):
            selected_row = df_view.iloc[selected_index]
            seal_selecionado = selected_row['seal']
            
            st.divider()
            st.subheader(f":material/search: Detalhes do Lacre: {seal_selecionado}")
            st.caption(f"Destino: {selected_row['agência_destino_anotacao']} | Veículo: {selected_row['Identificador']}")
            
            # Filtrar pacotes originais deste seal
            pacotes_do_seal = df[df['seal'] == seal_selecionado].copy()
            
            # Mostrar apenas colunas disponiveis para evitar quebra com CSVs incompletos
            cols_detalhe = ['barcode', 'nfe_key', 'company_name', 'promised_date', 'package_id', 'Status']
            cols_detalhe_existentes = [c for c in cols_detalhe if c in pacotes_do_seal.columns]
            if not cols_detalhe_existentes:
                st.info("Nenhuma coluna de detalhe disponivel para este lacre.")
                return

            df_display = pacotes_do_seal[cols_detalhe_existentes]
            
            # Função para destacar linhas encontradas
            def highlight_matches(row):
                matches = st.session_state.get('highlight_packages', [])
                if not matches:
                    return [''] * len(row)
                
                pid_value = row.get('package_id', '')
                barcode_value = row.get('barcode', '')
                pid = str(pid_value) if pd.notna(pid_value) else ''
                barcode = str(barcode_value) if pd.notna(barcode_value) else ''
                
                # Verifica se o ID ou Barcode está na lista de encontrados
                if pid in matches or barcode in matches:
                    # Amarelo claro para destaque (compatível com light/dark mode geralmente, mas vamos forçar cor de texto escura)
                    return ['background-color: #ffeb3b; color: black; font-weight: bold'] * len(row)
                return [''] * len(row)

            column_config_detalhe = {}
            if 'promised_date' in cols_detalhe_existentes:
                column_config_detalhe["promised_date"] = st.column_config.DateColumn("Prazo", format="DD/MM/YYYY")

            st.dataframe(
                df_display.style.apply(highlight_matches, axis=1),
                use_container_width=True,
                column_config=column_config_detalhe
            )
            
            if st.button("Fechar Detalhes", key="btn_close_lacres", icon=":material/close:"):
                st.session_state['show_details_lacres'] = False
                st.rerun()



def render_home():
    st.title("Bem-vindo ao XDDF Transbordo", anchor=False)
    
    st.markdown("""
    <div class='info-box'>
        Este painel centraliza a análise operacional de remessas, segregando fluxos de <b>Transbordo</b> e <b>Processo</b>.
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### :material/folder_open: 1. Carregue")
        st.info("Faça upload de múltiplos arquivos CSV de remessa na barra lateral.")
        
    with c2:
        st.markdown("### :material/settings: 2. Configure")
        st.info("Defina quais agencias sao de Transbordo e ajuste os tempos de transito (SLA).")
        
    with c3:
        st.markdown("### :material/analytics: 3. Analise")
        st.info("Visualize KPIs, identifique gargalos e monitore prazos de expedição.")

    st.divider()
    
    st.subheader(":material/rocket_launch: Funcionalidades Principais")
    row1 = st.columns(2)
    row1[0].markdown("""
    **Gestao de Lacres**
    - Agrupamento inteligente por Seal.
    - Identificacao de veiculos e placas.
    - Drill-down para ver pacotes individuais.
    """)
    
    row1[1].markdown("""
    **Controle de SLA & Expedicao**
    - Calculo automatico de data limite de saida.
    - Monitoramento de risco (Critico, Atencao).
    - Configuracao persistente por agencia.
    """)

def render_dashboard_geral(df):
    st.title("Dashboard Geral", anchor=False)
    st.markdown("#### :material/bar_chart: Visão consolidada de volume por agência, categoria e veículos.")
    st.markdown("---")
    
    # Filtros Linha 1
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        cat_filter = st.multiselect("Filtrar Categoria", ["Transbordo", "Processo"], default=["Transbordo", "Processo"])
    with col_f2:
        # Filtro de Agências (Novo)
        all_agencies = sorted(df['agência_destino_anotacao'].unique()) if 'agência_destino_anotacao' in df.columns else []
        agency_filter = st.multiselect("Filtrar Agências", all_agencies, placeholder="Todas as agências")
    
    # Filtros Linha 2 (Novos)
    col_f3, col_f4 = st.columns(2)
    
    # Filtro de Veículos
    with col_f3:
        if 'Identificador' in df.columns:
            # Opções de veículos (remove nulos e vazios para a lista)
            veiculos_opcoes = sorted([v for v in df['Identificador'].dropna().unique() if v not in ['-', 'Indefinido', '']])
            veiculo_filter = st.multiselect("Filtrar Veículos (Placa/ID)", veiculos_opcoes, placeholder="Todos os veículos")
        else:
            veiculo_filter = []

    # Filtro de Arquivos
    with col_f4:
        if 'source_file' in df.columns:
            arquivos_opcoes = sorted(df['source_file'].dropna().unique())
            arquivo_filter = st.multiselect("Filtrar Arquivo de Origem", arquivos_opcoes, placeholder="Todos os arquivos")
        else:
            arquivo_filter = []
    
    # Aplicar Filtros
    df_filtered = df[df['Categoria'].isin(cat_filter)]
    
    if agency_filter:
        df_filtered = df_filtered[df_filtered['agência_destino_anotacao'].isin(agency_filter)]
        
    if veiculo_filter:
         df_filtered = df_filtered[df_filtered['Identificador'].isin(veiculo_filter)]
         
    if arquivo_filter:
         df_filtered = df_filtered[df_filtered['source_file'].isin(arquivo_filter)]
    
    # KPIs Topo
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total = len(df_filtered)
    vol_transbordo = len(df_filtered[df_filtered['Categoria'] == 'Transbordo'])
    vol_processo = len(df_filtered[df_filtered['Categoria'] == 'Processo'])
    
    # KPI de Veículos (Novo)
    if 'Identificador' in df_filtered.columns:
        # Conta veículos únicos que não sejam placeholder
        veiculos_unicos = df_filtered[
            (~df_filtered['Identificador'].isin(['-', 'Indefinido'])) & 
            (df_filtered['Identificador'].notna())
        ]['Identificador'].nunique()
    else:
        veiculos_unicos = 0
    
    kpi1.metric("Volume Total", f"{total:,}".replace(",", "."))
    kpi2.metric("Transbordo", f"{vol_transbordo:,} ({vol_transbordo/total*100:.1f}%)" if total else "0")
    kpi3.metric("Processo", f"{vol_processo:,} ({vol_processo/total*100:.1f}%)" if total else "0")
    kpi4.metric("Veículos Envolvidos", veiculos_unicos)
    
    st.markdown("### Volume por Agência")
    
    # Gráfico Principal
    agrupado = df_filtered.groupby(['agência_destino_anotacao', 'Categoria']).size().reset_index(name='Volume')
    agrupado = agrupado.sort_values('Volume', ascending=False)
    
    fig = px.bar(
        agrupado, x='agência_destino_anotacao', y='Volume', color='Categoria',
        color_discrete_map={"Transbordo": "#FF9F00", "Processo": "#0084FF"}, # Laranja e Azul Loggi
        text='Volume'
    )
    fig.update_layout(xaxis_title="Agência", yaxis_title="Volume")
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Exportação de Dados (Agências) ---
    if not df_filtered.empty:
        # Pivotar dados: Agência x Categoria
        df_export = df_filtered.groupby(['agência_destino_anotacao', 'Categoria']).size().unstack(fill_value=0)
        
        # Garantir colunas
        if 'Transbordo' not in df_export.columns: df_export['Transbordo'] = 0
        if 'Processo' not in df_export.columns: df_export['Processo'] = 0
        
        # Calcular Totais
        df_export['Total Geral'] = df_export['Transbordo'] + df_export['Processo']
        
        # Calcular Grand Total (Soma de todos os itens do contexto atual)
        grand_total = df_export['Total Geral'].sum()
        
        # Calcular Percentuais baseados no TOTAL GERAL (Share of Total)
        # Ex: Se Total Geral é 100 e Agência X tem 12 Transbordo, % Transbordo = 12%
        if grand_total > 0:
            df_export['% Transbordo'] = (df_export['Transbordo'] / grand_total * 100).fillna(0).round(2)
            df_export['% Processo'] = (df_export['Processo'] / grand_total * 100).fillna(0).round(2)
            df_export['% do Total'] = (df_export['Total Geral'] / grand_total * 100).fillna(0).round(2)
        else:
            df_export['% Transbordo'] = 0.0
            df_export['% Processo'] = 0.0
            df_export['% do Total'] = 0.0
        
        # Ordenar e formatar
        df_export = df_export.sort_values('Total Geral', ascending=False)
        
        # Renomear índice para o CSV
        df_export.index.name = "Agencias/ leves"
        
        # Botão de Download
        csv_export = df_export.to_csv().encode('utf-8')
        
        # Nome do arquivo dinâmico
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
        file_name = f"Relatorio_Volume_Agencias_{timestamp}.csv"
        
        st.download_button(
            label=f"Baixar Relatório Detalhado (CSV) - Total: {grand_total}",
            data=csv_export,
            file_name=file_name,
            mime="text/csv"
        )
    
    # --- Visão de Veículos (Novo) ---
    if veiculos_unicos > 0:
        st.markdown("### :material/local_shipping: Veículos e Caminhões")
        cv1, cv2 = st.columns([1, 1])
        
        with cv1:
            st.markdown("#### Top Veículos por Volume")
            df_veiculos = df_filtered[
                (~df_filtered['Identificador'].isin(['-', 'Indefinido']))
            ].groupby(['Identificador', 'Tipo_Veiculo']).size().reset_index(name='Volume')
            
            df_veiculos = df_veiculos.sort_values('Volume', ascending=False).head(10)
            
            fig_veiculos = px.bar(
                df_veiculos,
                x='Volume',
                y='Identificador',
                orientation='h',
                color='Tipo_Veiculo',
                text='Volume'
            )
            fig_veiculos.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_veiculos, use_container_width=True)
            
        with cv2:
            st.markdown("#### Detalhes")
            st.dataframe(
                df_veiculos,
                use_container_width=True,
                hide_index=True
            )
    
    st.markdown("---")
    
    # --- KPI de Pacotes Críticos ---
    st.subheader(":material/warning: Pacotes Críticos (Vencimento)")
    st.caption("Foco em volumes atrasados ou vencendo hoje. Clique na data para ver detalhes.")
    
    # 1. Filtrar Críticos
    if 'Status_Prazo' in df_filtered.columns:
        df_critical = df_filtered[df_filtered['Status_Prazo'].isin(['Atrasado', 'Vence Hoje'])].copy()
        
        if not df_critical.empty:
            # Métricas
            c1, c2, c3 = st.columns(3)
            with c1:
                tc = len(df_critical)
                st.metric("Total Crítico", tc, delta="Ação Necessária", delta_color="inverse")
            with c2:
                ta = len(df_critical[df_critical['Status_Prazo'] == 'Atrasado'])
                st.metric("Atrasados", ta, delta_color="inverse")
            with c3:
                th = len(df_critical[df_critical['Status_Prazo'] == 'Vence Hoje'])
                st.metric("Vence Hoje", th, delta_color="off")
            
            # 2. Agrupamento por Data
            df_critical['Data Vencimento'] = pd.to_datetime(df_critical['promised_date']).dt.date
            
            vol_por_data = df_critical.groupby(['Data Vencimento', 'Status_Prazo']).size().reset_index(name='Volume')
            vol_por_data = vol_por_data.sort_values('Data Vencimento')
            
            col_chart, col_list = st.columns([1, 1])
            
            with col_chart:
                st.markdown("#### Volume por Data")
                # Gráfico Simples
                fig_crit = px.bar(
                    vol_por_data, 
                    x='Data Vencimento', 
                    y='Volume', 
                    color='Status_Prazo',
                    color_discrete_map={"Atrasado": "#FF4B4B", "Vence Hoje": "#FFA421"},
                    text='Volume'
                )
                st.plotly_chart(fig_crit, use_container_width=True)

            with col_list:
                st.markdown("#### Selecione uma Data")
                # Tabela Interativa de Datas
                event_date = st.dataframe(
                    vol_por_data,
                    use_container_width=True,
                    hide_index=True,
                    selection_mode="single-row",
                    on_select="rerun",
                     column_config={
                        "Data Vencimento": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                        "Status_Prazo": st.column_config.TextColumn("Situação"),
                        "Volume": st.column_config.NumberColumn("Qtd Pacotes")
                    }
                )
            
            # 3. Drill-down (Detalhes)
            if event_date.selection.rows:
                idx = event_date.selection.rows[0]
                row_sel = vol_por_data.iloc[idx]
                data_sel = row_sel['Data Vencimento']
                status_sel = row_sel['Status_Prazo']
                
                # Filtrar Pacotes do Dia/Status Selecionado
                # Garantir comparação de data clean
                df_detalhe = df_critical[
                    (pd.to_datetime(df_critical['promised_date']).dt.date == data_sel) &
                    (df_critical['Status_Prazo'] == status_sel)
                ].copy()
                
                st.divider()
                st.markdown(f"### :material/list_alt: Detalhes: {data_sel.strftime('%d/%m/%Y')} - {status_sel}")
                st.caption(f"Listando {len(df_detalhe)} pacotes encontrados.")
                
                # Colunas para exibir
                cols_view = ['package_id', 'seal', 'agência_destino_anotacao', 'barcode', 'nfe_key', 'company_name']
                # Verificar se existem
                cols_final = [c for c in cols_view if c in df_detalhe.columns]
                
                st.dataframe(
                    df_detalhe[cols_final],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "package_id": "ID Pacote",
                        "seal": "Seal (Malote)",
                        "agência_destino_anotacao": "Agência Destino",
                        "barcode": "Cód. Barras",
                        "nfe_key": "Chave NFe",
                        "company_name": "Cliente"
                    }
                )
                
                # 4. Botão de Exportação (CSV)
                csv = df_detalhe[cols_final].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar Dados (CSV)",
                    data=csv,
                    file_name=f"relatorio_critico_{data_sel}_{status_sel}.csv",
                    mime="text/csv",
                    icon=":material/download:",
                    type="primary"
                )
                
        else:
            st.success("Nenhum pacote crítico encontrado! Operação saudável.", icon=":material/thumb_up:")
    else:
        st.info("Dados de prazo não disponíveis para cálculo.", icon=":material/info:")

def render_detalhamento_kpis(df):
    st.title("Detalhamento e KPIs", anchor=False)
    st.markdown("#### :material/analytics: Análise Tática e Saúde Operacional")

    if df.empty:
        st.warning("Sem dados para analisar.")
        return

    AGENCY_COL_PREF = "agência_destino_anotacao"
    AGENCY_COL_FALLBACK = "agencia_destino_anotacao"

    STATUS_SEM_DATA = "Sem Data"
    STATUS_ATRASADO = "Atrasado"
    STATUS_VENCE_HOJE = "Vence Hoje"
    STATUS_ATENCAO = "Atenção"
    STATUS_NO_PRAZO = "No Prazo"

    def get_agency_col(columns):
        if AGENCY_COL_PREF in columns:
            return AGENCY_COL_PREF
        if AGENCY_COL_FALLBACK in columns:
            return AGENCY_COL_FALLBACK
        return None

    agency_col = get_agency_col(df.columns)

    def ensure_status_prazo(df_input):
        if 'Status_Prazo' in df_input.columns:
            return df_input
        if 'promised_date' not in df_input.columns:
            return df_input

        df_out = df_input.copy()
        promised = pd.to_datetime(df_out['promised_date'], errors='coerce', dayfirst=True)
        hoje = pd.Timestamp.now().normalize()
        delta = (promised.dt.normalize() - hoje).dt.days

        status = pd.Series(STATUS_NO_PRAZO, index=df_out.index, dtype='object')
        status = status.mask(promised.isna(), STATUS_SEM_DATA)
        status = status.mask(delta < 0, STATUS_ATRASADO)
        status = status.mask(delta == 0, STATUS_VENCE_HOJE)
        status = status.mask(delta == 1, STATUS_ATENCAO)

        df_out['Status_Prazo'] = status
        return df_out

    def semaforo_pct(value, green_max, yellow_max, orange_max):
        if value <= green_max:
            return 'green'
        if value <= yellow_max:
            return 'yellow'
        if value <= orange_max:
            return 'orange'
        return 'red'

    def semaforo_score(value):
        if value >= 90:
            return 'green'
        if value >= 80:
            return 'yellow'
        if value >= 70:
            return 'orange'
        return 'red'

    def color_for(level):
        colors = {
            'green': '#16A34A',
            'yellow': '#EAB308',
            'orange': '#F97316',
            'red': '#DC2626',
            'gray': '#64748B',
        }
        return colors.get(level, colors['gray'])

    def render_kpi_card(container, title, value, subtitle, level):
        color = color_for(level)
        container.markdown(
            f"""
            <div style="border:1px solid #e5e7eb; border-left:6px solid {color}; border-radius:12px; padding:14px 16px; min-height:132px; background:#ffffff08;">
                <div style="font-size:14px; opacity:0.85; margin-bottom:8px;">{title}</div>
                <div style="font-size:42px; font-weight:700; line-height:1.0; margin-bottom:8px;">{value}</div>
                <div style="font-size:14px; color:{color}; font-weight:600;">{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.container():
        c1, c2, c3 = st.columns(3)

        with c1:
            if agency_col:
                agencias = sorted(df[agency_col].fillna('N/A').astype(str).unique())
            else:
                agencias = []
            filtro_agencia = st.multiselect("Filtrar Agências", options=agencias)

        with c2:
            filtro_status = st.multiselect(
                "Filtrar Status Prazo",
                options=[STATUS_NO_PRAZO, STATUS_ATENCAO, STATUS_ATRASADO, STATUS_VENCE_HOJE],
                default=[STATUS_ATRASADO, STATUS_VENCE_HOJE],
            )

        with c3:
            if 'promised_date' in df.columns:
                promised_all = pd.to_datetime(df['promised_date'], errors='coerce', dayfirst=True)
                min_d = promised_all.min()
                max_d = promised_all.max()
                if pd.notna(min_d) and pd.notna(max_d):
                    date_range = st.date_input("Período (Data Promessa)", value=(min_d.date(), max_d.date()))
                else:
                    date_range = None
            else:
                date_range = None

    df_base = df.copy()

    if filtro_agencia and agency_col:
        df_base = df_base[df_base[agency_col].isin(filtro_agencia)]

    if date_range and len(date_range) == 2 and 'promised_date' in df_base.columns:
        promised_base = pd.to_datetime(df_base['promised_date'], errors='coerce', dayfirst=True)
        df_base = df_base[
            (promised_base.dt.date >= date_range[0]) &
            (promised_base.dt.date <= date_range[1])
        ]

    df_base = ensure_status_prazo(df_base)

    df_view = df_base.copy()
    if filtro_status and 'Status_Prazo' in df_view.columns:
        df_view = df_view[df_view['Status_Prazo'].isin(filtro_status)]

    st.caption("Base KPI: Completa (agências + período). O filtro de status afeta gráficos e tabela.")
    st.markdown("---")

    total_base = len(df_base)
    if total_base > 0 and 'Status_Prazo' in df_base.columns:
        count_status = df_base['Status_Prazo'].value_counts()
        atrasados = int(count_status.get(STATUS_ATRASADO, 0))
        vence_hoje = int(count_status.get(STATUS_VENCE_HOJE, 0))
        atencao = int(count_status.get(STATUS_ATENCAO, 0))
        no_prazo = int(count_status.get(STATUS_NO_PRAZO, 0))

        backlog_critico = atrasados + vence_hoje

        taxa_atraso = (atrasados / total_base) * 100
        pct_vence_hoje = (vence_hoje / total_base) * 100
        pct_atencao = (atencao / total_base) * 100
        eficiencia = max(0.0, 100 - taxa_atraso)

        score_sla = max(0.0, min(100.0, 100 - (1.2 * taxa_atraso + 0.8 * pct_vence_hoje + 0.4 * pct_atencao)))

        hoje = pd.Timestamp.now().normalize()
        dias_medio_atraso = 0.0
        if atrasados > 0 and 'promised_date' in df_base.columns:
            promised_atraso = pd.to_datetime(
                df_base.loc[df_base['Status_Prazo'] == STATUS_ATRASADO, 'promised_date'],
                errors='coerce',
                dayfirst=True,
            ).dt.normalize()
            delta_atraso = (hoje - promised_atraso).dt.days
            delta_atraso = delta_atraso[delta_atraso >= 0]
            if not delta_atraso.empty:
                dias_medio_atraso = float(delta_atraso.mean())

        backlog_pct = (backlog_critico / total_base) * 100

        level_backlog = semaforo_pct(backlog_pct, 8, 15, 25)
        level_taxa_atraso = semaforo_pct(taxa_atraso, 2, 5, 10)
        level_eficiencia = 'green' if eficiencia >= 98 else ('yellow' if eficiencia >= 95 else ('orange' if eficiencia >= 90 else 'red'))
        level_score = semaforo_score(score_sla)
        level_vence_hoje = semaforo_pct(pct_vence_hoje, 5, 10, 20)
        level_atencao = semaforo_pct(pct_atencao, 10, 20, 35)
        level_dias_atraso = 'green' if dias_medio_atraso <= 0.2 else ('yellow' if dias_medio_atraso <= 1 else ('orange' if dias_medio_atraso <= 2 else 'red'))
        level_volume = 'gray'

        if agency_col and backlog_critico > 0:
            top_impacto = (
                df_base[df_base['Status_Prazo'].isin([STATUS_ATRASADO, STATUS_VENCE_HOJE])][agency_col]
                .value_counts()
                .head(3)
            )
            impacto_texto = ' | '.join([f"{ag}: {vol}" for ag, vol in top_impacto.items()])
            impacto_concentracao = (top_impacto.sum() / backlog_critico) * 100 if backlog_critico else 0.0
        else:
            impacto_texto = 'Sem concentracao relevante'
            impacto_concentracao = 0.0

        if score_sla < 70 or taxa_atraso > 10:
            estado_operacao = 'CRITICO'
            nivel_estado = 'red'
        elif score_sla < 80 or taxa_atraso > 5 or pct_vence_hoje > 10:
            estado_operacao = 'ALERTA'
            nivel_estado = 'orange'
        elif score_sla < 90 or taxa_atraso > 2:
            estado_operacao = 'ATENCAO'
            nivel_estado = 'yellow'
        else:
            estado_operacao = 'SAUDAVEL'
            nivel_estado = 'green'

        st.markdown(
            f"**Estado da Operacao:** <span style='color:{color_for(nivel_estado)}; font-weight:700;'>{estado_operacao}</span> | "
            f"Score SLA: **{score_sla:.1f}** | Top impacto: {impacto_texto}",
            unsafe_allow_html=True,
        )

        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        render_kpi_card(r1c1, 'Volume Base', f"{total_base:,}".replace(',', '.'), 'Pacotes no periodo', level_volume)
        render_kpi_card(r1c2, 'Backlog Critico', f"{backlog_critico:,}".replace(',', '.'), f"{backlog_pct:.1f}% da base", level_backlog)
        render_kpi_card(r1c3, 'Taxa de Atraso', f"{taxa_atraso:.1f}%", f"Atrasados: {atrasados:,}".replace(',', '.'), level_taxa_atraso)
        render_kpi_card(r1c4, 'Eficiencia de Prazo', f"{eficiencia:.1f}%", f"No prazo: {no_prazo:,}".replace(',', '.'), level_eficiencia)

        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        render_kpi_card(r2c1, '% Vence Hoje', f"{pct_vence_hoje:.1f}%", f"Pacotes: {vence_hoje:,}".replace(',', '.'), level_vence_hoje)
        render_kpi_card(r2c2, '% Atencao', f"{pct_atencao:.1f}%", f"Pacotes: {atencao:,}".replace(',', '.'), level_atencao)
        render_kpi_card(r2c3, 'Dias Medios de Atraso', f"{dias_medio_atraso:.1f}", 'Gravidade do backlog', level_dias_atraso)
        render_kpi_card(r2c4, 'Score SLA', f"{score_sla:.1f}", f"Concentracao Top 3: {impacto_concentracao:.1f}%", level_score)

    else:
        st.info('Sem base suficiente para calcular KPIs.')

    st.markdown('---')

    g1, g2 = st.columns([1, 1])

    with g1:
        st.subheader(':material/bar_chart: Top 10 Gargalos (Pareto)')
        if 'Status_Prazo' in df_view.columns and not df_view.empty:
            df_atraso = df_view[df_view['Status_Prazo'] == STATUS_ATRASADO]
            if not df_atraso.empty and agency_col:
                pareto = df_atraso[agency_col].value_counts().reset_index()
                pareto.columns = ['Agencia', 'Volume Atrasado']
                pareto = pareto.head(10)

                fig_pareto = px.bar(
                    pareto,
                    x='Volume Atrasado',
                    y='Agencia',
                    orientation='h',
                    text='Volume Atrasado',
                    color='Volume Atrasado',
                    color_continuous_scale='Reds'
                )
                fig_pareto.update_layout(yaxis=dict(autorange='reversed'))
                st.plotly_chart(fig_pareto, use_container_width=True)
            else:
                st.success('Nenhum atraso registrado na selecao atual.')
        else:
            st.info('Sem dados de status para gerar Pareto.')

    with g2:
        st.subheader(':material/show_chart: Curva de Vencimento')
        if 'promised_date' in df_view.columns and not df_view.empty:
            df_curve = df_view.copy()
            df_curve['Data_Vencimento'] = pd.to_datetime(df_curve['promised_date'], errors='coerce', dayfirst=True)
            df_curve = df_curve.dropna(subset=['Data_Vencimento'])

            if df_curve.empty:
                st.info('Sem datas validas para gerar curva.')
            else:
                periodos = sorted(df_curve['Data_Vencimento'].dt.to_period('M').unique())
                if periodos:
                    hoje_periodo = pd.Timestamp.now().to_period('M')
                    periodo_default = hoje_periodo if hoje_periodo in periodos else periodos[-1]
                    labels = [p.strftime('%m/%Y') for p in periodos]
                    label_default = periodo_default.strftime('%m/%Y')
                    idx_default = labels.index(label_default) if label_default in labels else len(labels) - 1

                    mes_selecionado = st.selectbox(
                        'Mes da curva',
                        options=labels,
                        index=idx_default,
                        key='curve_month_filter'
                    )
                    periodo_sel = periodos[labels.index(mes_selecionado)]

                    df_mes = df_curve[df_curve['Data_Vencimento'].dt.to_period('M') == periodo_sel].copy()
                    df_mes['Dia_Mes'] = df_mes['Data_Vencimento'].dt.day
                    curve = df_mes.groupby(['Dia_Mes', 'Status_Prazo']).size().reset_index(name='Volume')

                    fig_curve = px.area(
                        curve,
                        x='Dia_Mes',
                        y='Volume',
                        color='Status_Prazo',
                        color_discrete_map={
                            STATUS_ATRASADO: '#FF4B4B',
                            STATUS_VENCE_HOJE: '#FFA421',
                            STATUS_ATENCAO: '#FFD166',
                            STATUS_NO_PRAZO: '#09AB3B',
                        }
                    )
                    fig_curve.update_layout(
                        xaxis_title=f"Dia do mes ({mes_selecionado})",
                        yaxis_title='Volume'
                    )
                    fig_curve.update_xaxes(dtick=1)
                    st.plotly_chart(fig_curve, use_container_width=True)
                else:
                    st.info('Sem periodo mensal disponivel para curva.')
        else:
            st.info('Sem datas para gerar curva.')

    st.markdown('---')

    st.subheader(':material/table: Base de Dados Detalhada')

    cols_padrao = ['package_id', 'seal', 'promised_date', 'Status_Prazo', 'Categoria']
    if agency_col:
        cols_padrao.insert(2, agency_col)

    cols_existentes = [c for c in cols_padrao if c in df_view.columns]

    column_config = {
        'package_id': 'Pacote',
        'seal': 'Lacre',
        'promised_date': st.column_config.DateColumn('Promessa', format='DD/MM/YYYY'),
        'Status_Prazo': st.column_config.TextColumn('Status'),
    }
    if agency_col:
        column_config[agency_col] = 'Agencia'

    st.dataframe(
        df_view[cols_existentes],
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )


def render_sla_expedicao(df):
    st.title("Gestão de SLA e Expedição", anchor=False)
    
    # Explicação Visual da Fórmula
    with st.expander("Entenda o Cálculo do SLO (Expedição)", expanded=True, icon=":material/info:"):
        st.markdown("O sistema calcula a data limite para o lacre sair da origem (SLO) usando a seguinte lógica:")
        st.latex(r'''
        \text{Data Limite Expedição} = \text{Data Promessa} - \text{Buffer (1 Dia)} - \text{Tempo Trânsito} - \text{Tempo Agência}
        ''')
        st.caption("- **Buffer**: Margem de segurança de 1 dia para entrega final.\n- **Tempo Trânsito**: Viagem entre origem e destino.\n- **Tempo Agência**: Processamento interno na ponta.")

    # 1. Configuração de Agências
    st.markdown("### :material/settings: Configuração de Prazos")
    agencias_atuais = utils.get_unique_agencies(df)
    
    # Check if empty
    if not agencias_atuais:
        st.warning("Nenhuma agência encontrada nos dados carregados.")
        return

    df_config = config_manager.get_agency_config_df(agencias_atuais)
    
    # Tabela Editável
    edited_df = st.data_editor(
        df_config, 
        key="editor_sla",
        column_config={
            "Agência": st.column_config.TextColumn(disabled=True),
            "Tempo Trânsito (Dias)": st.column_config.NumberColumn(min_value=0, max_value=30, step=1, format="%d d"),
            "Tempo Agência (Dias)": st.column_config.NumberColumn(min_value=0, max_value=10, step=1, help="Tempo de processo na agência de destino", format="%d d")
        },
        hide_index=True,
        use_container_width=True
    )
    
    col_btn, _ = st.columns([1, 4])
    if col_btn.button("Salvar e Recalcular", type="primary", icon=":material/save:"):
        config_manager.update_config_from_df(edited_df)
        st.toast("Configurações salvas com sucesso!", icon=":material/save:")
        st.rerun()

    st.divider()
    
    # 2. Cálculo do SLA
    with st.spinner("Recalculando prioridades de expedição..."):
        current_config = config_manager.load_config()
        df_sla = utils.calculate_slo(df, current_config)
    
    # 3. Visão de Lacres Críticos
    def get_seal_urgency(series):
        if "Atrasado (Crítico)" in series.values:
            return "Crítico"
        if "Expedir Hoje" in series.values:
            return "Expedir Hoje"
        if "Atenção" in series.values:
             return "Atenção"
        return "No Prazo"

    # Função Helper para Recomendação
    def get_recommendation(status):
        if status == "Crítico":
            return "PRAZO VENCIDO. Expedir imediatamente e tratar como atraso confirmado."
        elif status == "Expedir Hoje":
            return "Vence hoje. Priorizar saída no veículo de hoje."
        elif status == "Atenção":
            return "Ainda no prazo, mas com risco. Planejar veículo para amanhã."
        else:
            return "Seguir fluxo normal."

    if 'seal' in df_sla.columns:
        df_view = df_sla.groupby('seal').agg({
            'agência_destino_anotacao': 'first',
            'Data_Limite_Expedicao': 'min',
            'Status_Expedicao': get_seal_urgency
        }).reset_index()

        df_volume = df_sla.groupby('seal').size().reset_index(name='Qtd Pacotes')
        df_view = df_view.merge(df_volume, on='seal', how='left')
        df_view.rename(columns={'Data_Limite_Expedicao': 'Expedir Até'}, inplace=True)
        
        # Adicionar Coluna de Recomendação
        df_view['Ação Recomendada'] = df_view['Status_Expedicao'].apply(get_recommendation)
        
        # --- Filtros Avançados SLA ---
        st.subheader(f":material/calendar_month: Monitoramento de Expedição")
        st.caption("Utilize os filtros abaixo para localizar lacres específicos ou focar em agências.")
        
        filtro_col1, filtro_col2, filtro_col3, filtro_col4 = st.columns(4)
        
        with filtro_col1:
            search_seal_sla = st.text_input("Buscar Seal", key="search_sla", placeholder="Ex: CJ2...")
        
        with filtro_col2:
             filtro_status = st.multiselect(
                "Status", 
                ["Crítico", "Atenção", "Expedir Hoje", "No Prazo"], 
                default=["Crítico", "Expedir Hoje", "Atenção"]
            )
            
        with filtro_col3:
             filtro_agencia_sla = st.multiselect("Agência Destino", options=sorted(df_view['agência_destino_anotacao'].unique()))

        with filtro_col4:
             # Filtro de Data Expedição
             min_date_sla = pd.to_datetime(df_view['Expedir Até']).min()
             max_date_sla = pd.to_datetime(df_view['Expedir Até']).max()
             if pd.notna(min_date_sla) and pd.notna(max_date_sla):
                 date_range_sla = st.date_input("Data Limite (SLO)", value=(min_date_sla, max_date_sla))
             else:
                 date_range_sla = None

        # Aplicação dos Filtros SLA
        if search_seal_sla:
            df_view = df_view[df_view['seal'].str.contains(search_seal_sla, case=False, na=False)]
            
        if filtro_status:
            df_view = df_view[df_view['Status_Expedicao'].isin(filtro_status)]
            
        if filtro_agencia_sla:
            df_view = df_view[df_view['agência_destino_anotacao'].isin(filtro_agencia_sla)]
            
        if date_range_sla and len(date_range_sla) == 2:
            df_view['Expedir Até'] = pd.to_datetime(df_view['Expedir Até'])
            df_view = df_view[
                (df_view['Expedir Até'] >= pd.to_datetime(date_range_sla[0])) & 
                (df_view['Expedir Até'] <= pd.to_datetime(date_range_sla[1]))
            ]
            
        # Tratar NaT antes de ordenar (ordenação)
        df_view['Expedir Até'] = pd.to_datetime(df_view['Expedir Até'])
        df_view = df_view.sort_values('Expedir Até', na_position='last')
        
        # Visualização Condicional
        if df_view.empty:
            st.success("Nenhum lacre pendente com os filtros selecionados!", icon=":material/check_circle:")
        else:
            # Tabela Interativa (Master)
            # Função de Estilo Pandas
            def highlight_status(val):
                color = 'transparent'
                if val == 'Crítico':
                    color = '#ff4b4b' # Red
                elif val == 'Atenção':
                    color = '#ffa421' # Orange
                elif val == 'Expedir Hoje':
                    color = '#29b5e8' # Blue
                elif val == 'No Prazo':
                    color = '#09ab3b' # Green
                return f'background-color: {color}; color: white; font-weight: bold'

            # Aplicar Estilo
            df_styled = df_view[['seal', 'agência_destino_anotacao', 'Qtd Pacotes', 'Status_Expedicao', 'Expedir Até', 'Ação Recomendada']].style.map(highlight_status, subset=['Status_Expedicao'])

            event = st.dataframe(
                df_styled,
                use_container_width=True,
                column_config={
                    "Expedir Até": st.column_config.DateColumn("Limite de Saída (SLO)", format="DD/MM/YYYY"),
                    "Qtd Pacotes": st.column_config.NumberColumn("Volume", format="%d"),
                    "Ação Recomendada": st.column_config.TextColumn("Diagnóstico & Ação")
                },
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun"
            )
            
            # Detalhes (Detail)
            if event.selection.rows:
                selected_index = event.selection.rows[0]
                selected_row = df_view.iloc[selected_index]
                seal_selecionado = selected_row['seal']
                
                # Container de Detalhes com Estilo Distinto
                st.markdown("---")
                with st.container():
                    st.markdown(f"### :material/expand_more: Detalhando Lacre: `{seal_selecionado}`")
                    st.caption(f"Agência: **{selected_row['agência_destino_anotacao']}** | Status: **{selected_row['Status_Expedicao']}**")
                    
                    # Filtrar e Ordenar Pacotes
                    pacotes_seal = df[df['seal'] == seal_selecionado].copy()
                    
                    # Garantir data
                    if 'promised_date' in pacotes_seal.columns:
                        pacotes_seal['promised_date'] = pd.to_datetime(pacotes_seal['promised_date'], errors='coerce')
                        pacotes_seal = pacotes_seal.sort_values('promised_date', ascending=True, na_position='last')
                    
                    # Exibir Tabela de Pacotes
                    cols_pacotes = ['barcode', 'promised_date', 'Status', 'nfe_key', 'company_name']
                    cols_pacotes_existentes = [c for c in cols_pacotes if c in pacotes_seal.columns]

                    if not cols_pacotes_existentes:
                        st.info("Nenhuma coluna de pacote disponível para este lacre.")
                        return

                    col_cfg_pacotes = {}
                    if "barcode" in cols_pacotes_existentes:
                        col_cfg_pacotes["barcode"] = st.column_config.TextColumn("Pacote / Barcode")
                    if "promised_date" in cols_pacotes_existentes:
                        col_cfg_pacotes["promised_date"] = st.column_config.DateColumn("Vence Em", format="DD/MM/YYYY")
                    if "Status" in cols_pacotes_existentes:
                        col_cfg_pacotes["Status"] = st.column_config.TextColumn("Status Entrega")
                    if "nfe_key" in cols_pacotes_existentes:
                        col_cfg_pacotes["nfe_key"] = st.column_config.TextColumn("Chave NFe")
                    if "company_name" in cols_pacotes_existentes:
                        col_cfg_pacotes["company_name"] = st.column_config.TextColumn("Embarcador")

                    st.dataframe(
                        pacotes_seal[cols_pacotes_existentes],
                        use_container_width=True,
                        column_config=col_cfg_pacotes,
                        hide_index=True
                    )
                    
                    if st.button("Fechar Detalhes"):
                        st.rerun()
        
    else:
        st.error("Coluna 'seal' não encontrada. Verifique se o arquivo contém dados de lacres.")

if __name__ == "__main__":
    main()

