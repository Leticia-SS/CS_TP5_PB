import socket
import ssl
import threading
import json
from cryptography.fernet import Fernet
import base64
import os

class ServidorMessenger:
    def __init__(self, host='localhost', porta=8443):
        self.host = host
        self.porta = porta
        self.clientes_conectados = {}
        self.chave_criptografia = Fernet.generate_key()
        self.cifrador = Fernet(self.chave_criptografia)

        if not os.path.exists('certificado.pem') or not os.path.exists('chave_privada.pem'):
            self.gerar_certificados()
        
        self.contexto_ssl = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.contexto_ssl.load_cert_chain(certfile='certificado.pem', keyfile='chave_privada.pem')
        self.contexto_ssl.check_hostname = False
        
    def gerar_certificados(self):
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import datetime
            
            chave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            assunto = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])

            certificado = x509.CertificateBuilder().subject_name(assunto).issuer_name(assunto).public_key(chave_privada.public_key()).serial_number(x509.random_serial_number()).not_valid_before(datetime.datetime.utcnow()).not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365)).sign(chave_privada, hashes.SHA256())
            
            with open("chave_privada.pem", "wb") as f:
                f.write(chave_privada.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                ))
            
            with open("certificado.pem", "wb") as f:
                f.write(certificado.public_bytes(serialization.Encoding.PEM))
                
            print("Certificados TLS gerados com sucesso!")
            
        except ImportError:
            print("⚠ Biblioteca cryptography não instalada.")

    def criptografar_mensagem(self, mensagem):
        mensagem_bytes = mensagem.encode('utf-8')
        mensagem_criptografada = self.cifrador.encrypt(mensagem_bytes)
        return base64.urlsafe_b64encode(mensagem_criptografada).decode('utf-8')
    
    def processar_cliente(self, conexao_cliente, endereco):
        try:
            print(f"Novo cliente conectado: {endereco}")
            
            dados_chave = json.dumps({
                'tipo': 'chave_criptografia',
                'chave': base64.urlsafe_b64encode(self.chave_criptografia).decode('utf-8')
            })
            conexao_cliente.send(dados_chave.encode('utf-8'))
            
            while True:
                dados = conexao_cliente.recv(1024)
                if not dados:
                    break
                
                mensagem_recebida = json.loads(dados.decode('utf-8'))
                
                if mensagem_recebida['tipo'] == 'registro':
                    nome_usuario = mensagem_recebida['usuario']
                    self.clientes_conectados[nome_usuario] = conexao_cliente
                    print(f"Usuário registrado: {nome_usuario}")
                    
                    mensagem_sistema = self.criptografar_mensagem(
                        f"~~{nome_usuario} entrou no chat"
                    )
                    self.transmitir_mensagem(mensagem_sistema, nome_usuario)
                    
                elif mensagem_recebida['tipo'] == 'mensagem':
                    mensagem_criptografada = mensagem_recebida['conteudo']
                    usuario_origem = mensagem_recebida['usuario']
                    
                    print(f"Mensagem de {usuario_origem}: {self.cifrador.decrypt(base64.urlsafe_b64decode(mensagem_criptografada)).decode('utf-8')}")
                    
                    mensagem_transmitir = json.dumps({
                        'tipo': 'mensagem',
                        'usuario': usuario_origem,
                        'conteudo': mensagem_criptografada
                    })
                    
                    self.transmitir_mensagem_para_todos(mensagem_transmitir, usuario_origem)
                    
        except Exception as e:
            print(f"Erro no cliente {endereco}: {e}")
        finally:
            for usuario, conexao in list(self.clientes_conectados.items()):
                if conexao == conexao_cliente:
                    del self.clientes_conectados[usuario]
                    print(f"Usuário desconectado: {usuario}")
                    break
            conexao_cliente.close()
    
    def transmitir_mensagem(self, mensagem_criptografada, usuario_origem):
        mensagem_transmitir = json.dumps({
            'tipo': 'mensagem',
            'usuario': 'Sistema',
            'conteudo': mensagem_criptografada
        })

        for usuario, conexao in self.clientes_conectados.items():
            if usuario != usuario_origem:
                try:
                    conexao.send(mensagem_transmitir.encode('utf-8'))
                except:
                    if usuario in self.clientes_conectados:
                        del self.clientes_conectados[usuario]


    def transmitir_mensagem_para_todos(self, mensagem, usuario_origem):
        for usuario, conexao in self.clientes_conectados.items():
            if usuario != usuario_origem:
                try:
                    conexao.send(mensagem.encode('utf-8'))
                except:
                    if usuario in self.clientes_conectados:
                        del self.clientes_conectados[usuario]
    
    def iniciar_servidor(self):
        try:
            socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_servidor.bind((self.host, self.porta))
            socket_servidor.listen(5)
            
            print(f"Servidor messenger seguro iniciado em {self.host}:{self.porta}")
            print("Aguardando conexões de clientes...")
            
            while True:
                conexao_cliente, endereco = socket_servidor.accept()
                
                conexao_segura = self.contexto_ssl.wrap_socket(
                    conexao_cliente, 
                    server_side=True
                )
                
                thread_cliente = threading.Thread(
                    target=self.processar_cliente, 
                    args=(conexao_segura, endereco)
                )
                thread_cliente.daemon = True
                thread_cliente.start()
                
        except Exception as e:
            print(f"Erro no servidor: {e}")

if __name__ == "__main__":
    servidor = ServidorMessenger()
    servidor.iniciar_servidor()
