import socket
from Client_lib import calcular_checksum, enviarRespostaNegativaServidor, enviarRespostaFinalServidor
import json
import time

# ==================== SERVIDOR ==================== #

#Configura servidor e coloca no ar
soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete_servidor.bind(('localhost', 1024))
soquete_servidor.listen(5)
print("Servidor local rodando na porta 1024")

#Criação inicial da janela
janela = {}
janela["inicio"] = 0
janela["final"] = 4

#Aceita conexão com cliente
cliente, endereco = soquete_servidor.accept()
print(f"Conexão estabelecida com {endereco}")

while True:
    #Recebe configurações iniciais do client
    modo_operacao = cliente.recv(1024).decode()

    if modo_operacao == 'close':
        break

    print(f"Modo de operação recebido: {modo_operacao}\n")

    #Envia confirmação das configurações para o cliente
    cliente.send(json.dumps(janela).encode())

    pacotes_recebidos = []
    num_sequencia_anterior = -1

    nack = 0
    timeout = 0

    while True:
        #Recebe o pacote do cliente
        pacote = cliente.recv(1024).decode()

        if pacote == '':
            enviarRespostaNegativaServidor(cliente, modo_operacao, "Pacote vazio", num_sequencia_anterior, janela)
            break

        print("\nPacote recebido: ", pacote)

        inicio = janela["inicio"]
        final = janela["final"]
        print(f"Janela: ({inicio}, {final})")

        # Transforma o pacote recebido em um dicionário
        pacote = json.loads(pacote)
        
        #Calcula intervalo da janela
        intervalo_janela = range(janela["inicio"], janela["final"])

        try:
            num_sequencia, dados, checksum_recebido = pacote["num_sequencia"], pacote["dados"], pacote["checksum"]
            num_sequencia = int(num_sequencia)
            checksum_calculado = calcular_checksum(dados)
        except ValueError:
            nack = 1
            enviarRespostaNegativaServidor(cliente, modo_operacao, "Pacote inválido", num_sequencia_anterior, janela)
            continue

        #Break caso seja o fim da mensagem
        if dados == '$$$':
            break

        if "flag" in pacote:
            if pacote["flag"] == "flag_no_ACK":
                nack = 1
                print("Pacote recebido sem enviar o ACK!")
                if modo_operacao == 'repeticao seletiva':        
                    enviarRespostaNegativaServidor(cliente, modo_operacao, "Pacote recebido sem ACK", num_sequencia_anterior, janela)   
                continue
            elif pacote["flag"] == "flag_ignore":
                nack = 1
                print ("* Pacote perdido *")
                if modo_operacao == 'repeticao seletiva':                 
                    enviarRespostaNegativaServidor(cliente, modo_operacao, "Pacote Perdido", num_sequencia_anterior, janela)                  
                continue
            elif pacote["flag"] == "flag_timeout":
                timeout = 1
                nack = 1
                if modo_operacao == 'repeticao seletiva':
                    time.sleep(6)
                    enviarRespostaNegativaServidor(cliente, modo_operacao, "Timeout", num_sequencia_anterior, janela)
                    timeout = 0
                continue

        
        #Verifica se o pacote está no limite da janela
        if num_sequencia not in intervalo_janela:
            enviarRespostaNegativaServidor(cliente, modo_operacao, "Pacote fora da janela", num_sequencia, janela)
            nack = 1
            continue

        #Verifica se o checksum bate
        if checksum_calculado != int(checksum_recebido):
            enviarRespostaNegativaServidor(cliente, modo_operacao, "Checksum inválido", num_sequencia, janela)
            nack = 1
            continue
        
        # Verifica se o pacote é duplicado
        if(num_sequencia == num_sequencia_anterior):
            enviarRespostaNegativaServidor(cliente, modo_operacao, "Pacote duplicado", num_sequencia, janela)
            nack = 1
            continue

        else:
            print("Nada de errado com o pacote!")
            pacotes_recebidos.append(dados)

            janela["inicio"] += 1
            janela["final"] += 1
            
        if modo_operacao == 'repeticao seletiva':
            enviarRespostaFinalServidor(cliente, num_sequencia, janela, timeout, nack)
            timeout = 0

        num_sequencia_anterior = num_sequencia

    #Junta os pacotes válidos recebidos
    mensagem = "".join(pacotes_recebidos)
    print("Mensagem final reconstruída:", mensagem)

    #Envia um ACK (final para repetição seletiva ou único se for go-back-n)
    if modo_operacao == 'go-back-n':
        enviarRespostaFinalServidor(cliente, num_sequencia, janela, timeout, nack)

    janela = {}
    janela["inicio"] = 0
    janela["final"] = 4
    
    nack = 0
    timeout = 0

# Fecha a conexão com o cliente
cliente.close()