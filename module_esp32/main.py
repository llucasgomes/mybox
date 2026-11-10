import uasyncio as asyncio

from device_secrets import API_TOKEN, AP_PASSWORD, AP_SSID
from api import ServidorAPI
from config_manager import ConfigManager
from controlador_bomba import ControladorBomba
from display_agua import DisplayAgua
from nivel_simulado import NivelSimulado
from rede import Rede
from rele import Rele
from seguranca import validar_segredos


PORTA_API = 80
PIN_RELE = 13
PIN_DISPLAY_SCL = 12
PIN_DISPLAY_SDA = 14

config = ConfigManager()
validar_segredos(AP_SSID, AP_PASSWORD, API_TOKEN)
display = DisplayAgua(scl_pin=PIN_DISPLAY_SCL, sda_pin=PIN_DISPLAY_SDA)
rele_bomba = Rele(PIN_RELE)
estado = {"nivel": 100, "bomba_ligada": False}
controlador_bomba = ControladorBomba(rele_bomba, estado)
fonte_nivel = NivelSimulado(estado)
rede = Rede(config, display, AP_SSID, AP_PASSWORD)


async def supervisionar_tanque():
    while True:
        rede.garantir_acesso_alternativo()
        nivel_pct = fonte_nivel.ler_pct()
        controlador_bomba.atualizar(
            nivel_pct,
            config.obter("gatilho_ligar_pct"),
            config.obter("gatilho_desligar_pct"),
            config.obter("controle_manual"),
        )
        dados_rede = rede.status()
        display.ip_display = dados_rede["ip_sta"] or dados_rede["ip_ap"] or "0.0.0.0"
        display.renderizar(int(nivel_pct))

        await asyncio.sleep(config.obter("delay_leitura_s"))
        fonte_nivel.avancar(rele_bomba.ligado)


async def main():
    await rede.iniciar()
    display.ip_display = rede.ip_ap

    servidor = ServidorAPI(
        config,
        estado,
        controlador_bomba.comandar_manual,
        reconectar_rede=rede.reconectar,
        rede=rede,
        api_token=API_TOKEN,
        porta=PORTA_API,
    )
    asyncio.create_task(servidor.iniciar())
    asyncio.create_task(supervisionar_tanque())

    print("Sistema pronto. Acesse primeiro o ponto de acesso:", "http://" + rede.ip_ap + "/api/status")
    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    controlador_bomba.desligar()
    display.limpar()
    print("Execução encerrada em segurança.")
