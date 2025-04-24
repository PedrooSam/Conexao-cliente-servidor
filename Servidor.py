import socket

def calcular_checksum(pacote):
    return sum(pacote.encode()) % 256

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
    #Recebe o pacote do cliente
    pacote = cliente.recv(1024).decode()
    print("Pacote recebido: ", pacote)

    #Verifica se é o fim da mensagem
    if pacote == '$$$':
        break

    #Tenta separar os dados e o checksum
    try:
        dados, checksum_recebido = pacote.split(":")
        checksum_calculado = calcular_checksum(dados)
    except ValueError:
        print("Formato inválido de pacote.")
        continue

    #Verifica se o checksum bate
    if checksum_calculado != int(checksum_recebido):
        print("Pacote corrompido! Ignorado.")
        continue
    else:
        print("Nada de errado com o pacote!")
        pacotes_recebidos.append(dados)

    #Envia ACK se for modo de repetição seletiva
    if modo_operacao == 'repeticao seletiva':
        cliente.sendall(b"ACK")

#Junta os pacotes válidos recebidos
mensagem = "".join(pacotes_recebidos)
print("Mensagem final reconstruída:", mensagem)

#Envia um ACK final se for go-back-n
if modo_operacao == "go-back-n":
    cliente.sendall(b"ACK")

# Fecha a conexão com o cliente
cliente.close()
