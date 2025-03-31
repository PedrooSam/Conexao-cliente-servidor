import socket

soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

soquete_servidor.bind(('localhost', 80))

soquete_servidor.listen(5)
print("Servidor local rodando na porta 80")

while True:
    cliente, endereco = soquete_servidor.accept()
    print(f"Conexão estabelecida com {endereco}")
    cliente.send(b"Bem-vindo ao servidor!\n")
    requisicao = cliente.recv(1024).decode()
    print("Requisição recebida:\n", requisicao)

    # Cria uma resposta HTTP
    resposta = """HTTP/1.0 200 OK
    Content-Type: text/plain
    Bem-vindo ao servidor!"""
    # Envia a resposta para o cliente
    cliente.sendall(resposta.encode())

    # Fecha a conexão com o cliente
    cliente.close()