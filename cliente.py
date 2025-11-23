import socket
import ssl
import threading
import json
from cryptography.fernet import Fernet
import base64
import time

class ClienteMessenger:
    def __init__(self, host='localhost', porta=8443):
        self.host = host
        self.porta = porta
        self.socket_cliente = None
        self.cifrador = None
        self.usuario = None
        self.conectado = False
        
        self.contexto_ssl = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.contexto_ssl.check_hostname = False
        self.contexto_ssl.verify_mode = ssl.CERT_NONE
    
    def conectar_servidor(self, nome_usuario):
        try:
            self.usuario = nome_usuario
            
            socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente = self.contexto_ssl.wrap_socket(
                socket_cliente,
                server_hostname=self.host
            )
            self.socket_cliente.connect((self.host, self.porta))
            self.conectado = True
            
            print(f"Conectado ao servidor {self.host}:{self.porta}")
            
            dados_chave = self.socket_cliente.recv(1024).decode('utf-8')
            chave_info = json.loads(dados_chave)
            
            if chave_info['tipo'] == 'chave_criptografia':
                chave_criptografia = base64.urlsafe_b64decode(chave_info['chave'].encode('utf-8'))
                self.cifrador = Fernet(chave_criptografia)
                print("Chave de criptografia recebida do servidor")
            
            mensagem_registro = json.dumps({
                'tipo': 'registro',
                'usuario': self.usuario
            })
            self.socket_cliente.send(mensagem_registro.encode('utf-8'))
            
            thread_recebimento = threading.Thread(target=self.receber_mensagens)
            thread_recebimento.daemon = True
            thread_recebimento.start()
            
            return True
            
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def criptografar_mensagem(self, mensagem):
        mensagem_bytes = mensagem.encode('utf-8')
        mensagem_criptografada = self.cifrador.encrypt(mensagem_bytes)
        return base64.urlsafe_b64encode(mensagem_criptografada).decode('utf-8')
    
    def descriptografar_mensagem(self, mensagem_criptografada):
        try:
            mensagem_bytes = base64.urlsafe_b64decode(mensagem_criptografada.encode('utf-8'))
            mensagem_descriptografada = self.cifrador.decrypt(mensagem_bytes)
            return mensagem_descriptografada.decode('utf-8')
        except Exception as e:
            return f"Erro ao descriptografar mensagem: {e}"
    
    def enviar_mensagem(self, mensagem):
        if not self.conectado or not self.cifrador:
            print("Cliente não conectado ou chave não configurada")
            return
        
        try:
            mensagem_criptografada = self.criptografar_mensagem(mensagem)
            
            dados_mensagem = json.dumps({
                'tipo': 'mensagem',
                'usuario': self.usuario,
                'conteudo': mensagem_criptografada,
                'timestamp': time.time()
            })
            
            self.socket_cliente.send(dados_mensagem.encode('utf-8'))
            print(f"Mensagem enviada: {mensagem}")
            
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            self.conectado = False
    
    def receber_mensagens(self):
        while self.conectado:
            try:
                dados = self.socket_cliente.recv(1024)
                if not dados:
                    break
                
                mensagem_recebida = json.loads(dados.decode('utf-8'))
                
                if mensagem_recebida['tipo'] == 'mensagem':
                    mensagem_descriptografada = self.descriptografar_mensagem(
                        mensagem_recebida['conteudo']
                    )
                    
                    usuario = mensagem_recebida['usuario']
                    timestamp = mensagem_recebida.get('timestamp', time.time())
                    hora = time.strftime('%H:%M:%S', time.localtime(timestamp))
                    
                    print(f"\n[{hora}] {usuario}: {mensagem_descriptografada}")
                    print("Digite sua mensagem: ", end='', flush=True)
                    
            except Exception as e:
                if self.conectado:
                    print(f"\nErro ao receber mensagem: {e}")
                break
        
        print("\nConexão com o servidor perdida")
        self.conectado = False
    
    def iniciar_chat(self):
        if not self.conectado:
            print("Cliente não conectado ao servidor")
            return
        
        print(f"\nChat seguro iniciado como: {self.usuario}")
        print("Digite '/sair' para desconectar\n")

        
        try:
            while self.conectado:
                mensagem = input("Digite sua mensagem: ")
                
                if mensagem.lower() == '/sair':
                    break
                
                if mensagem.strip():
                    self.enviar_mensagem(mensagem)
                    
        except KeyboardInterrupt:
            print("\n\nDesconectando...")
        finally:
            self.socket_cliente.close()
            print("Conexão encerrada")

def main():
    print("=============== MESSENGER SEGURO COM TLS ===============\n")
    
    host = input("Servidor [localhost]: ") or "localhost"
    porta = input("Porta [8443]: ") or "8443"
    usuario = input("Seu nome de usuário: ")
    
    if not usuario:
        print("Nome de usuario é obrigatório")
        return
    
    try:
        porta = int(porta)
    except ValueError:
        print("Porta deve ser um número")
        return
    
    cliente = ClienteMessenger(host, porta)
    
    if cliente.conectar_servidor(usuario):
        cliente.iniciar_chat()
    else:
        print("Não foi possível conectar ao servidor")

if __name__ == "__main__":
    main()




