from machine import Pin

class Rele:
    def __init__(self, pino, active_low=True):
        self.active_low = active_low
        # Inicializa desligado
        self.pin = Pin(pino, Pin.OUT, value=1 if active_low else 0)

    def on(self):
        """Aciona o relé."""
        self.pin.value(0 if self.active_low else 1)

    def off(self):
        """Desarma o relé."""
        self.pin.value(1 if self.active_low else 0)

    def toggle(self):
        """Inverte o estado atual."""
        self.pin.value(not self.pin.value())

    @property
    def ligado(self):
        return self.pin.value() == 0 if self.active_low else self.pin.value() == 1
