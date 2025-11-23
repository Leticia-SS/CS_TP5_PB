from scapy.all import *
import time
import sys
from datetime import datetime

class AnalisadorRede:
    def __init__(self):
        self.contador_pacotes = 0
        self.pacotes_capturados = []

    def formatar_timestamp(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

    def analisar_pacote(self, pacote):
        info = {'timestamp': time.time(), 'numero': self.contador_pacotes + 1, 'camadas': []}

        if Ether in pacote:
            eth = pacote[Ether]
            info['camadas'].append({'tipo': 'Ethernet','origem': eth.src,'destino': eth.dst,'protocolo': eth.type})

        if IP in pacote:
            ip = pacote[IP]
            info['camadas'].append({'tipo': 'IP','origem': ip.src,'destino': ip.dst,'protocolo': ip.proto,'ttl': ip.ttl,'tamanho': ip.len})

        if TCP in pacote:
            tcp = pacote[TCP]
            flags = self.interpretar_flags_tcp(tcp.flags)
            info['camadas'].append({'tipo': 'TCP','porta_origem': tcp.sport,'porta_destino': tcp.dport,'flags': flags,'sequencia': tcp.seq, 'ack': tcp.ack,'tamanho': len(tcp.payload)})

        elif UDP in pacote:
            udp = pacote[UDP]
            info['camadas'].append({'tipo': 'UDP', 'porta_origem': udp.sport, 'porta_destino': udp.dport,'tamanho': udp.len})

        elif ICMP in pacote:
            icmp = pacote[ICMP]
            info['camadas'].append({ 'tipo': 'ICMP','tipo_icmp': icmp.type, 'codigo': icmp.code})

        self.pacotes_capturados.append(info)
        self.contador_pacotes += 1
        return info

    def interpretar_flags_tcp(self, flags):
        flag_names = []
        if flags & 0x01: flag_names.append("FIN")
        if flags & 0x02: flag_names.append("SYN")
        if flags & 0x04: flag_names.append("RST")
        if flags & 0x08: flag_names.append("PSH")
        if flags & 0x10: flag_names.append("ACK")
        if flags & 0x20: flag_names.append("URG")
        if flags & 0x40: flag_names.append("ECE")
        if flags & 0x80: flag_names.append("CWR")

        return "/".join(flag_names) if flag_names else "Nenhuma"

    def exibir_pacote(self, info_pacote):
        print(f"=============== PACOTE #{info_pacote['numero']} - {self.formatar_timestamp(info_pacote['timestamp'])} ===============")

        for camada in info_pacote['camadas']:
            print(f"\n[{camada['tipo']}]")

            if camada['tipo'] == 'Ethernet':
                print(f" Origem:      {camada['origem']}")
                print(f" Destino:     {camada['destino']}")
                print(f" Protocolo:   {camada['protocolo']:04x}")

            elif camada['tipo'] == 'IP':
                print(f" Origem:      {camada['origem']}")
                print(f" Destino:     {camada['destino']}")
                print(f" Protocolo:   {camada['protocolo']}")
                print(f" TTL:         {camada['ttl']}")
                print(f" Tamanho:     {camada['tamanho']} bytes")

            elif camada['tipo'] == 'TCP':
                print(f" Porta Origem:    {camada['porta_origem']}")
                print(f" Porta Destino:   {camada['porta_destino']}")
                print(f" Flags:           {camada['flags']}")
                print(f" Sequência:       {camada['sequencia']}")
                print(f" ACK:             {camada['ack']}")
                print(f" Tamanho Dados:   {camada['tamanho']} bytes")

            elif camada['tipo'] == 'UDP':
                print(f" Porta Origem:    {camada['porta_origem']}")
                print(f" Porta Destino:   {camada['porta_destino']}")
                print(f" Tamanho:         {camada['tamanho']} bytes")

            elif camada['tipo'] == 'ICMP':
                print(f" Tipo:    {camada['tipo_icmp']}")
                print(f" Código:  {camada['codigo']}")

        print(f"=================================================================")

    def callback_captura(self, pacote):
        info_pacote = self.analisar_pacote(pacote)
        self.exibir_pacote(info_pacote)

        if self.contador_pacotes % 10 == 0:
            self.exibir_estatisticas()

    def exibir_estatisticas(self):
        print(f"=============== ESTATÍSTICAS DA CAPTURA ================")
        print(f"Total de pacotes capturados: {self.contador_pacotes}")

        protocolos = {}
        for pacote in self.pacotes_capturados:
            for camada in pacote['camadas']:
                if camada['tipo'] in ['TCP', 'UDP', 'ICMP']:
                    protocolos[camada['tipo']] = protocolos.get(camada['tipo'], 0) + 1

        print("Pacotes por protocolo:")
        for protocolo, quantidade in protocolos.items():
            print(f"  {protocolo}: {quantidade}")

        print(f"=================================================================")


    def listar_interfaces(self):
        interfaces = get_windows_if_list() if sys.platform == "win32" else get_if_list()
        print("\nInterfaces de rede disponíveis:")
        for i, interface in enumerate(interfaces):
            print(f"  {i}: {interface}")
        return interfaces

    def iniciar_captura(self, interface=None, filtro="tcp", quantidade=0):
        print("Iniciando captura de pacotes de rede...")
        print("Pressione Ctrl+C para parar a captura\n")

        try:
            sniff(
                iface=interface,
                filter=filtro,
                prn=self.callback_captura,
                count=quantidade
            )

        except KeyboardInterrupt:
            print("\n\nCaptura interrompida pelo usuário")
        except Exception as e:
            print(f"Erro durante a captura: {e}")

        finally:
            self.exibir_estatisticas()
            print("\nCaptura finalizada")

def main():
    print("=============== ANALISADOR DE PACOTES DE REDE ===============")

    analisador = AnalisadorRede()

    print("\nConfigurações da captura:")

    interfaces = analisador.listar_interfaces()

    if interfaces:
        try:
            escolha = input(f"\nSelecione a interface (0-{len(interfaces)-1}) ou Enter para padrão: ")
            if escolha.strip():
                interface = interfaces[int(escolha)]
            else:
                interface = None
        except (ValueError, IndexError):
            print("Interface inválida, usando padrão")
            interface = None
    else:
        interface = None

    filtro = input("Filtro (ex: tcp, udp, icmp, port 80) [tcp]: ").strip()
    if not filtro:
        filtro = "tcp"

    try:
        quantidade = input("Quantidade de pacotes (0 para ilimitado) [0]: ").strip()
        quantidade = int(quantidade) if quantidade else 0
    except ValueError:
        quantidade = 0

    print(f"\nIniciando captura com:")
    print(f"  Interface: {interface or 'padrão'}")
    print(f"  Filtro: {filtro}")
    print(f"  Quantidade: {quantidade or 'ilimitado'}")
    print(f"=================================================================")

    analisador.iniciar_captura(interface, filtro, quantidade)

if __name__ == "__main__":
    main()

























