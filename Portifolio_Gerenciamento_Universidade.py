# Bibliotecas para manipulação de datas e horários, ocultação de senha, JSON, comandos do sistema operacional, e atrasos.
import datetime
import getpass
import json
import os
import time
import sys

# Dados dos eventos e inscrições
evento = {}
inscricoes = {}

# Senha do Coordenador
coordenador_senha = "123456"

# Verifica o sistema operacional e importa bibliotecas específicas
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix-like (Linux, macOS)
    import termios
    import tty

# Função para limpar a tela
def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para validar data no formato dd/mm/yyyy
def validar_data(data_str):
    """Valida a data no formato dd/mm/yyyy."""
    try:
        datetime.datetime.strptime(data_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

# Função para obter a senha, ocultando os caracteres reais com asteriscos
def obter_senha():
    """Solicita ao usuário para inserir uma senha e exibe asteriscos."""
    senha = ""
    print("Digite a senha: ", end="", flush=True)
    while True:
        if os.name == 'nt':  # Windows
            ch = msvcrt.getch().decode('utf-8')
        else:  # Unix-like (Linux, macOS)
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if ch in ('\n', '\r'):
            break
        if ch in ('\b', '\x7f'):
            senha = senha[:-1]
            sys.stdout.write('\b \b')
        else:
            senha += ch
            sys.stdout.write('*')
            sys.stdout.flush()
    print()
    return senha

# Função para autenticar o coordenador
def autenticar_coordenador():
    """Autentica o coordenador usando a senha."""
    print("Digite a senha do coordenador (ou pressione Enter para voltar ao menu principal):")
    senha = obter_senha().strip()
    if not senha:
        print("Voltando ao menu principal...\n")
        time.sleep(2)
        limpar_tela()
        return False
    elif senha == coordenador_senha:
        print("Bem-vindo ao menu coordenador!\n")
        time.sleep(2)
        limpar_tela()
        return True
    else:
        print("Senha incorreta! Tente novamente.\n")
        time.sleep(2)
        limpar_tela()
        return False
    
# Função para salvar dados em um arquivo .txt
def salvar_dados():
    """Salva os dados dos eventos e inscrições em arquivos .txt."""
    try:
        with open("eventos.txt", "w") as arquivo_eventos:
            arquivo_eventos.write(json.dumps(evento, indent=4))
        with open("inscricoes.txt", "w") as arquivo_inscricoes:
            arquivo_inscricoes.write(json.dumps(inscricoes, indent=4))
        print("Dados salvos com sucesso!")
    except IOError as e:
        print(f"Falha ao salvar os dados: {e}")

# Função para carregar dados de um arquivo .txt
def carregar_dados():
    """Carrega os dados dos eventos e inscrições de arquivos .txt."""
    global evento, inscricoes
    try:
        with open("eventos.txt", "r") as arquivo_eventos:
            evento = json.loads(arquivo_eventos.read())
        with open("inscricoes.txt", "r") as arquivo_inscricoes:
            inscricoes = json.loads(arquivo_inscricoes.read())
        print("Dados carregados com sucesso!")
    except FileNotFoundError:
        evento = {}
        inscricoes = {}
    except json.JSONDecodeError:
        print("Não foi possível ler os dados do arquivo. O formato pode estar corrompido ou incorreto. Iniciando com novos dados.")
    except IOError as e:
        print(f"Falha ao carregar os dados: {e}")

# Função para cadastrar novos eventos
def cadastrar_evento():
    """Cadastra novos eventos."""
    while True:
        try:
            nome_evento = input("Digite o nome do Evento: ").strip().lower()
            while True:
                data_evento = input("Digite a data do Evento (dd/mm/yyyy): ").strip()
                if not validar_data(data_evento):
                    print("A data fornecida está no formato incorreto. Por favor, insira a data no formato dd/mm/yyyy.")
                else:
                    break
            descricao_evento = input("Digite a descrição do evento: ").strip()
            numero_participantes = int(input("Digite o número de participantes: ").strip())
            if numero_participantes <= 0:
                raise ValueError("O número de participantes deve ser um número positivo.")
            evento[nome_evento] = {
                "Nome Evento": nome_evento,
                "Data Evento": data_evento,
                "Descrição Evento": descricao_evento,
                "Numero Participantes": numero_participantes,
                "Inscritos": 0,
                "Status": "Ativo"
            }
            print(f"Evento '{nome_evento.title()}' cadastrado com sucesso! \n")
            salvar_dados()  # Salva os dados após cadastrar o evento
            time.sleep(2)  # Espera 2 segundos antes de limpar a tela
            limpar_tela()
        except ValueError as ve:
            print(f"Erro de Valor: {ve}. Por favor, insira um valor válido.")
        except Exception as e:
            print(f"Erro Inesperado: {e}. Algo deu errado, por favor tente novamente.")
        
        continuar = input("Gostaria de cadastrar outro evento? (s/n): ").strip().lower()
        if continuar == 'n':
            break

# Função para atualizar eventos existentes
def atualizar_eventos():
    """Atualiza eventos existentes."""
    if not evento:
        print("Sem eventos disponíveis para atualização.")
    else:
        exibir_evento()
        # Obter o índice válido do evento a ser atualizado
        indice_evento = obter_indice_valido("Digite o número do evento que deseja atualizar: ")
        nome_evento = obter_evento_por_indice(indice_evento)
        if nome_evento:
            # Loop para garantir que a data seja inserida corretamente
            while True:
                data_evento = input("Digite nova data do Evento (dd/mm/yyyy): ").strip()
                if validar_data(data_evento):
                    break  # Sai do loop se a data for válida
                else:
                    print("A data fornecida está no formato incorreto. Por favor, insira a data no formato dd/mm/yyyy.")
            
            # Obter a nova descrição do evento
            descricao_evento = input("Digite a nova descrição do evento: ").strip()
            try:
                # Obter o novo número de participantes
                numero_participantes = int(input("Digite o novo número de participantes: ").strip())
                if numero_participantes <= 0:
                    print("O número de participantes deve ser um número positivo.")
                    return
            except ValueError:
                print("Por favor, insira um número válido para o número de participantes.")
                return
            
            # Perguntar ao usuário se ele deseja reativar o evento se ele estiver cancelado
            if evento[nome_evento]["Status"] == "Cancelado":
                reativar = input("Este evento está atualmente cancelado. Deseja reativá-lo? (s/n): ").strip().lower()
                if reativar == 's':
                    evento[nome_evento]["Status"] = "Ativo"
            
            # Atualizar os detalhes do evento
            evento[nome_evento]["Data Evento"] = data_evento
            evento[nome_evento]["Descrição Evento"] = descricao_evento
            evento[nome_evento]["Numero Participantes"] = numero_participantes
            print(f"Evento '{nome_evento.title()}' atualizado com sucesso! \n")
            salvar_dados()  # Salva os dados após atualizar o evento
        else:
            print("Evento não encontrado. Verifique o número do evento e tente novamente.")
        time.sleep(2)  # Espera 2 segundos antes de limpar a tela
        limpar_tela()

# Função para exibir os detalhes de um evento
def exibir_detalhes_evento(i, nome_evento, detalhes):
    """Exibe os detalhes de um evento."""
    vagas_restantes = detalhes["Numero Participantes"] - detalhes["Inscritos"]
    status = detalhes["Status"]
    print(f"{i}. Evento: {nome_evento.title()}\n"
          f" Data: {detalhes['Data Evento']}\n"
          f" Descrição: {detalhes['Descrição Evento']}\n"
          f" Participantes: {detalhes['Numero Participantes']}\n"
          f" Vagas Restantes: {vagas_restantes}\n"
          f" Status: {status}\n")

# Função para exibir todos os eventos cadastrados ou filtrados por status
def exibir_evento(filtro_status=None):
    """Exibe todos os eventos cadastrados ou filtrados por status."""
    eventos_filtrados = {nome: detalhes for nome, detalhes in evento.items() if filtro_status is None or detalhes["Status"] == filtro_status}
    if not eventos_filtrados:
        print("Sem Evento cadastrado" if filtro_status is None else f"Sem eventos com status '{filtro_status}'")
    else:
        print("Eventos Cadastrados:\n")  # Cabeçalho da lista de eventos
        for i, (nome_evento, detalhes) in enumerate(eventos_filtrados.items(), start=1):
            exibir_detalhes_evento(i, nome_evento, detalhes)
        print()  # Linha em branco para melhorar a legibilidade

# Função para exibir todos os eventos cadastrados
def exibir_evento():
    """Exibe todos os eventos cadastrados."""
    if not evento:
        print("Sem Evento cadastrado")  # Informa se não houver eventos cadastrados
    else:
        print("Eventos Cadastrados:\n")  # Cabeçalho da lista de eventos
        for i, (nome_evento, detalhes) in enumerate(evento.items(), start=1):
            exibir_detalhes_evento(i, nome_evento, detalhes)
        print()  # Linha em branco para melhorar a legibilidade

# Função para obter um índice válido do usuário
def obter_indice_valido(mensagem):
    """Obtém um índice válido do usuário."""
    while True:
        try:
            indice = int(input(mensagem).strip()) - 1
            if indice < 0 or indice >= len(evento):
                print("Índice fora dos limites válidos. Certifique-se de escolher um número listado acima.")
            else:
                return indice
        except ValueError:
            print("Por favor, insira um número válido.")

# Função para obter o nome do evento pelo índice
def obter_evento_por_indice(indice):
    """Obtém o nome do evento pelo índice."""
    try:
        if 0 <= indice < len(evento):
            return list(evento.keys())[indice]
        else:
            raise IndexError("O número fornecido não existe. Verifique um número disponível e tente novamente.")
    except IndexError as ie:
        print(f"Falha ao acessar evento: {ie}")
        return None

# Função para inscrever um aluno no evento
def inscrever_aluno():
    """Inscreve um aluno em um evento."""
    while True:
        exibir_evento()
        if evento:
            try:
                indice_evento = int(input("Digite o número do evento em que deseja se inscrever: ").strip()) - 1
                nome_evento = obter_evento_por_indice(indice_evento)
                if nome_evento and evento[nome_evento]["Status"] == "Ativo":
                    if evento[nome_evento]["Inscritos"] < evento[nome_evento]["Numero Participantes"]:
                        nome_aluno = input("Digite o nome do aluno: ").strip()
                        if nome_evento in inscricoes:
                            inscricoes[nome_evento].append(nome_aluno)
                        else:
                            inscricoes[nome_evento] = [nome_aluno]
                        evento[nome_evento]["Inscritos"] += 1
                        print(f"Aluno {nome_aluno} inscrito com sucesso no evento '{nome_evento.title()}'!\n")
                        salvar_dados()  # Salva os dados após a inscrição do aluno
                        time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                        limpar_tela()
                    else:
                        print("Não há vagas disponíveis para este evento.\n")
                        time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                        limpar_tela()
                else:
                    print("Evento não encontrado ou está cancelado. Verifique o número do evento e tente novamente.\n")
                    time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                    limpar_tela()
            except ValueError:
                print("Por favor, insira um número válido para o índice do evento.")
                time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                limpar_tela()
        continuar = input("Gostaria de se inscrever em outro evento? (s/n): ").strip().lower()
        if continuar == 'n':
            break

# Função para exibir inscritos em um evento e gerenciar inscrições
def exibir_inscritos():
    """Exibe os inscritos em um evento e permite o gerenciamento das inscrições."""
    exibir_evento()
    if evento:
        try:
            indice_evento = int(input("Digite o número do evento para visualizar os inscritos: ").strip()) - 1
            nome_evento = obter_evento_por_indice(indice_evento)
            if nome_evento:
                if nome_evento in inscricoes and inscricoes[nome_evento]:
                    print(f"Inscritos no evento {nome_evento.title()}:")
                    for nome_aluno in inscricoes[nome_evento]:
                        print(f"- {nome_aluno}")

                    # Opções para o coordenador gerenciar inscrições
                    while True:
                        opcao = input("Gostaria de (a) Adicionar um aluno, (b) Excluir um aluno, ou (c) Voltar ao menu? (a/b/c): ").strip().lower()
                        if opcao == 'a':
                            nome_novo_aluno = input("Digite o nome do aluno a ser adicionado: ").strip()
                            if evento[nome_evento]["Inscritos"] < evento[nome_evento]["Numero Participantes"]:
                                inscricoes[nome_evento].append(nome_novo_aluno)
                                evento[nome_evento]["Inscritos"] += 1
                                print(f"Aluno {nome_novo_aluno} adicionado com sucesso ao evento '{nome_evento.title()}'!\n")
                                salvar_dados()  # Salva os dados após adicionar um novo aluno
                                time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                                limpar_tela()
                            else:
                                print("Não há vagas disponíveis para este evento.\n")
                                time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                                limpar_tela()
                        elif opcao == 'b':
                            nome_aluno_excluir = input("Digite o nome do aluno a ser excluído: ").strip()
                            if nome_aluno_excluir in inscricoes[nome_evento]:
                                inscricoes[nome_evento].remove(nome_aluno_excluir)
                                evento[nome_evento]["Inscritos"] -= 1
                                print(f"Aluno {nome_aluno_excluir} excluído com sucesso do evento '{nome_evento.title()}'!\n")
                                salvar_dados()  # Salva os dados após excluir um aluno
                                time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                                limpar_tela()
                            else:
                                print("Aluno não encontrado na lista de inscritos.\n")
                                time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                                limpar_tela()
                        elif opcao == 'c':
                            break
                        else:
                            print("Opção inválida. Por favor, escolha 'a', 'b' ou 'c'.")
                            time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                            limpar_tela()
                else:
                    print(f"Sem inscritos no evento '{nome_evento.title()}'.\n")
                    time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                    limpar_tela()
            else:
                print("Evento não encontrado. Verifique o número do evento e tente novamente.\n")
                time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                limpar_tela()
        except ValueError:
            print("Por favor, insira um número válido para o índice do evento.")
            time.sleep(2)  # Espera 2 segundos antes de limpar a tela
            limpar_tela()
    else:
        print("Nenhum evento disponível no momento.")
        time.sleep(2)  # Espera 2 segundos antes de limpar a tela
        limpar_tela()

# Função para cancelar eventos existentes
def cancelar_eventos():
    """Cancela eventos existentes."""
    if not evento:
        print("Sem eventos disponíveis para cancelamento.")
        time.sleep(2)  # Espera 2 segundos antes de limpar a tela
        limpar_tela()
    else:
        exibir_evento()
        try:
            indice_evento = int(input("Digite o número do evento que deseja cancelar: ").strip()) - 1
            nome_evento = obter_evento_por_indice(indice_evento)
            if nome_evento:
                confirmacao = input(f"Tem certeza que deseja cancelar o evento '{nome_evento.title()}'? (s/n): ").strip().lower()
                if confirmacao == 's':
                    evento[nome_evento]["Status"] = "Cancelado"  # Altera o status para cancelado
                    print(f"Evento '{nome_evento.title()}' cancelado com sucesso! \n")
                    salvar_dados()  # Salva os dados após cancelar um evento
                    time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                    limpar_tela()
                else:
                    print(f"Cancelamento do evento '{nome_evento.title()}' foi abortado. \n")
                    time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                    limpar_tela()
            else:
                print("Evento não existe. Verifique o número do evento e tente novamente.\n")
                time.sleep(5)  # Espera 5 segundos antes de limpar a tela
                limpar_tela()
        except ValueError:
            print("Por favor, insira um número válido para o índice do evento.")
            time.sleep(5)  # Espera 5 segundos antes de limpar a tela
            limpar_tela()

# Função para excluir eventos existentes
def excluir_eventos():
    """Exclui eventos existentes."""
    eventos_cancelados = {nome: detalhes for nome, detalhes in evento.items() if detalhes["Status"] == "Cancelado"}
    if not eventos_cancelados:
        print("Sem eventos cancelados. Por favor cancele o evento para excluir.")
        time.sleep(5)  # Espera 5 segundos antes de limpar a tela
        limpar_tela()
        return  # Retorna imediatamente para evitar pedir confirmação duplicada
    else:
        # Exibe apenas eventos cancelados
        print("Eventos Cancelados:\n")
        for i, (nome_evento, detalhes) in enumerate(eventos_cancelados.items(), start=1):
            exibir_detalhes_evento(i, nome_evento, detalhes)
        print()  # Linha em branco para melhorar a legibilidade

        try:
            indice_evento = int(input("Digite o número do evento que deseja excluir: ").strip()) - 1
            nome_evento = list(eventos_cancelados.keys())[indice_evento]
            if nome_evento and "Status" in evento[nome_evento] and evento[nome_evento]["Status"] == "Cancelado":  # Verifica se o status é cancelado
                confirmacao = input(f"Tem certeza que deseja excluir o evento '{nome_evento.title()}'? (s/n): ").strip().lower()
                if confirmacao == 's':
                    del evento[nome_evento]
                    if nome_evento in inscricoes:
                        del inscricoes[nome_evento]
                    print(f"Evento '{nome_evento.title()}' excluído com sucesso! \n")
                    salvar_dados()  # Salva os dados após excluir um evento
                    time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                    limpar_tela()
                else:
                    print(f"Exclusão do evento '{nome_evento.title()}' foi cancelada. \n")
                    time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                    limpar_tela()
            else:
                print("Evento não está cancelado. Verifique o status do evento e tente novamente.\n")
                time.sleep(5)  # Espera 5 segundos antes de limpar a tela
                limpar_tela()
        except (ValueError, IndexError):
            print("Por favor, insira um número válido para o índice do evento.")
            time.sleep(5)  # Espera 5 segundos antes de limpar a tela
            limpar_tela()

# Loop principal do programa
def loop_principal():
    """Executa o loop principal do programa."""
    carregar_dados()
    while True:
        print("________Bem-vindo ao Gerenciador de Eventos UniFECAF________ \n")
        print("(1) Coordenador")
        print("(2) Aluno")
        print("(3) Sair \n")
        escolha_perfil = obter_escolha_perfil()
        if escolha_perfil == 1:  # Menu para Coordenador
            if autenticar_coordenador():  # Autenticação bem-sucedida ou retorno ao menu principal
                menu_coordenador()
        elif escolha_perfil == 2:  # Menu para Aluno
            menu_aluno()
        elif escolha_perfil == 3:
            salvar_dados()
            print("Saindo do sistema. Até logo!\n")
            break

def obter_escolha_perfil():
    """Obtém a escolha do perfil do usuário."""
    while True:
        try:
            escolha_perfil = int(input("Escolha uma das opções: ").strip())
            if escolha_perfil in [1, 2, 3]:
                return escolha_perfil
            else:
                print("Por favor, insira 1 para Coordenador, 2 para Aluno ou 3 para Sair.")
        except ValueError:
            print("Por favor, insira um número válido.")

# Função para exibir o menu do aluno
def exibir_menu_aluno():
    """Exibe o menu de opções para o aluno."""
    print("________Gerenciar Eventos Universitarios - Aluno________ \n")
    print("(1) Visualizar Eventos")
    print("(2) Inscrever no Evento")
    print("(3) Voltar ao Menu Principal \n")

# Função para exibir o menu do coordenador
def exibir_menu_coordenador():
    """Exibe o menu de opções para o coordenador."""
    print("________Gerenciar Eventos Universitarios - Coordenador________ \n")
    print("(1) Criar Novo Evento")
    print("(2) Atualizar Eventos")
    print("(3) Visualizar Eventos")
    print("(4) Visualizar Inscritos")
    print("(5) Cancelar Evento")
    print("(6) Excluir Eventos Cancelados")
    print("(7) Voltar ao Menu Principal \n")

# Função para gerenciar o menu do aluno
def menu_aluno():
    """Gerencia as opções do menu do aluno."""
    while True:
        exibir_menu_aluno()
        try:
            escolha_opcao = int(input("Qual opção você deseja? ").strip())
            if escolha_opcao == 1:
                exibir_evento()
            elif escolha_opcao == 2:
                inscrever_aluno()
            elif escolha_opcao == 3:
                break
            else:
                print("Por favor, escolha uma opção válida.")
        except ValueError:
            print("Por favor, insira um número válido.")
        input("Pressione ENTER para voltar ao menu do aluno...")
        limpar_tela()

# Função para gerenciar o menu do coordenador
def menu_coordenador():
    """Gerencia as opções do menu do coordenador."""
    while True:
        exibir_menu_coordenador()
        try:
            escolha_opcao = int(input("Qual opção você deseja? ").strip())
            if escolha_opcao == 1:
                cadastrar_evento()
            elif escolha_opcao == 2:
                atualizar_eventos()
            elif escolha_opcao == 3:
                exibir_evento()
            elif escolha_opcao == 4:
                exibir_inscritos()
            elif escolha_opcao == 5:
                cancelar_eventos()
            elif escolha_opcao == 6:
                excluir_eventos()
            elif escolha_opcao == 7:
                break
            else:
                print("Por favor, escolha uma opção válida.")
        except ValueError:
            print("Por favor, insira um número válido.")
        input("Pressione ENTER para voltar ao menu dos coordenadores...")
        limpar_tela()

# Ponto de entrada do programa
if __name__ == "__main__":
    loop_principal()
