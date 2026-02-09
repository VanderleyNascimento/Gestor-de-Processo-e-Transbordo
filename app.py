import streamlit as st
import pandas as pd
import plotly.express as px
import utils
import config_manager
from streamlit_option_menu import option_menu
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Loggi Transbordo e Processos",
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
        
        /* Sidebar Styling - FIXED LOGGI NAVY */
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
    # Injetar CSS fixo e profissional
    inject_custom_css()

    with st.sidebar:
        page = option_menu(
            "Navegação", 
            ["Dashboard Geral", "Detalhamento e KPIs", "Gestão de Lacres", "Gestão de SLA"],
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

    # Upload global (acessível em ambas as páginas)
    st.sidebar.header("Carregar Dados", divider="gray")
    uploaded_files = st.sidebar.file_uploader(
        "Arquivos CSV", 
        type=["csv"], 
        accept_multiple_files=True,
        help="Carregue um ou mais arquivos de remessa."
    )

    if uploaded_files:
        # Carregamento
        df = utils.load_and_combine_data(uploaded_files)
        
        if not df.empty:
            # Validação básica
            if 'agência_destino_anotacao' not in df.columns:
                 st.error("Erro: Coluna 'agência_destino_anotacao' não encontrada.")
                 return

            # Configuração de Transbordo (Global)
            todas_agencias = utils.get_unique_agencies(df)
            
            with st.sidebar.expander("Configurar Transbordo", expanded=False, icon=":material/settings:"):
                lista_trasbordo = st.multiselect(
                    "Agências de Transbordo:",
                    options=todas_agencias,
                    default=[] 
                )
            
            # Processamento
            df_processed = utils.process_data(df, lista_trasbordo)

            # Roteamento de páginas
            if page == "Dashboard Geral":
                render_dashboard_geral(df_processed)
            elif page == "Detalhamento e KPIs":
                render_detalhamento_kpis(df_processed)
            elif page == "Gestão de Lacres":
                render_gestao_lacres(df_processed)
            elif page == "Gestão de SLA":
                render_sla_expedicao(df_processed)
        
        else:
            st.warning("Nenhum dado válido encontrado nos arquivos.")
    else:
        render_home()

# ... (Existing functions)

def render_gestao_lacres(df):
    st.title("Gestão de Lacres", anchor=False)
    st.markdown("#### :material/package_2: Visão agrupada por Lacres, vinculando agências e veículos.")
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
            submitted = st.form_submit_button("🔍 Buscar Pacote", use_container_width=True)
            
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
            
            # Mostrar colunas solicitadas
            cols_detalhe = ['barcode', 'nfe_key', 'company_name', 'promised_date', 'package_id', 'Status']
            df_display = pacotes_do_seal[cols_detalhe]
            
            # Função para destacar linhas encontradas
            def highlight_matches(row):
                matches = st.session_state.get('highlight_packages', [])
                if not matches:
                    return [''] * len(row)
                
                pid = str(row['package_id']) if pd.notna(row['package_id']) else ''
                barcode = str(row['barcode']) if pd.notna(row['barcode']) else ''
                
                # Verifica se o ID ou Barcode está na lista de encontrados
                if pid in matches or barcode in matches:
                    # Amarelo claro para destaque (compatível com light/dark mode geralmente, mas vamos forçar cor de texto escura)
                    return ['background-color: #ffeb3b; color: black; font-weight: bold'] * len(row)
                return [''] * len(row)

            st.dataframe(
                df_display.style.apply(highlight_matches, axis=1),
                use_container_width=True,
                column_config={
                    "promised_date": st.column_config.DateColumn("Prazo", format="DD/MM/YYYY")
                }
            )
            
            if st.button("Fechar Detalhes", key="btn_close_lacres", icon=":material/close:"):
                st.session_state['show_details_lacres'] = False
                st.rerun()



def render_home():
    st.title("Bem-vindo ao Loggi Transbordo", anchor=False)
    
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
        st.info("Defina quais agências são de Transbordo e ajuste os tempos de trânsito (SLA).")
        
    with c3:
        st.markdown("### :material/analytics: 3. Analise")
        st.info("Visualize KPIs, identifique gargalos e monitore prazos de expedição.")

    st.divider()
    
    st.subheader(":material/rocket_launch: Funcionalidades Principais")
    row1 = st.columns(2)
    row1[0].markdown("""
    **Gestão de Lacres**
    - Agrupamento inteligente por Seal.
    - Identificação de veículos e placas.
    - Drill-down para ver pacotes individuais.
    """)
    
    row1[1].markdown("""
    **Controle de SLA & Expedição**
    - Cálculo automático de data limite de saída.
    - Monitoramento de risco (Crítico, Atenção).
    - Configuração persistente por agência.
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

    # --- 1. Filtros Globais (Barra Superior) ---
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            # Safely get unique agencies
            agencias = sorted(df['agência_destino_anotacao'].fillna("N/A").astype(str).unique()) if 'agência_destino_anotacao' in df.columns else []
            filtro_agencia = st.multiselect("Filtrar Agências", options=agencias)
        with c2:
            filtro_status = st.multiselect(
                "Filtrar Status Prazo",
                options=["No Prazo", "Atenção", "Atrasado", "Vence Hoje"],
                default=["Atrasado", "Vence Hoje"] # Default focado em problema
            )
        with c3:
            # Filtro Data Prometida
            if 'promised_date' in df.columns:
                min_d = pd.to_datetime(df['promised_date']).min()
                max_d = pd.to_datetime(df['promised_date']).max()
                if pd.notna(min_d) and pd.notna(max_d):
                    date_range = st.date_input("Período (Data Promessa)", value=(min_d, max_d))
                else:
                    date_range = None
            else:
                date_range = None

    # Aplicação dos Filtros
    df_view = df.copy()
    if filtro_agencia:
        df_view = df_view[df_view['agência_destino_anotacao'].isin(filtro_agencia)]
    
    # Processar Status se não existir (garantia)
    if 'Status_Prazo' not in df_view.columns and 'promised_date' in df_view.columns:
        hoje = pd.Timestamp.now().normalize()
        def calc_status(d):
            if pd.isna(d): return "Sem Data"
            delta = (pd.to_datetime(d) - hoje).days
            if delta < 0: return "Atrasado"
            if delta == 0: return "Vence Hoje"
            return "No Prazo"
            
        df_view['Status_Prazo'] = df_view['promised_date'].apply(calc_status)

    if filtro_status and 'Status_Prazo' in df_view.columns:
        df_view = df_view[df_view['Status_Prazo'].isin(filtro_status)]

    if date_range and len(date_range) == 2 and 'promised_date' in df_view.columns:
        df_view = df_view[
            (pd.to_datetime(df_view['promised_date']).dt.date >= date_range[0]) & 
            (pd.to_datetime(df_view['promised_date']).dt.date <= date_range[1])
        ]

    st.markdown("---")

    # --- 2. KPI Cards (Health Check) ---
    total_view = len(df_view)
    if total_view > 0:
        atrasados = len(df_view[df_view['Status_Prazo'] == 'Atrasado']) if 'Status_Prazo' in df_view.columns else 0
        taxa_atraso = (atrasados / total_view) * 100
        
        kriticos_abs = len(df_view[df_view['Status_Prazo'].isin(['Atrasado', 'Vence Hoje'])]) if 'Status_Prazo' in df_view.columns else 0

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Volume Selecionado", total_view, border=True)
        k2.metric("Backlog Crítico", kriticos_abs, delta="Atenção Imediata", delta_color="inverse", border=True)
        k3.metric("Taxa de Atraso", f"{taxa_atraso:.1f}%", border=True)
        
        # Eficiência (Inverso do Atraso)
        k4.metric("Eficiência de Prazo", f"{100-taxa_atraso:.1f}%", border=True)

    # --- 3. Gráficos Estratégicos ---
    g1, g2 = st.columns([1, 1])

    # Gráfico 1: Pareto de Atrasos (Top 10 Agências)
    with g1:
        st.subheader(":material/bar_chart: Top 10 Gargalos (Pareto)")
        if 'Status_Prazo' in df_view.columns and not df_view.empty:
            df_atraso = df_view[df_view['Status_Prazo'] == 'Atrasado']
            if not df_atraso.empty:
                pareto = df_atraso['agência_destino_anotacao'].value_counts().reset_index()
                pareto.columns = ['Agência', 'Volume Atrasado']
                pareto = pareto.head(10)
                
                fig_pareto = px.bar(
                    pareto, 
                    x='Volume Atrasado', 
                    y='Agência', 
                    orientation='h',
                    text='Volume Atrasado',
                    color='Volume Atrasado',
                    color_continuous_scale='Reds'
                )
                fig_pareto.update_layout(yaxis=dict(autorange="reversed")) # Top 1 em cima
                st.plotly_chart(fig_pareto, use_container_width=True)
            else:
                st.success("Nenhum atraso registrado na seleção atual! 🏆")
        else:
            st.info("Sem dados de status para gerar Pareto.")

    # Gráfico 2: Curva de Vencimento (Temporal)
    with g2:
        st.subheader(":material/show_chart: Curva de Vencimento")
        if 'promised_date' in df_view.columns and not df_view.empty:
            df_view['Data Vencimento'] = pd.to_datetime(df_view['promised_date']).dt.date
            curve = df_view.groupby(['Data Vencimento', 'Status_Prazo']).size().reset_index(name='Volume')
            
            fig_curve = px.area(
                curve, 
                x='Data Vencimento', 
                y='Volume', 
                color='Status_Prazo',
                color_discrete_map={
                    "Atrasado": "#FF4B4B", 
                    "Vence Hoje": "#FFA421", 
                    "No Prazo": "#09AB3B"
                }
            )
            st.plotly_chart(fig_curve, use_container_width=True)
        else:
            st.info("Sem datas para gerar curva.")

    st.markdown("---")
    
    # --- 4. Tabela Detalhada (Legado Melhorado) ---
    st.subheader(":material/table: Base de Dados Detalhada")
    
    # Seleção de Colunas Inteligente
    cols_padrao = ['package_id', 'seal', 'agência_destino_anotacao', 'promised_date', 'Status_Prazo', 'Categoria']
    cols_existentes = [c for c in cols_padrao if c in df_view.columns]
    
    st.dataframe(
        df_view[cols_existentes],
        use_container_width=True,
        hide_index=True,
        column_config={
            "package_id": "Pacote",
            "seal": "Lacre",
            "agência_destino_anotacao": "Agência",
            "promised_date": st.column_config.DateColumn("Promessa", format="DD/MM/YYYY"),
            "Status_Prazo": st.column_config.TextColumn("Status"),
        }
    )

def render_sla_expedicao(df):
    st.title("Gestão de SLA e Expedição", anchor=False)
    
    # Explicação Visual da Fórmula
    with st.expander("Entenda o Cálculo do SLO (Expedição)", expanded=True, icon=":material/info:"):
        st.markdown("O sistema calcula a data limite para o lacre sair da origem (SLO) usando a seguinte lógica:")
        st.latex(r'''
        \text{Data Limite Expedição} = \text{Data Promessa} - \text{Buffer (1 Dia)} - \text{Tempo Trânsito} - \text{Tempo Agência}
        ''')
        st.caption("• **Buffer**: Margem de segurança de 1 dia para entrega final.\n• **Tempo Trânsito**: Viagem entre origem e destino.\n• **Tempo Agência**: Processamento interno na ponta.")

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
        if "Atenção" in series.values:
             return "Atenção"
        if "Expedir Hoje" in series.values:
            return "Expedir Hoje"
        return "No Prazo"

    # Função Helper para Recomendação
    def get_recommendation(status):
        if status == "Crítico":
            return "EXPEDIR IMEDIATAMENTE! Risco de Atraso."
        elif status == "Expedir Hoje":
            return "Priorizar saída no veículo de hoje."
        elif status == "Atenção":
            return "Planejar veículo para amanhã."
        else:
            return "Seguir fluxo normal."

    if 'seal' in df_sla.columns:
        df_view = df_sla.groupby('seal').agg({
            'agência_destino_anotacao': 'first',
            'Data_Limite_Expedicao': 'min',
            'package_id': 'count',
            'Status_Expedicao': get_seal_urgency
        }).reset_index()
        
        df_view.rename(columns={'package_id': 'Qtd Pacotes', 'Data_Limite_Expedicao': 'Expedir Até'}, inplace=True)
        
        df_view.rename(columns={'package_id': 'Qtd Pacotes', 'Data_Limite_Expedicao': 'Expedir Até'}, inplace=True)
        
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
                    st.dataframe(
                        pacotes_seal[['barcode', 'promised_date', 'Status', 'nfe_key', 'company_name']],
                        use_container_width=True,
                        column_config={
                            "barcode": st.column_config.TextColumn("Pacote / Barcode"),
                            "promised_date": st.column_config.DateColumn("Vence Em", format="DD/MM/YYYY"),
                            "Status": st.column_config.TextColumn("Status Entrega"),
                            "nfe_key": st.column_config.TextColumn("Chave NFe"),
                            "company_name": st.column_config.TextColumn("Embarcador")
                        },
                        hide_index=True
                    )
                    
                    if st.button("Fechar Detalhes"):
                        st.rerun()
        
    else:
        st.error("⚠️ Coluna 'seal' não encontrada. Verifique se o arquivo contém dados de lacres.")

if __name__ == "__main__":
    main()