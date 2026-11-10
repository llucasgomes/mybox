import network
import uasyncio as asyncio


class Rede:
    def __init__(self, config, display, ssid_ap, senha_ap, tentativas=20, intervalo_s=0.5):
        self.config = config
        self.display = display
        self.ssid_ap = ssid_ap
        self.senha_ap = senha_ap
        self.tentativas = tentativas
        self.intervalo_s = intervalo_s
        self.ip_ap = None
        self.ap_configurado = False
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)

    async def iniciar(self):
        self._iniciar_ponto_de_acesso()
        ip = await self._conectar_wifi()
        return ip if ip is not None else self.ip_ap

    async def reconectar(self):
        self._iniciar_ponto_de_acesso()
        ip = await self._conectar_wifi()
        if ip is not None:
            print("Wi-Fi reconectado:", ip)
            return ip
        return self.ip_ap

    async def _conectar_wifi(self):
        ssid = self.config.obter("SSID_ROTEADOR")
        senha = self.config.obter("SENHA_ROTEADOR")
        if not ssid:
            return None

        self.display.tela_loading("Conectando ao Wi-Fi", 10)
        self.wlan_sta.active(True)
        if self.wlan_sta.isconnected():
            self.wlan_sta.disconnect()
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
        if self.ap_configurado and self.wlan_ap.active():
            self.ip_ap = self.wlan_ap.ifconfig()[0]
            return self.ip_ap

        self.display.tela_loading("Iniciando ponto de acesso", 90)
        self.wlan_ap.active(True)
        self.wlan_ap.config(
            ssid=self.ssid_ap,
            key=self.senha_ap,
            security=network.AUTH_WPA2_PSK,
        )
        self.ap_configurado = True
        self.ip_ap = self.wlan_ap.ifconfig()[0]
        self.display.tela_loading("Ponto de acesso ativo", 100)
        print("Conecte-se à rede protegida", self.ssid_ap, "e acesse", self.ip_ap)
        return self.ip_ap

    def status(self):
        ip_sta = self.wlan_sta.ifconfig()[0] if self.wlan_sta.isconnected() else None
        ap_ativo = self.wlan_ap.active()
        return {
            "ip_ap": self.ip_ap if ap_ativo else None,
            "ip_sta": ip_sta,
            "ap_ativo": ap_ativo,
        }

    def confirmar_conexao_sta(self):
        if not self.wlan_sta.isconnected():
            return False
        self.wlan_ap.active(False)
        print("Conexão STA confirmada; ponto de acesso desativado.")
        return True

    def garantir_acesso_alternativo(self):
        if not self.wlan_sta.isconnected() and not self.wlan_ap.active():
            self._iniciar_ponto_de_acesso()
