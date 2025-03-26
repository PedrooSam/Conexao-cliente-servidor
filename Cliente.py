import socket

soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

endereco_servidor = ("localhost", 80)
soquete_cliente.connect(endereco_servidor)

requisicao = "GET / HTTP/1.0\r\nHost: localhost\r\n\r\n"
soquete_cliente.sendall(requisicao.encode())

while True: 
    dados = soquete_cliente.recv(512)
    
    if len(dados) < 1:
        break

    print(dados.decode(), end="")

soquete_cliente.close()