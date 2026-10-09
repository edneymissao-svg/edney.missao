import subprocess
import os
import time
from datetime import datetime
from google import genai
from google.genai import types


def rodar_comando(comando):
    """Executa um comando no terminal do Linux e retorna a saída como string."""
    try:
        resultado = subprocess.run(
            comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return resultado.stdout
    except subprocess.CalledProcessError as e:
        return f"[-] Erro ao executar o comando: {e.stderr}"
    except FileNotFoundError:
        return f"[-] Erro: A ferramenta '{comando}' não está instalada no sistema."


def checar_status_ufw():
    """Verifica se o firewall UFW está ativo no sistema operacional."""
    print("[*] Verificando status do firewall local (UFW)...")
    status_bruto = rodar_comando(["sudo", "ufw", "status"])

    # Converte o texto para minúsculas para evitar problemas de localização (PT-BR vs EN)
    status_min = status_bruto.lower()

    if "status: active" in status_min or "status: ativo" in status_min or "estado: ativo" in status_min:
        return "ATIVO (O sistema local possui proteção de firewall ativa)."
    elif "status: inactive" in status_min or "status: inativo" in status_min or "estado: inativo" in status_min:
        return "INATIVO (Alerta: O sistema local está com as portas desprotegidas!)."
    else:
        return f"Não foi possível determinar o status do UFW. Detalhes: {status_bruto.strip()}"


def analisar_com_guardai(dados_do_terminal, alvo, status_ufw="Não aplicável (Alvo Externo)"):
    """Envia os dados capturados e o contexto de segurança para o cérebro da IA."""
    print("[*] Enviando dados para análise do cérebro GuardAI...")

    tentativas_maximas = 5  # Configuração expandida para maior resiliência
    tempo_espera = 5  # Tempo inicial para o backoff exponencial

    for tentativa in range(1, tentativas_maximas + 1):
        try:
            client = genai.Client()

            prompt_sistema = f"""
            Você é o GuardAI, um agente autônomo de inteligência artificial de elite, especializado em Cibersegurança.
            Seu objetivo é analisar saídas textuais brutas de comandos de rede e identificar vulnerabilidades para o alvo: {alvo}.

            CONTEXTO DE SEGURANÇA LOCAL:
            - Status do Firewall UFW do Sistema Operacional Host: {status_ufw}

            Seja analítico e preciso. Se o status do UFW for INATIVO em uma análise local, destaque isso como um risco crítico.
            Baseie suas conclusions estritamente nos dados de rede fornecidos.

            FORMATO OBRIGATÓRIO DE SAÍDA (MARKDOWN):
            ## 🔍 RESUMO DA SUPERFÍCIE DE ATAQUE
            * **Alvo Analisado:** {alvo}
            * **Status do Firewall do Host:** {status_ufw}
            * **Portas Abertas Identificadas:** [Lista de portas]
            * **Nível de Risco Geral:** [Baixo / Médio / Alto / Crítico]

            ## ⚠️ VULNERABILIDADES OU RISCOS ENCONTRADOS
            [Liste aqui os serviços suspeitos, portas que representam riscos ou problemas com o Firewall]

            ## 🛠️ PLANO DE MITIGAÇÃO RECOMENDADO
            [Forneça comandos de terminal Linux derivados do Ubuntu/Mint para fechar as portas ou ativar/configurar o UFW se necessário]
            """

            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=f"Aqui está a saída do comando do terminal para análise:\n\n{dados_do_terminal}",
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.2
                )
            )
            return response.text

        except Exception as e:
            if tentativa == tentativas_maximas:
                return f"[-] Erro definitivo após {tentativas_maximas} tentativas: {e}"

            print(
                f"[!] Servidor sob alta demanda (Tentativa {tentativa}/{tentativas_maximas}). Aguardando {tempo_espera} segundos...")
            time.sleep(tempo_espera)
            tempo_espera *= 2  # Dobra o tempo de espera para a próxima tentativa (Backoff Exponencial)


def salvar_relatorio(conteudo):
    """Salva o relatório gerado pela IA em um arquivo físico Markdown (.md)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_guardai_{timestamp}.md"

    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
        print(f"[+] Sucesso! Relatório salvo fisicamente em: {nome_arquivo}")
        return nome_arquivo
    except Exception as e:
        print(f"[-] Erro ao salvar o arquivo: {e}")
        return None


# --- BLOCO DE EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("==================================================")
    print("          INICIALIZANDO AGENTE GUARDAI            ")
    print("==================================================")

    escolha_alvo = input(
        "Digite o IP/Host alvo para varredura Nmap (ou aperte ENTER para varredura local segura): ").strip()

    status_ufw = "Não aplicável (Alvo Externo)"

    if escolha_alvo:
        alvo = escolha_alvo
        comando_rede = ["nmap", "-F", alvo]
    else:
        alvo = "localhost (Máquina Local)"
        comando_rede = ["ss", "-tln"]
        status_ufw = checar_status_ufw()

    print(f"[*] Iniciando reconhecimento em: {alvo}")
    saida_bruta = rodar_comando(comando_rede)

    if "Erro" in saida_bruta:
        print(saida_bruta)
    else:
        relatorio_final = analisar_com_guardai(saida_bruta, alvo, status_ufw)

        print("\n" + "=" * 50)
        print(relatorio_final)
        print("=" * 50)

        salvar_relatorio(relatorio_final)
