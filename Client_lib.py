import socket

def solicitar_mensagem():
    mensagem = input("Digite a mensagem: ")
    return mensagem

def soliticar_modoOperacao():
    while True:
        selecao = int(input("Informe o modo de operação (go-back-n[1] ou repeticao seletiva[2]): "))
        if selecao == 1:
            return "go-back-n"
        elif selecao == 2:
            return "repeticao seletiva"
        else:
            print("Tente novamente")

def calcular_checksum(pacote):
    return sum(pacote.encode()) % 256


def dividir_pacotes(mensagem):
    tamanho_pacote = 3

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
    pacotes.append({"num_sequencia": num_sequencia, "dados": "$$$", "checksum": 0})

    return pacotes

def receberRespostaServidor(soquete_cliente):
    try: 
        resposta_servidor = soquete_cliente.recv(512)
        return resposta_servidor.decode()
    except socket.timeout:
        print("Tempo de espera excedido. O servidor não respondeu.")
        soquete_cliente.close()
        exit()