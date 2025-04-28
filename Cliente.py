import socket
from time import sleep
import Client_lib
import json

# ==================== CLIENTE ==================== #

# Criando conexão com servidor
soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
endereco_servidor = ("localhost", 1024)
soquete_cliente.connect(endereco_servidor)

# Solicita informações do cliente
modo_operacao = Client_lib.soliticar_modoOperacao()
mensagem = Client_lib.solicitar_mensagem()

# Divide a mensagem em pacotes e adiciona flag de rajada
pacotes = Client_lib.dividir_pacotes(mensagem)

#Adiciona flag de rajada
rajada = False
if len(pacotes) > 1:
    rajada = True

# Envia especificações para o servidor
dados_para_servidor = f"{modo_operacao},{rajada}"
soquete_cliente.sendall(dados_para_servidor.encode())

# Obtém a resposta do servidor
resposta_servidor = soquete_cliente.recv(512)
print(f"Resposta do servidor: {resposta_servidor.decode()}")

# Controle de janela
tamanho_janela = 4  # Tamanho fixo da janela
base = 0  # Índice da base da janela
next_seq_num = 0  # Número da próxima sequência de pacote a ser enviado

# Envio de pacotes
while base < len(pacotes):

    # Envia pacotes dentro da janela
    while next_seq_num < base + tamanho_janela and next_seq_num < len(pacotes):
        pacote_json = json.dumps(pacotes[next_seq_num])
        print(f"Enviando pacote: {pacote_json}")
        soquete_cliente.sendall(pacote_json.encode())
        next_seq_num += 1
    if base >= len(pacotes):
        break
    # Espera resposta do servidor
    try:
        soquete_cliente.settimeout(3.0)  # Define timeout para esperar a resposta
        resposta = soquete_cliente.recv(512).decode()
        print("Resposta do servidor:", resposta)

        if not resposta:
            print("Servidor fechou a conexão. Finalizando cliente...")
            break

        # Caso seja Go-Back-N, ajusta a base conforme o ACK
        if modo_operacao == 'go-back-n':
            if "ACK" in resposta:
                qtd_acks = resposta.count("ACK")
                base += qtd_acks  # Avança base conforme quantidade de ACKs
                print(f"ACKs recebidos: {qtd_acks}. Nova base: {base}")
            else:
                print("Erro detectado, voltando janela...")
                next_seq_num = base  # Reenvia a partir da base

        # Caso seja Repetição Seletiva, confirma pacotes individualmente
        elif modo_operacao == 'repeticao seletiva':
            base += 1  # Incrementa base após o ACK individual
    except socket.timeout:
        print("Timeout: reenviando janela a partir do base...")
        next_seq_num = base  # Reenvia a partir da base


# Fecha a conexão com o servidor
soquete_cliente.close()
