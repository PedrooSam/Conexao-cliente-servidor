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
    pacotes = []
    tamanho_pacote = 3

    #Divide a mensagem em uma lista de 3 em 3 caracteres
    for i in range(0, len(mensagem), tamanho_pacote):
        dados = mensagem[i:i+tamanho_pacote]
        checksum = calcular_checksum(dados)
        pacotes.append(f"{dados}:{checksum}")
    
    #Adiciona uma verificação que representa o fim dos pacotes
    pacotes.append('$$$')

    return pacotes