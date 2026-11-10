import json

class ConfigManager:
    # Definido dentro da própria classe para evitar problemas de escopo global no MicroPython
    CONFIG_PADRAO = {
        "IP_FIXO": "192.168.1.350",
        "SSID_ROTEADOR": "NOME_DO_SEU_WIFI",
        "SENHA_ROTEADOR": "SENHA_ROTEADOR",
        "delay_leitura_s": 15,
        "gatilho_ligar_pct": 30,
        "gatilho_desligar_pct": 100,
        "dist_sensor_cheio_cm": 20,
        "dist_sensor_vazio_cm": 120,
        "capacidade_litros": 500
    }
    ARQUIVO = "config.json"

    def __init__(self):
        self.dados = self._carregar()

    def _carregar(self):
        try:
            with open(self.ARQUIVO, "r") as f:
                return json.load(f)
        except Exception:
            # Se o arquivo não existir ou estiver corrompido, grava o padrão
            self._salvar(self.CONFIG_PADRAO)
            # Cópia manual compatível com MicroPython
            return dict(self.CONFIG_PADRAO)

    def _salvar(self, dados):
        try:
            with open(self.ARQUIVO, "w") as f:
                json.dump(dados, f)
        except Exception as e:
            print("Erro ao salvar config.json:", e)

    def obter(self, chave=None):
        if chave:
            return self.dados.get(chave, self.CONFIG_PADRAO.get(chave))
        return self.dados

    def atualizar(self, novos_dados):
        for k, v in novos_dados.items():
            if k in self.CONFIG_PADRAO:
                # Converte para o tipo correto (int, float, etc.)
                tipo = type(self.CONFIG_PADRAO[k])
                self.dados[k] = tipo(v)
        self._salvar(self.dados)
