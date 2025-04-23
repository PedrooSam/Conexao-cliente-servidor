import socket


# ==================== SERVIDOR ==================== #

#Configura servidor e coloca no ar
soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete_servidor.bind(('localhost', 1024))
soquete_servidor.listen(5)
print("Servidor local rodando na porta 1024")

#Aceita conexão com cliente
cliente, endereco = soquete_servidor.accept()
print(f"Conexão estabelecida com {endereco}")

#Recebe configurações iniciais do cliente
dados_cliente = cliente.recv(1024).decode()
modo_operacao, rajada = dados_cliente.split(',')
print(f"Modo de operação recebido: {modo_operacao}")
print(f"Rajada: {rajada}")
print("\n")

#Envia confirmação das configurações para o cliente
cliente.send(b"Configuracoes recebidas com sucesso!\n")

pacotes_recebidos = []

while True:

    #Recebe os pacotes do cliente
    pacote = cliente.recv(1024).decode()
    print("Pacote recebido: ", pacote)

    pacotes_recebidos.append(pacote)

    #Envia um ACK para cada pacote caso seja repetição seletiva
    if modo_operacao == 'repeticao seletiva':
        resposta = "ACK"
        cliente.sendall(resposta.encode())

    #Break caso chegue no fim da mensagem
    if pacote == '$$$':
        break


#Junta os pacotes recebidos em uma mensagem
mensagem = "".join(pacotes_recebidos)
print(mensagem)

#Envia apenas um ACK para o cliente caso seja go back n
if modo_operacao == "go-back-n":
    resposta = "ACK"
    cliente.sendall(resposta.encode())

# Fecha a conexão com o cliente
cliente.close()