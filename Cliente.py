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

#Adiciona flag de rajada
rajada = False
if len(pacotes) > 1:
    rajada = True
    
#Envia especificações para o servidor
dados_para_servidor = f"{modo_operacao},{rajada}"
soquete_cliente.sendall(dados_para_servidor.encode())

#Obtém a resposta do servidor
resposta_servidor = soquete_cliente.recv(512)
print(f"Resposta do servidor: {resposta_servidor.decode()}")

for pacote in pacotes:
    #transforma o pacote em json string para enviar
    pacote = json.dumps(pacote)

    print(pacote.encode())

    #Envia a requisição para o servidor
    soquete_cliente.sendall(pacote.encode())

    #Recebe resposta do seridor para cada pacote enviado no modo repetição seletiva
    if modo_operacao == 'repeticao seletiva':
        resposta = soquete_cliente.recv(512).decode()
        print("Resposta do servidor: ", resposta)

#Recebe uma única resposta do seridor no modo go back n
if modo_operacao == 'go-back-n':
    resposta = soquete_cliente.recv(512).decode()
    print("Resposta do servidor: ", resposta)

#Fecha a conexão com o servidor
soquete_cliente.close()