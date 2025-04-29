import socket
from Client_lib import calcular_checksum
import json

# ==================== SERVIDOR ==================== #

#Configura servidor e coloca no ar
soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete_servidor.bind(('localhost', 1024))
soquete_servidor.listen(5)
print("Servidor local rodando na porta 1024")

#Criação inicial da janela
janela = {}
janela['inicio'] = 0
janela['final'] = 4

#Aceita conexão com cliente
cliente, endereco = soquete_servidor.accept()
print(f"Conexão estabelecida com {endereco}")

#Recebe configurações iniciais do cliente
modo_operacao = cliente.recv(1024).decode()

print(f"Modo de operação recebido: {modo_operacao}\n")

#Envia confirmação das configurações para o cliente
cliente.send(b"Configuracoes recebidas com sucesso!\n")
cliente.send((str(janela)).encode())

pacotes_recebidos = []
pacotes_rejeitados = []
num_sequencia_anterior = -1

while True:
    #Recebe o pacote do cliente
    pacote = cliente.recv(1024).decode()

    print("\nPacote recebido: ", pacote)
    print("Janela: ", janela)

    # Transforma o pacote recebido em um dicionário
    pacote = json.loads(pacote)

    #Calcula intervalo da janela
    intervalo_janela = range(janela["inicio"], janela['final'])

    try:
        num_sequencia, dados, checksum_recebido = pacote["num_sequencia"], pacote["dados"], pacote["checksum"]
        num_sequencia = int(num_sequencia)
        checksum_calculado = calcular_checksum(dados)
    except ValueError:
        print("Formato inválido de pacote.")
        continue

    #Break caso seja o fim da mensagem
    if dados == '$$$':
        break

    #Verifica se o pacote está no limite da janela
    if num_sequencia not in intervalo_janela:
        retorno = "Pacote fora do intervalo da janela"
        print(retorno)

        #incrementa as informações da janela e retorna para o cliente
        janela['inicio'] += 1
        janela["final"] += 1
        retorno_janela = (str(janela)) + '\n'

        #Retorna o erro caso seja repetição seletiva
        if modo_operacao == 'repeticao seletiva':
            cliente.send(retorno.encode())
            cliente.send(retorno_janela.encode())

        #Ignora o pacote fora do limite
        continue

    #Verifica se o checksum bate
    if checksum_calculado != int(checksum_recebido):
        print("Pacote corrompido! Ignorado.")
        continue

    # Verifica se o pacote está fora de ordem
    if num_sequencia != num_sequencia_anterior + 1:
        print("Pacote fora de ordem!")
        continue
    
    # Verifica se o pacote é duplicado
    if(num_sequencia == num_sequencia_anterior):
        print("Pacote duplicado!")
        continue

    else:
        print("Nada de errado com o pacote!")
        pacotes_recebidos.append(dados)
        
    #Envia ACK se for modo de repetição seletiva
    if modo_operacao == 'repeticao seletiva':
        cliente.sendall(b"ACK" + str(num_sequencia).encode())

        #incrementa as informações da janela e retorna para o cliente
        janela['inicio'] += 1
        janela["final"] += 1
        cliente.send((str(janela)).encode())

    num_sequencia_anterior = num_sequencia


#Junta os pacotes válidos recebidos
mensagem = "".join(pacotes_recebidos)
print("Mensagem final reconstruída:", mensagem)

#Envia um ACK (final para repetição seletiva ou único se for go-back-n)
if modo_operacao == 'go-back-n':
    cliente.sendall(b"ACK" + str(num_sequencia_anterior).encode())
    
    #incrementa as informações da janela e retorna para o cliente
    janela['inicio'] += 1
    janela["final"] += 1
    cliente.send((str(janela)).encode())

# Fecha a conexão com o cliente
cliente.close()