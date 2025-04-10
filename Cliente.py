import socket
import hashlib
import time

def calcular_checksum(dados):
    return hashlib.md5(dados.encode()).hexdigest()

def solicitarTamanho():
    while True:
        mensagem = input("Digite a mensagem (tem que ter no máximo 3 caracteres): ")
        if len(mensagem) <= 3:
            return mensagem
        else:
            print("Tente novamente")

def modoOperacao():
    while True:
        selecao = int(input("Informe o modo de operação (go-back-n[1] ou repeticao seletiva[2]): "))
        if selecao == 1:
            return "go-back-n"
        elif selecao == 2:
            return "repeticao seletiva"
        else:
            print("Tente novamente")

def esperar_resposta(soquete_cliente, timeout=5):
    soquete_cliente.settimeout(timeout)
    try:
        resposta = soquete_cliente.recv(512)
        return resposta
    except socket.timeout:
        print("Tempo excedido, retransmitindo...")
        return None

numero_sequencial = 0

def incrementar_numero_sequencial():
    global numero_sequencial
    numero_sequencial += 1
    return numero_sequencial

def dividir_em_pacotes(mensagem, tamanho_pacote):
    pacotes = []
    for i in range(0, len(mensagem), tamanho_pacote):
        pacote = mensagem[i:i+tamanho_pacote]
        pacotes.append(pacote)
    return pacotes

def enviar_com_janela(soquete_cliente, pacotes, janela_tamanho):
    enviados = 0
    acknowledgments = 0
    
    try:
        while enviados < len(pacotes):
            while enviados - acknowledgments < janela_tamanho and enviados < len(pacotes):
                pacote = pacotes[enviados]
                checksum = calcular_checksum(pacote)
                pacote_completo = f"{pacote},{checksum}"
                try:
                    soquete_cliente.sendall(pacote_completo.encode())
                    print(f"Enviando pacote {enviados + 1}")
                    enviados += 1
                except ConnectionError as e:
                    print(f"Erro ao enviar pacote: {e}")
                    return False
            
            try:
                resposta = esperar_resposta(soquete_cliente)
                if resposta == b"ACK":
                    print("ACK recebido, movendo a janela.")
                    acknowledgments += 1
                else:
                    print("Erro ou timeout, retransmitindo pacotes.")
            except ConnectionError as e:
                print(f"Conexão encerrada pelo servidor: {e}")
                return False
        return True
    except Exception as e:
        print(f"Erro durante o envio: {e}")
        return False

soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
endereco_servidor = ("localhost", 1024)
soquete_cliente.connect(endereco_servidor)

modo_operacao = modoOperacao()
tamanho_mensagem = solicitarTamanho()

dados_para_servidor = f"{modo_operacao},{tamanho_mensagem}"
checksum = calcular_checksum(dados_para_servidor)
dados_para_servidor_completo = f"{dados_para_servidor},{checksum}"
soquete_cliente.sendall(dados_para_servidor_completo.encode())

resposta_servidor = esperar_resposta(soquete_cliente)

if resposta_servidor and resposta_servidor == b"ACK":
    print(f"Resposta do servidor: {resposta_servidor.decode()}")
    
    
    requisicao = "GET / HTTP/1.0\r\nHost: localhost\r\n\r\n"
    checksum_requisicao = calcular_checksum(requisicao)
    requisicao_completo = f"{requisicao},{checksum_requisicao}"
    
    try:
        soquete_cliente.sendall(requisicao_completo.encode())
        print("Requisição HTTP enviada com sucesso")
        
        resposta_http = esperar_resposta(soquete_cliente)
        if resposta_http:
            print("Resposta HTTP do servidor:")
            print(resposta_http.decode())
        else:
            print("Não foi recebida resposta HTTP do servidor")
    except ConnectionError as e:
        print(f"Erro na comunicação HTTP: {e}")
else:
    print("Não houve resposta ACK do servidor ou a comunicação falhou")


print("Fechando conexão com o servidor...")
soquete_cliente.close()
