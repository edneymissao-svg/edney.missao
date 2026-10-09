import streamlit as st
import guardai_recon as recon
import guardai_historico as hist
import os
import time

# Configuração inicial da página web (Deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Painel GuardAI - Cibersegurança",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Projeto GuardAI - Agente Autônomo de Segurança")
st.markdown("Bem-vindo ao painel operacional do seu agente de cibersegurança e análise de superfície de ataque.")

# --- CORREÇÃO AQUI: Criando as abas ANTES de usá-las ---
aba_escanear, aba_historico = st.tabs(["🚀 Executar Varredura", "📜 Histórico de Relatórios"])

# --- ABA 1: EXECUÇÃO DE VARREDURAS ---
with aba_escanear:
    st.header("Configuração do Alvo")

    # Campo de texto interativo para definir o alvo
    escolha_alvo = st.text_input(
        "Digite o IP ou Host de destino para varredura Nmap:",
        placeholder="Deixe em branco para realizar uma varredura local segura no seu Linux Mint"
    ).strip()

    if st.button("🔄 Iniciar Análise Automatizada", type="primary"):
        status_ufw = "Não aplicável (Alvo Externo)"

        if escolha_alvo:
            alvo = escolha_alvo
            comando_rede = ["nmap", "-F", alvo]
        else:
            alvo = "localhost (Máquina Local)"
            comando_rede = ["ss", "-tln"]

            # Executa a chamada do firewall integrada usando a lógica do backend
            with st.spinner("Consultando privilégios e status do UFW local..."):
                status_ufw = recon.checar_status_ufw()

        # Exibe mensagens de progresso na tela web
        st.info(f"[*] Iniciando reconhecimento em: **{alvo}**")

        with st.spinner("Coletando dados brutos do terminal e gerando relatório com a IA (Aguarde)..."):
            # 1. Executa a ferramenta de rede
            saida_bruta = recon.rodar_comando(comando_rede)

            if "Erro" in saida_bruta:
                st.error(saida_bruta)
            else:
                # 2. Envia para o cérebro da IA processar
                relatorio_final = recon.analisar_com_guardai(saida_bruta, alvo, status_ufw)

                # 3. Salva em arquivo físico .md
                arquivo_salvo = recon.salvar_relatorio(relatorio_final)

                st.success("✅ Relatório de Segurança Gerado com Sucesso!")

                # Exibe o relatório em Markdown formatado direto na página web
                st.markdown("### 📝 Relatório do Agente:")
                st.markdown(relatorio_final)

                if arquivo_salvo:
                    st.caption(f"💾 Cópia física salva localmente como: `{arquivo_salvo}`")

# --- ABA 2: GERENCIAMENTO E CONSULTA DE HISTÓRICO ---
with aba_historico:
    st.header("Relatórios Antigos Salvos")

    # Busca a lista de relatórios existentes usando o módulo de histórico
    lista_arquivos = hist.listar_relatorios()

    if not lista_arquivos:
        st.warning("Nenhum relatório histórico encontrado na pasta do projeto.")
    else:
        arquivo_selecionado = st.selectbox(
            "Selecione um relatório para visualização detalhada:",
            options=lista_arquivos
        )

        if os.path.exists(arquivo_selecionado):
            # Cria duas colunas para alinhar o título e o botão de exclusão
            col_titulo, col_botao = st.columns([4, 1])

            with col_titulo:
                st.markdown(f"#### 📖 Visualizando: `{arquivo_selecionado}`")

            with col_botao:
                # Botão vermelho para apagar arquivos inválidos
                if st.button("🗑️ Excluir este Relatório", type="secondary", help="Remove este arquivo permanentemente"):
                    hist.excluir_relatorio(arquivo_selecionado)
                    st.success(f"Arquivo `{arquivo_selecionado}` excluído!")
                    time.sleep(1)
                    st.rerun()  # Atualiza a página web para limpar a lista

            st.divider()
            conteudo = hist.ler_relatorio(arquivo_selecionado)
            st.markdown(conteudo)
