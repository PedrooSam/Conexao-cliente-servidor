import socket
from time import sleep
import Client_lib
            

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

    #Envia a requisição para o servidor
    soquete_cliente.sendall(pacote.encode())

    while True:
        dados = soquete_cliente.recv(512)
        
        if len(dados) < 1:
            break

        print(dados.decode(), end="")

#Fecha a conexão com o servidor
soquete_cliente.close()