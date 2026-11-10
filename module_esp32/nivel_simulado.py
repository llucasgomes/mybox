class NivelSimulado:
    def __init__(self, estado, passo_pct=10):
        self.estado = estado
        self.passo_pct = passo_pct

    def ler_pct(self):
        return self.estado["nivel"]

    def avancar(self, bomba_ligada):
        nivel = self.ler_pct()
        if bomba_ligada and nivel < 100:
            nivel = min(100, nivel + self.passo_pct)
        elif not bomba_ligada and nivel > 0:
            nivel = max(0, nivel - self.passo_pct)
        self.estado["nivel"] = nivel
