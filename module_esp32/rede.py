import network
import uasyncio as asyncio


class Rede:
    def __init__(self, config, display, tentativas=20, intervalo_s=0.5):
        self.config = config
        self.display = display
        self.tentativas = tentativas
        self.intervalo_s = intervalo_s
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)

    async def iniciar(self):
        self.wlan_ap.active(False)
        ip = await self._conectar_wifi()
        if ip is not None:
            return ip
        return self._iniciar_ponto_de_acesso()

    async def reconectar(self):
        ip = await self._conectar_wifi()
        if ip is not None:
            self.wlan_ap.active(False)
            print("Wi-Fi reconectado:", ip)
            return ip
        return self._iniciar_ponto_de_acesso()

    async def _conectar_wifi(self):
        ssid = self.config.obter("SSID_ROTEADOR")
        senha = self.config.obter("SENHA_ROTEADOR")
        if not ssid:
            return None

        self.display.tela_loading("Conectando ao Wi-Fi", 10)
        self.wlan_sta.active(True)
        self.wlan_sta.ifconfig(
            (
                self.config.obter("IP_FIXO"),
                self.config.obter("MASCARA"),
                self.config.obter("GATEWAY"),
                self.config.obter("DNS"),
            )
        )
        self.wlan_sta.connect(ssid, senha)

        for tentativa in range(self.tentativas):
            if self.wlan_sta.isconnected():
                ip = self.wlan_sta.ifconfig()[0]
                self.display.tela_loading("Wi-Fi conectado", 100)
                return ip
            progresso = 10 + int(((tentativa + 1) / self.tentativas) * 80)
            self.display.tela_loading("Conectando...", progresso)
            await asyncio.sleep(self.intervalo_s)

        self.wlan_sta.active(False)
        return None

    def _iniciar_ponto_de_acesso(self):
        nome_ap = self.config.obter("NOME_AP")
        self.display.tela_loading("Iniciando ponto de acesso", 90)
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid=nome_ap)
        ip = self.wlan_ap.ifconfig()[0]
        self.display.tela_loading("Ponto de acesso ativo", 100)
        print("Conecte-se à rede", nome_ap, "e acesse", ip)
        return ip
