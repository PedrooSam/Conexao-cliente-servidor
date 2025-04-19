import socket
import Client_lib
            

# ==================== MAIN ==================== #

#Criando conexão com servidor
soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
endereco_servidor = ("localhost", 1024)
soquete_cliente.connect(endereco_servidor)

#Solicita informações do cliente
modo_operacao = Client_lib.soliticar_modoOperacao()
mensagem = Client_lib.solicitar_Tamanho()

#Divide a mensagem em pacotes
pacotes = Client_lib.dividir_pacotes(mensagem)
rajada = False
if len(pacotes > 1):
    rajada = True

for pacote in pacotes:
    
    #Envia mensagem
    dados_para_servidor = f"{modo_operacao},{rajada}"
    soquete_cliente.sendall(dados_para_servidor.encode())

    resposta_servidor = soquete_cliente.recv(512)
    print(f"Resposta do servidor: {resposta_servidor.decode()}")

    requisicao = "GET / HTTP/1.0\r\nHost: localhost\r\n\r\n"
    soquete_cliente.sendall(requisicao.encode())

    while True:
        dados = soquete_cliente.recv(512)
        
        if len(dados) < 1:
            break

        print(dados.decode(), end="")

soquete_cliente.close()