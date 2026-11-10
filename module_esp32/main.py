import uasyncio as asyncio
import time
import network
from rele import Rele
from display_agua import DisplayAgua
from config_manager import ConfigManager
from api import ServidorAPI

# ==========================================================
# CONFIGURAÇÕES DE REDE (WI-FI E IP FIXO)
# ==========================================================
SSID_ROTEADOR = "NOME_DO_SEU_WIFI"
SENHA_ROTEADOR = "SENHA_DO_SEU_WIFI"

# Definições do IP Estático:
IP_DESEJADO = "192.168.1.200"
MASCARA     = "255.255.255.0"
GATEWAY     = "192.168.1.1"       # IP do seu roteador
DNS         = "192.168.1.1"       # Ou "8.8.8.8"

NOME_AP = "ESP_Tanque"

# ==========================================================
# INSTÂNCIAS DE PERIFÉRICOS E MÓDULOS
# ==========================================================
bomba = Rele(13)
display = DisplayAgua(scl_pin=12, sda_pin=14)
cfg = ConfigManager()

# Estado dinâmico compartilhado em memória com a API
estado = {
    "nivel": 100,
    "bomba_ligada": False
}


def iniciar_rede():
    wlan_sta = network.WLAN(network.STA_IF)
    wlan_ap = network.WLAN(network.AP_IF)

    display.tela_loading("Buscando Wi-Fi", 10)
    wlan_ap.active(False)
    wlan_sta.active(True)

    # 1. Aplica o IP fixo antes da autenticação
    wlan_sta.ifconfig((IP_DESEJADO, MASCARA, GATEWAY, DNS))
    print(f"Definindo IP Fixo: {IP_DESEJADO}")

    # 2. Conecta ao roteador
    wlan_sta.connect(SSID_ROTEADOR, SENHA_ROTEADOR)

    tentativas = 20
    for i in range(tentativas):
        if wlan_sta.isconnected():
            break
        progresso = 10 + int(((i + 1) / tentativas) * 75)
        display.tela_loading("Conectando...", progresso)
        time.sleep(0.5)

    # 3. Validação da conexão
    if wlan_sta.isconnected():
        dados_rede = wlan_sta.ifconfig()
        ip = dados_rede[0]
        print(f"Wi-Fi conectado com sucesso! IP Fixo: {ip}")
        display.tela_loading("Wi-Fi Conectado!", 100)
        time.sleep(1)
        return ip
    else:
        # Fallback para ponto de acesso próprio caso o Wi-Fi falhe
        print("Falha ao conectar no Wi-Fi. Iniciando AP de emergência...")
        display.tela_loading("Criando AP...", 90)
        wlan_sta.active(False)
        wlan_ap.active(True)
        wlan_ap.config(essid=NOME_AP)
        ip = wlan_ap.ifconfig()[0]
        display.tela_loading("Modo AP Ativo!", 100)
        time.sleep(1)
        return f"AP:{ip}"


def controlar_bomba_manual(ligar: bool):
  if ligar:
    bomba.on()
  else:
    bomba.off()
  estado["bomba_ligada"] = bomba.ligado
  print(f"[MANUAL] Bomba alterada para: {'LIGADA' if ligar else 'DESLIGADA'}")

async def loop_controle_tanque():
    passo = -10
    while True:
        # Configurações dinâmicas persistidas
        gatilho_ligar = cfg.obter("gatilho_ligar_pct")
        gatilho_desligar = cfg.obter("gatilho_desligar_pct")
        delay_s = cfg.obter("delay_leitura_s")

        # 1. Regra de acionamento do relé
        if estado["nivel"] <= gatilho_ligar and not bomba.ligado:
            bomba.on()
            print(f"Bomba acionada! (Nível <= {gatilho_ligar}%)")
        elif estado["nivel"] >= gatilho_desligar and bomba.ligado:
            bomba.off()
            print(f"Bomba desligada! (Nível >= {gatilho_desligar}%)")

        estado["bomba_ligada"] = bomba.ligado

        # 2. Renderiza no OLED (com o IP fixo no topo)
        display.renderizar(estado["nivel"])

        # 3. Aguarda sem travar a API HTTP
        await asyncio.sleep(delay_s)

        # Simulação de alteração de nível (substituído pelo ultrassom depois)
        if estado["nivel"] <= 0:
            passo = 10
        elif estado["nivel"] >= 100:
            passo = -10

        estado["nivel"] += passo


async def main():
    # 1. Inicializa a rede com IP fixo e tela de loading
    ip = iniciar_rede()
    display.ip_display = ip

    # 2. Inicia o servidor HTTP da API REST
    servidor = ServidorAPI(cfg, estado,controlar_bomba_manual, porta=80)
    asyncio.create_task(servidor.iniciar())

    # 3. Inicia rotina de controle e display
    asyncio.create_task(loop_controle_tanque())

    print(f"Sistema pronto! Acesse a API em: http://{ip}/api/status")

    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    bomba.off()
    display.limpar()
    print("\nExecução encerrada em segurança.")
