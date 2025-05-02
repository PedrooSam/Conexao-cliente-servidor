import json

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
    resposta_servidor = soquete_cliente.recv(512)
    return resposta_servidor.decode()

def enviarRespostaNegativaServidor(soquete_cliente, modo, resposta, num_sequencia, janela):
    retorno = f"{resposta} | NACK{num_sequencia}"
    print(retorno)

    janela["inicio"] += 1
    janela["final"] += 1

    if modo == 'repeticao seletiva':
        soquete_cliente.send(retorno.encode())
        soquete_cliente.send(json.dumps(janela).encode())

def simularErro(pacotes, opcao):
    if opcao == 1:
        return pacotes
    elif opcao == 2:
        pacote = pacotes[0]
        pacote = {'num_sequencia': pacote["num_sequencia"], "dados": pacote["dados"], "checksum": -1}

        return pacotes
    elif opcao == 3:
        pacote = pacotes[0]
        pacote["num_sequencia"] = 5

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
        return pacotes


        
