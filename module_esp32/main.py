import uasyncio as asyncio

from api import ServidorAPI
from config_manager import ConfigManager
from controlador_bomba import ControladorBomba
from display_agua import DisplayAgua
from nivel_simulado import NivelSimulado
from rede import Rede
from rele import Rele


PORTA_API = 80
PIN_RELE = 13
PIN_DISPLAY_SCL = 12
PIN_DISPLAY_SDA = 14

config = ConfigManager()
display = DisplayAgua(scl_pin=PIN_DISPLAY_SCL, sda_pin=PIN_DISPLAY_SDA)
rele_bomba = Rele(PIN_RELE)
estado = {"nivel": 100, "bomba_ligada": False}
controlador_bomba = ControladorBomba(rele_bomba, estado)
fonte_nivel = NivelSimulado(estado)
rede = Rede(config, display)


async def supervisionar_tanque():
    while True:
        nivel_pct = fonte_nivel.ler_pct()
        controlador_bomba.atualizar_automaticamente(
            nivel_pct,
            config.obter("gatilho_ligar_pct"),
            config.obter("gatilho_desligar_pct"),
        )
        display.renderizar(int(nivel_pct))

        await asyncio.sleep(config.obter("delay_leitura_s"))
        fonte_nivel.avancar(rele_bomba.ligado)


async def main():
    ip = await rede.iniciar()
    display.ip_display = ip

    servidor = ServidorAPI(
        config,
        estado,
        controlador_bomba.comandar_manual,
        reconectar_rede=rede.reconectar,
        porta=PORTA_API,
    )
    asyncio.create_task(servidor.iniciar())
    asyncio.create_task(supervisionar_tanque())

    print("Sistema pronto. API:", "http://" + ip + "/api/status")
    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    controlador_bomba.desligar()
    display.limpar()
    print("Execução encerrada em segurança.")
