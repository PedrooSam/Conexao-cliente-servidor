import socket
import hashlib

def calcular_checksum(dados):
    return hashlib.md5(dados.encode()).hexdigest()

def verificar_integridade(dados, checksum_recebido):
    checksum_calculado = calcular_checksum(dados)
    if checksum_calculado != checksum_recebido:
        return False
    else:
        return True

soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete_servidor.bind(('localhost', 1024))
soquete_servidor.listen(5)
print("Servidor local rodando na porta 1024")

while True:
    cliente, endereco = soquete_servidor.accept()
    print(f"Conexão estabelecida com {endereco}")

    dados_cliente = cliente.recv(1024).decode()
    dados, checksum_cliente = dados_cliente.rsplit(",", 1)

    if not verificar_integridade(dados, checksum_cliente):
        cliente.send(b"NAK")
        print("Erro de integridade: checksum não bate")
        continue

    modo_operacao, tamanho_mensagem = dados.split(',')
    print(f"Modo de operação recebido: {modo_operacao}")
    print(f"Tamanho da mensagem recebido: {tamanho_mensagem}")

    cliente.send(b"ACK")

    requisicao = cliente.recv(1024).decode()
    requisicao_dados, checksum_requisicao = requisicao.rsplit(",", 1)

    if not verificar_integridade(requisicao_dados, checksum_requisicao):
        cliente.send(b"NAK")
        print("Erro de integridade na requisição.")
        continue

    print(f"Requisição recebida: {requisicao_dados}")

    resposta = """HTTP/1.0 200 OK
    Content-Type: text/plain
    Bem-vindo ao servidor!"""

    cliente.sendall(resposta.encode())

    cliente.close()
