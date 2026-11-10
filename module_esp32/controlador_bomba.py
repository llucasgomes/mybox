class ControladorBomba:
    def __init__(self, rele, estado):
        self.rele = rele
        self.estado = estado
        self._sincronizar_estado()

    def comandar_manual(self, ligar):
        self._aplicar_estado(ligar)
        print("[MANUAL] Bomba", "ligada" if ligar else "desligada")

    def atualizar(self, nivel_pct, gatilho_ligar_pct, gatilho_desligar_pct, controle_manual=False):
        if controle_manual:
            self._sincronizar_estado()
            return

        if nivel_pct <= gatilho_ligar_pct and not self.rele.ligado:
            self._aplicar_estado(True)
            print("Bomba acionada: nível abaixo do gatilho de ligar.")
        elif nivel_pct >= gatilho_desligar_pct and self.rele.ligado:
            self._aplicar_estado(False)
            print("Bomba desligada: nível atingiu o gatilho de desligar.")
        else:
            self._sincronizar_estado()

    def desligar(self):
        self.rele.off()
        self._sincronizar_estado()

    def _aplicar_estado(self, ligar):
        if ligar:
            self.rele.on()
        else:
            self.rele.off()
        self._sincronizar_estado()

    def _sincronizar_estado(self):
        self.estado["bomba_ligada"] = self.rele.ligado
