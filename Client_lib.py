import json
import time
import socket

def solicitar_mensagem():
    print()
    mensagem = input("Digite a mensagem: ")
    return mensagem

def soliticar_modoOperacao():
    while True:
        print()
        print("Selecione o modo de operação:")
        print("1. Go-Back-N")
        print("2. Repetição Seletiva")
        print("0. Fechar aplicação")
        selecao = int(input("Selecione uma opção: "))
        if selecao == 1:
            return "go-back-n"
        elif selecao == 2:
            return "repeticao seletiva"
        elif selecao == 0:
            return "close"
        else:
            print("Tente novamente")

def calcular_checksum(pacote):
    return sum(pacote.encode()) % 256


def dividir_pacotes(mensagem, tamanho_mensagem):
    tamanho_pacote = tamanho_mensagem 

    num_sequencia = 0

    pacotes = []

    #Divide a mensagem em uma lista de 3 em 3 caracteres
    for i in range(0, len(mensagem), tamanho_pacote):

        pacote = {}

        dados = mensagem[i:i+tamanho_pacote]
        checksum = calcular_checksum(dados)

        #Adiciona as informações do pacote em uma dicionário
        pacote["num_sequencia"] = num_sequencia
        pacote["dados"] = dados
        pacote["checksum"] = checksum

        #Soma o numero de sequencia do pacote (contador)
        num_sequencia += 1

        pacotes.append(pacote)

    
    #Adiciona uma verificação que representa o fim dos pacotes
    pacotes[-1]["flag"] = "$$$"

    return pacotes

def receberRespostaServidor(soquete_cliente):
    resposta_servidor = soquete_cliente.recv(512)
    return resposta_servidor.decode()

def receberPacoteServidor(soquete_cliente, opcao):
    if opcao == 6:
        soquete_cliente.settimeout(5)
    
    try:
        print()
        start_time = time.time()
        resposta = receberRespostaServidor(soquete_cliente)
        print('Resposta: ', resposta)

        janela = json.loads(receberRespostaServidor(soquete_cliente))

        inicio = janela["inicio"]
        final = janela["final"]

        print(f"Janela: ({inicio}, {final})")

        elapsed_time = time.time() - start_time
        soquete_cliente.send(str(elapsed_time).encode())
        print(f"Tempo de resposta: {elapsed_time:.2f} segundos")
        time.sleep(0.2)
    except socket.timeout:
        timeout_time = time.time() - start_time
        soquete_cliente.send(str(timeout_time).encode())
        print("Tempo de espera excedido!")
        print(f"Tempo de espera: {timeout_time:.2f} segundos")
        time.sleep(1)
        return "break"

def enviarRespostaNegativaServidor(soquete_cliente, modo, resposta, num_sequencia, janela):
    retorno = f"{resposta} | NACK{num_sequencia}"
    print(retorno)

    if modo == 'repeticao seletiva':
        soquete_cliente.send(retorno.encode())

        time.sleep(0.2)

        soquete_cliente.send(json.dumps(janela).encode())
        elapsed_time = soquete_cliente.recv(1024).decode()
        print(f"Tempo de resposta: {float(elapsed_time):.2f} segundos")

def enviarRespostaFinalServidor(soquete_cliente, num_sequencia, janela, timeout, nack):
    if timeout == 1:
        time.sleep(6)
    if nack == 0:
        soquete_cliente.sendall(b"ACK" + str(num_sequencia).encode())
    else:
        soquete_cliente.sendall(b"NACK" + str(num_sequencia).encode())

    time.sleep(0.2)

    soquete_cliente.send(json.dumps(janela).encode())

    elapsed_time = soquete_cliente.recv(1024).decode()
    print(f"Tempo de resposta: {float(elapsed_time):.2f} segundos")


def simularErro(pacotes, opcao):
    if opcao == 1:
        return pacotes
    elif opcao == 2:
        pacote = pacotes[0]
        pacote["checksum"]  = -1

        return pacotes
    elif opcao == 3:
        pacote = pacotes[0]

        print()
        num_sequencia = int(input("Digite o número de sequência do pacote a ser perdido: "))

        pacote["num_sequencia"] = num_sequencia

        return pacotes
    elif opcao == 4:
        pacote = pacotes[0]

        pacote["flag"] = "flag_no_ACK"

        return pacotes
    elif opcao == 5:
        pacote = pacotes[0]

        pacote["flag"] = "flag_ignore"

        return pacotes
    elif opcao == 6:
        pacote = pacotes[0]

        pacote["flag"] = "flag_timeout"
        return pacotes

def limpar_buffer(soquete):
    soquete.setblocking(False)  
    try:
        while True:
            dados = soquete.recv(1024)
            if not dados:
                break
    except BlockingIOError:
        pass
    finally:
        soquete.setblocking(True)  
