import socket
import time
import Client_lib
import json
            

# ==================== CLIENTE ==================== #

#Criando conexão com servidor
soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
endereco_servidor = ("localhost", 1024)
soquete_cliente.connect(endereco_servidor)

while True:
    #Solicita informações do cliente
    modo_operacao = Client_lib.soliticar_modoOperacao()

    print()
    tamanho_mensagem = int(input("Digite o tamanho da mensagem do pacote: "))

    if modo_operacao == 'close':
        dados_para_servidor = f"{modo_operacao}"
        soquete_cliente.sendall(dados_para_servidor.encode())
        break
    
    while True:
        print()
        print("Escolha uma opção:")
        print("1. Enviar pacotes sem erros")
        print("2. Simular erro de integridade")
        print("3. Manipular número de sequência")
        print("4. Forçar erro no ACK retornado")
        print("5. Enviar pacote que deve ser perdido")
        print("6. Enviar pacote com atraso proposital e sem ACK (testar timeout)")
        opcao = int(input("Digite o número da opção: "))

        if opcao in range (1, 7):
            break
        else:
            print('Opção invalida!')


    mensagem = Client_lib.solicitar_mensagem()

    #Divide a mensagem em pacotes e adiciona flag de rajada
    pacotes = Client_lib.dividir_pacotes(mensagem, tamanho_mensagem)

    pacotes = Client_lib.simularErro(pacotes, opcao)

    #Envia especificações para o servidor
    dados_para_servidor = f"{modo_operacao}"
    soquete_cliente.sendall(dados_para_servidor.encode())

    Client_lib.limpar_buffer(soquete_cliente)

    janela = Client_lib.receberRespostaServidor(soquete_cliente)

    #Percorre todos os pacotes da mensagem
    for pacote in pacotes:
        fim_mensagem = pacote['dados']

        #transforma o pacote em json string para enviar
        pacote_json = json.dumps(pacote)

        #Envia a requisição para o servidor
        soquete_cliente.send(pacote_json.encode())

        #Recebe resposta do seridor para cada pacote enviado no modo repetição seletiva
        if modo_operacao == 'repeticao seletiva':
            pacoteServidor = Client_lib.receberPacoteServidor(soquete_cliente, opcao)

            if pacoteServidor == "break":
                break
        
        if 'flag' in pacote and pacote['flag'] == '$$$':
            break

    #Recebe uma única resposta do seridor no modo go back n
    if modo_operacao == 'go-back-n':
        pacoteServidor = Client_lib.receberPacoteServidor(soquete_cliente, opcao)

#Fecha a conexão com o servidor
soquete_cliente.close()