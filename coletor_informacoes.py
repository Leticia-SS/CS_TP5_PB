import subprocess
import json
import socket
import sys
from datetime import datetime

class ColetorInformacoes:
    def __init__(self):
        self.resultados = {}

    def verificar_dependencias(self):
        dependencias = ['nmap', 'dig', 'host']

        print("Verificando dependencias..")
        try:
            subprocess.run(['nmap', '--version'], capture_output=True, check=True)
            print("nmap encontrado")
        except:
            print("nmap não encontrado")
            return False

        try:
            subprocess.run(['/usr/bin/dig', '-v'], capture_output=True, check=True)
            print("dig encontrado")
        except:
            print("dig não encontrado")
            return False

        try:
            subprocess.run(['host', 'localhost'], capture_output=True, timeout=2)
            print("host encontrado")
        except:
            print("host não encontrado")
            return False

        return True

    def coletar_info_dns_basico(self, dominio):
        print(f"\n=============== Coletando informações DNS para: {dominio} =============== ")

        info_dns = {
            'dominio': dominio, 'timestamp': datetime.now().isoformat(), 'registro_a': [], 'registro_mx': [], 'registro_ns': [], 'registro_txt': []}

        try:
            resultado = subprocess.run(['dig', '+short', 'A', dominio],
                                    capture_output=True, text=True, check=True)
            info_dns['registro_a'] = [ip.strip() for ip in resultado.stdout.splitlines() if ip.strip()]

            resultado = subprocess.run(['dig', '+short', 'MX', dominio],
                                    capture_output=True, text=True, check=True)
            info_dns['registro_mx'] = [mx.strip() for mx in resultado.stdout.splitlines() if mx.strip()]

            resultado = subprocess.run(['dig', '+short', 'NS', dominio],
                                    capture_output=True, text=True, check=True)
            info_dns['registro_ns'] = [ns.strip() for ns in resultado.stdout.splitlines() if ns.strip()]

            resultado = subprocess.run(['dig', '+short', 'TXT', dominio],
                                    capture_output=True, text=True, check=True)
            info_dns['registro_txt'] = [txt.strip() for txt in resultado.stdout.splitlines() if txt.strip()]

        except subprocess.CalledProcessError as e:
            print(f"Erro ao coletar DNS: {e}")

        return info_dns

    def executar_nmap(self, alvo, portas="1-1000"):
        print(f"\n=============== Executando Nmap em: {alvo} (portas: {portas}) ===============")

        resultado_nmap = {'alvo': alvo,'timestamp': datetime.now().isoformat(), 'servicos': []}

        try:
            comando = ['nmap', '-sV', '-p', portas, alvo]
            resultado = subprocess.run(comando, capture_output=True, text=True, check=True)

            linhas = resultado.stdout.split('\n')
            for i, linha in enumerate(linhas):
                if '/tcp' in linha and 'open' in linha:
                    partes = linha.split()
                    if len(partes) >= 4:
                        porta_protocolo = partes[0]
                        estado = partes[1]
                        servico = partes[2] if len(partes) > 2 else 'desconhecido'
                        versao = ' '.join(partes[3:]) if len(partes) > 3 else 'desconhecida'

                        resultado_nmap['servicos'].append({'porta': porta_protocolo, 'estado': estado,'servico': servico,'versao': versao})

        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar nmap: {e}")

        return resultado_nmap

    def coletar_info_host(self, dominio):
        print(f"\n=============== Coletando informações com host: {dominio} =============== ")

        info_host = {'dominio': dominio,'ips': [], 'mail_servers': [], 'name_servers': []}

        try:
            resultado = subprocess.run(['host', dominio], capture_output=True, text=True, check=True)
            linhas = resultado.stdout.split('\n')

            for linha in linhas:
                if 'has address' in linha:
                    ip = linha.split()[-1]
                    info_host['ips'].append(ip)
                elif 'mail is handled' in linha:
                    mail_server = linha.split()[-1]
                    info_host['mail_servers'].append(mail_server)
                elif 'name server' in linha:
                    ns = linha.split()[-1]
                    info_host['name_servers'].append(ns)

        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar host: {e}")

        return info_host

    def verificar_portas_com_socket(self, host, portas=[80, 443, 22, 21, 25]):
        print(f"\n=============== Verificando portas em: {host} =============== ")

        portas_abertas = []

        for porta in portas:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2)
                    resultado = sock.connect_ex((host, porta))
                    if resultado == 0:
                        portas_abertas.append(porta)
                        print(f"  Porta {porta}: ABERTA")
                    else:
                        print(f"  Porta {porta}: FECHADA")
            except Exception as e:
                print(f"  Porta {porta}: ERRO - {e}")

        return portas_abertas

    def exibir_resultados(self, resultados):
        print("=============== RESULTADOS DA COLETA =============== ")

        for dominio, info in resultados.items():
            print(f"\n=============== DOMÍNIO: {dominio} ===============")

            if 'dns' in info:
                dns = info['dns']
                print("============== INFORMAÇÕES DNS: ===============")
                print(f"  IPs (Registro A): {', '.join(dns['registro_a']) if dns['registro_a'] else 'Nenhum'}")
                print(f"  Servidores de Email (MX): {', '.join(dns['registro_mx']) if dns['registro_mx'] else 'Nenhum'}")
                print(f"  Name Servers (NS): {', '.join(dns['registro_ns']) if dns['registro_ns'] else 'Nenhum'}")
                print(f"  Registros TXT: {', '.join(dns['registro_txt']) if dns['registro_txt'] else 'Nenhum'}")

            if 'host' in info:
                host_info = info['host']
                print(f"  IPs (host): {', '.join(host_info['ips']) if host_info['ips'] else 'Nenhum'}")

            if 'nmap' in info:
                nmap = info['nmap']
                print("\n=============== SERVIÇOS ENCONTRADOS (Nmap): =============== ")
                for servico in nmap['servicos']:
                    print(f"  {servico['porta']} - {servico['servico']} - {servico['versao']}")

            if 'portas_abertas' in info:
                print(f"\n===============  PORTAS ABERTAS: {', '.join(map(str, info['portas_abertas']))} =============== ")

    def salvar_resultados(self, resultados, arquivo="resultados_coleta.json"):
        with open(arquivo, 'w') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        print(f"\n=============== Resultados salvos em: {arquivo} =============== ")

    def coletar_informacoes_completas(self, dominio):
        print(f"Iniciando coleta para: {dominio}")

        resultados_dominio = {}

        resultados_dominio['dns'] = self.coletar_info_dns_basico(dominio)

        resultados_dominio['host'] = self.coletar_info_host(dominio)

        ips_alvo = resultados_dominio['dns']['registro_a']
        if not ips_alvo:
            ips_alvo = resultados_dominio['host']['ips']

        if ips_alvo:
            ip_alvo = ips_alvo[0]

            resultados_dominio['portas_abertas'] = self.verificar_portas_com_socket(ip_alvo)

            resultados_dominio['nmap'] = self.executar_nmap(ip_alvo, "21,22,23,25,53,80,110,443,993,995")

        return resultados_dominio

def main():
    print("=============== COLETOR DE INFORMAÇÕES DE DOMÍNIOS E SERVIDORES ===============")

    coletor = ColetorInformacoes()

    if not coletor.verificar_dependencias():
        print("\nDependências faltando. Instale as ferramentas necessárias.")
        sys.exit(1)

    dominio = input("\nDigite o domínio para análise (ex: google.com): ").strip()

    if not dominio:
        print("Domínio não informado.")
        sys.exit(1)

    resultados = {}
    resultados[dominio] = coletor.coletar_informacoes_completas(dominio)

    coletor.exibir_resultados(resultados)

    coletor.salvar_resultados(resultados)

    print(f"\nAnálise concluída para: {dominio}")

if __name__ == "__main__":
    main()







