import socket

def solicitarTamanho():
    while True:
        mensagem = input("Digite a mensagem (tem que ter no maximo 3 caracteres): ")
        if len(mensagem)<=3:
            return mensagem
        else:
            print("Tente novamente")

def modoOperacao():
    while True:
        selecao = int(input("Informe o modo de operação (go-back-n[1] ou repeticao seletiva[2]): "))
        if selecao == 1:
            return "go-back-n"
        elif selecao == 2:
            return "repeticao seletiva"
        else:
            print("Tente novamente")
            
soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

endereco_servidor = ("localhost", 1024)
soquete_cliente.connect(endereco_servidor)

modo_operacao = modoOperacao()
tamanho_mensagem = solicitarTamanho()

dados_para_servidor = f"{modo_operacao},{tamanho_mensagem}"
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