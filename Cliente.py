import socket
from time import sleep
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
    pacotes = Client_lib.dividir_pacotes(mensagem)

    pacotes = Client_lib.simularErro(pacotes, opcao)

    #Envia especificações para o servidor
    dados_para_servidor = f"{modo_operacao}"
    soquete_cliente.sendall(dados_para_servidor.encode())

    resposta = Client_lib.receberRespostaServidor(soquete_cliente)
    janela = Client_lib.receberRespostaServidor(soquete_cliente)

    #Percorre todos os pacotes da mensagem
    for pacote in pacotes:

        print()
        fim_mensagem = pacote['dados']

        #transforma o pacote em json string para enviar
        pacote = json.dumps(pacote)

        #Envia a requisição para o servidor
        soquete_cliente.sendall(pacote.encode())

        #Caso seja o fim da string, quebra o loop
        if fim_mensagem == '$$$':
            break

        #Recebe resposta do seridor para cada pacote enviado no modo repetição seletiva
        if modo_operacao == 'repeticao seletiva':
            if opcao == 6:
                soquete_cliente.settimeout(0.001)
            

            try:
                resposta = Client_lib.receberRespostaServidor(soquete_cliente)
                print('Resposta: ', resposta)

                janela = json.loads(Client_lib.receberRespostaServidor(soquete_cliente))

                inicio = janela["inicio"]
                final = janela["final"]

                print(f"Janela: ({inicio}, {final})")
            except socket.timeout:
                print("Tempo de espera excedido!")
                break
            
        if modo_operacao == 'go-back-n':
            sleep(0.2)


    #Recebe uma única resposta do seridor no modo go back n
    if modo_operacao == 'go-back-n':
        if opcao == 6:
            soquete_cliente.settimeout(0.001)

        try:
            resposta = Client_lib.receberRespostaServidor(soquete_cliente)
            print('Resposta: ', resposta)

            janela = json.loads(Client_lib.receberRespostaServidor(soquete_cliente))

            inicio = janela["inicio"]
            final = janela["final"]

            print(f"Janela: ({inicio}, {final})")
        except socket.timeout:
            print("Tempo de espera excedido!")
            break

#Fecha a conexão com o servidor
soquete_cliente.close()