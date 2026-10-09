import os
import glob


def listar_relatorios():
    """Gera uma lista com todos os relatórios do GuardAI salvos na pasta atual."""
    arquivos = glob.glob("relatorio_guardai_*.md")
    arquivos.sort(reverse=True)
    return arquivos


def ler_relatorio(nome_arquivo):
    """Lê e retorna o conteúdo textual de um relatório específico."""
    if not os.path.exists(nome_arquivo):
        return f"[-] Erro: O arquivo {nome_arquivo} não existe."

    try:
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except Exception as e:
        return f"[-] Erro ao ler o arquivo: {e}"


def excluir_relatorio(nome_arquivo):
    """Remove fisicamente o arquivo do relatório do disco rígido."""
    if os.path.exists(nome_arquivo):
        try:
            os.remove(nome_arquivo)
            print(f"[+] Arquivo {nome_arquivo} excluído com sucesso!")
            return True
        except Exception as e:
            print(f"[-] Erro ao excluir o arquivo: {e}")
            return False
    return False


# --- BLOCO DE INTERAÇÃO VIA TERMINAL ---
if __name__ == "__main__":
    print("==================================================")
    print("        GERENCIADOR DE HISTÓRICO GUARDAI          ")
    print("==================================================")

    relatorios = listar_relatorios()

    if not relatorios:
        print("[!] Nenhum relatório encontrado na pasta do projeto.")
    else:
        print(f"[+] Foram encontrados {len(relatorios)} relatório(s) de segurança:")
        for idx, arquivo in enumerate(relatorios, 1):
            print(f"  [{idx}] {arquivo}")

        print("\n--------------------------------------------------")
        try:
            escolha = int(input("Digite o número do relatório que deseja gerenciar (ou 0 para sair): ").strip())

            if escolha > 0 and escolha <= len(relatorios):
                arquivo_selecionado = relatorios[escolha - 1]

                print(f"\n[?] O que deseja fazer com {arquivo_selecionado}?")
                print("  [1] Ler Relatório")
                print("  [2] Apagar/Excluir Relatório")
                acao = int(input("Escolha a ação (1 ou 2): ").strip())

                if acao == 1:
                    print(f"\n[+] Abrindo: {arquivo_selecionado}")
                    print("=" * 60)
                    print(ler_relatorio(arquivo_selecionado))
                    print("=" * 60)
                elif acao == 2:
                    confirmar = input(
                        f"[!] Tem certeza que deseja deletar {arquivo_selecionado}? (s/n): ").strip().lower()
                    if confirmar == 's':
                        excluir_relatorio(arquivo_selecionado)
                    else:
                        print("[*] Operação cancelada.")
                else:
                    print("[-] Opção de ação inválida.")

            elif escolha == 0:
                print("[*] Encerrando gerenciador de histórico.")
            else:
                print("[-] Opção inválida.")
        except ValueError:
            print("[-] Erro: Por favor, digite um número válido.")

