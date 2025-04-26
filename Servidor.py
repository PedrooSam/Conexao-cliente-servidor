import socket
from Client_lib import calcular_checksum
import json

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

try:
    modo_operacao, rajada = dados_cliente.split(',')
except ValueError:
    print("Erro ao processar dados iniciais.")
    cliente.close()
    exit()

print(f"Modo de operação recebido: {modo_operacao}")
print(f"Rajada: {rajada}")
print("\n")

#Envia confirmação das configurações para o cliente
cliente.send(b"Configuracoes recebidas com sucesso!\n")

pacotes_recebidos = []
num_sequencia_anterior = -1

while True:
    #Recebe o pacote do cliente
    pacote = cliente.recv(1024).decode()

    print("Pacote recebido:", pacote)

    # Transforma o pacote recebido em um dicionário
    pacote = json.loads(pacote)

    #Verifica se é o fim da mensagem
    if pacote["dados"] == '$$$':
        break
    
    try:
        num_sequencia, dados, checksum_recebido = pacote["num_sequencia"], pacote["dados"], pacote["checksum"]
        num_sequencia = int(num_sequencia)
        checksum_calculado = calcular_checksum(dados)
    except ValueError:
        print("Formato inválido de pacote.")
        continue

    #Verifica se o checksum bate
    if checksum_calculado != int(checksum_recebido):
        print("Pacote corrompido! Ignorado.")
        continue

    # Verifica se o pacote está fora de ordem
    if num_sequencia != num_sequencia_anterior + 1:
        print("Pacote fora de ordem!")
        if modo_operacao == 'go-back-n':
            print("Reenviando pacotes...")
            cliente.sendall(b"ACK")
            break
        else:
            print("Modo de operação: repetição seletiva. Pacote ignorado.")
            continue
    
    # Verifica se o pacote é duplicado
    if(num_sequencia == num_sequencia_anterior):
        print("Pacote duplicado!")
        if modo_operacao == 'go-back-n':
            print("Reenviando pacotes...")
            cliente.sendall(b"ACK")
            break
        else:
            print("Modo de operação: repetição seletiva. Pacote ignorado.")
            continue

    else:
        print("Nada de errado com o pacote!")
        pacotes_recebidos.append(dados)

    #Envia ACK se for modo de repetição seletiva
    if modo_operacao == 'repeticao seletiva':
        cliente.sendall(b"ACK")

    num_sequencia_anterior = num_sequencia

    cliente.sendall(b"")

#Junta os pacotes válidos recebidos
mensagem = "".join(pacotes_recebidos)
print("Mensagem final reconstruída:", mensagem)

#Envia um ACK final se for go-back-n
if modo_operacao == "go-back-n":
    cliente.sendall(b"ACK")

# Fecha a conexão com o cliente
cliente.close()
