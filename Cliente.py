import socket
from time import sleep
import Client_lib
import json
            

# ==================== CLIENTE ==================== #

#Criando conexão com servidor
soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
endereco_servidor = ("localhost", 1024)
soquete_cliente.connect(endereco_servidor)

#Solicita informações do cliente
modo_operacao = Client_lib.soliticar_modoOperacao()
mensagem = Client_lib.solicitar_mensagem()

#Divide a mensagem em pacotes e adiciona flag de rajada
pacotes = Client_lib.dividir_pacotes(mensagem)
    
#Envia especificações para o servidor
dados_para_servidor = f"{modo_operacao}"
soquete_cliente.sendall(dados_para_servidor.encode())

#Obtém as respostas do servidor
soquete_cliente.settimeout(5)  # Define um tempo limite de 5 segundos para a resposta do servidor

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
        resposta = Client_lib.receberRespostaServidor(soquete_cliente)
        print('Resposta: ', resposta)
        janela = json.dumps(Client_lib.receberRespostaServidor(soquete_cliente))
        print("Janela: ", janela)
        
    if modo_operacao == 'go-back-n':
        # Aguarda um tempo para simular o envio de pacotes
        sleep(0.1)


#Recebe uma única resposta do seridor no modo go back n
if modo_operacao == 'go-back-n':
    resposta = Client_lib.receberRespostaServidor(soquete_cliente)
    print('Resposta: ', resposta)
    janela = json.dumps(Client_lib.receberRespostaServidor(soquete_cliente))
    print("Janela: ", janela)

#Fecha a conexão com o servidor
soquete_cliente.close()