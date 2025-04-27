import socket
from Client_lib import calcular_checksum
import json

# ==================== SERVIDOR ==================== #

# Configura servidor e coloca no ar
soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete_servidor.bind(('localhost', 1024))
soquete_servidor.listen(5)
print("Servidor local rodando na porta 1024")

# Aceita conexão com cliente
cliente, endereco = soquete_servidor.accept()
print(f"Conexão estabelecida com {endereco}")

# Recebe configurações iniciais do cliente
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

# Envia confirmação das configurações para o cliente
cliente.send(b"Configuracoes recebidas com sucesso!\n")

# Inicializa variáveis
pacotes_recebidos = {}
esperado = 0

while True:
    try:
        # Recebe o pacote do cliente
        pacote = cliente.recv(1024).decode()
    except:
        break

    if not pacote:
        break

    print("Pacote recebido:", pacote)

    # Transforma o pacote recebido em um dicionário
    try:
        pacote = json.loads(pacote)
    except json.JSONDecodeError:
        print("Erro ao decodificar pacote JSON!")
        continue

    # Verifica se é o fim da mensagem
    if pacote["dados"] == "$$$":
        break

    try:
        num_sequencia = int(pacote["num_sequencia"])
        dados = pacote["dados"]
        checksum_recebido = int(pacote["checksum"])
        checksum_calculado = calcular_checksum(dados)
    except ValueError:
        print("Formato inválido de pacote.")
        continue

    # Verifica se o checksum bate
    if checksum_recebido != checksum_calculado:
        print("Erro de checksum!")
        cliente.sendall(b"ERRO")
        continue

    # Se estiver no modo Go-Back-N, verifica a ordem dos pacotes
    if modo_operacao == 'go-back-n':
        if num_sequencia == esperado:
            pacotes_recebidos[num_sequencia] = dados
            esperado += 1
            cliente.sendall(b"ACK")
        else:
            print("Pacote fora de ordem! Esperado:", esperado)
            cliente.sendall(b"ERRO")
    # Se estiver no modo Repetição Seletiva, armazena pacotes fora de ordem
    elif modo_operacao == 'repeticao seletiva':
        pacotes_recebidos[num_sequencia] = dados
        cliente.sendall(b"ACK")

# Junta os pacotes válidos recebidos
mensagem_final = "".join([pacotes_recebidos[i] for i in sorted(pacotes_recebidos)])
print("Mensagem final reconstruída:", mensagem_final)

# Fecha a conexão com o cliente
cliente.close()
