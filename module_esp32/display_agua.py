from machine import Pin, SoftI2C
import ssd1306

class DisplayAgua:
    def __init__(self, scl_pin=12, sda_pin=14, addr=0x3C):
        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c, addr=addr)
        self.ip_display = "0.0.0.0"

    def tela_loading(self, mensagem, progresso_pct):
        self.oled.fill(0)
        self.oled.text("INICIALIZANDO...", 0, 5, 1)
        self.oled.text(mensagem, 0, 22, 1)
        self.oled.rect(10, 40, 108, 12, 1)
        largura = int((progresso_pct / 100) * 104)
        if largura > 0:
            self.oled.fill_rect(12, 42, largura, 8, 1)
        self.oled.show()

    def renderizar(self, nivel):
        self.oled.fill(0)
        # IP no topo
        offset_x = max(0, (128 - (len(self.ip_display) * 8)) // 2)
        self.oled.text(self.ip_display, offset_x, 3, 1)
        self.oled.hline(0, 14, 128, 1)

        # Tanque
        self.oled.rect(5, 22, 110, 25, 1)
        self.oled.fill_rect(115, 28, 6, 13, 1)
        for i in range(10):
            if nivel >= (i + 1) * 10:
                self.oled.fill_rect(9 + i * 10, 25, 8, 19, 1)

        # Porcentagem
        self.oled.text(f"{nivel}%", 52, 53, 1)
        self.oled.show()

    def limpar(self):
        self.oled.fill(0)
        self.oled.show()
