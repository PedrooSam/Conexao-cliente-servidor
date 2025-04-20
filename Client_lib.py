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

def dividir_pacotes(mensagem):
    pacotes = []
    tamanho_pacote = 3

    for i in range(0, len(mensagem), tamanho_pacote):
        pacote = mensagem[i:i+tamanho_pacote]
        pacotes.append(pacote)

    return pacotes