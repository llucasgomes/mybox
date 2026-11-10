import json


class ConfigManager:
    CONFIG_PADRAO = {
        "IP_FIXO": "192.168.1.200",
        "MASCARA": "255.255.255.0",
        "GATEWAY": "192.168.1.1",
        "DNS": "192.168.1.1",
        "NOME_AP": "ESP_Tanque",
        "SSID_ROTEADOR": "",
        "SENHA_ROTEADOR": "",
        "delay_leitura_s": 15,
        "gatilho_ligar_pct": 30,
        "gatilho_desligar_pct": 100,
        "controle_manual": False,
        "dist_sensor_cheio_cm": 20,
        "dist_sensor_vazio_cm": 120,
        "capacidade_litros": 500,
    }
    ARQUIVO = "config.json"
    LIMITES_NUMERICOS = {
        "delay_leitura_s": (1, 3600),
        "gatilho_ligar_pct": (0, 100),
        "gatilho_desligar_pct": (0, 100),
        "dist_sensor_cheio_cm": (1, 1000),
        "dist_sensor_vazio_cm": (1, 1000),
        "capacidade_litros": (1, 100000),
    }
    CAMPOS_REDE = ("IP_FIXO", "MASCARA", "GATEWAY", "DNS")
    CAMPOS_TRANSITORIOS = ("controle_manual",)

    def __init__(self):
        self.dados = self._carregar()

    def _carregar(self):
        try:
            with open(self.ARQUIVO, "r") as arquivo:
                salvos = json.load(arquivo)
        except OSError as erro:
            if erro.args and erro.args[0] == 2:
                self._salvar(dict(self.CONFIG_PADRAO))
                return dict(self.CONFIG_PADRAO)
            raise
        except ValueError as erro:
            print("config.json inválido; usando padrões sem sobrescrever o arquivo:", erro)
            return dict(self.CONFIG_PADRAO)

        if not isinstance(salvos, dict):
            print("config.json não contém um objeto; usando padrões.")
            return dict(self.CONFIG_PADRAO)

        dados = dict(self.CONFIG_PADRAO)
        for campo, valor in salvos.items():
            if campo not in self.CONFIG_PADRAO or campo in self.CAMPOS_TRANSITORIOS:
                continue
            try:
                dados[campo] = self._validar_campo(campo, valor)
            except ValueError as erro:
                print("Configuração inválida para", campo, ":", erro)
        try:
            self._validar_gatilhos(dados)
        except ValueError as erro:
            print("Gatilhos inválidos em config.json; usando padrões:", erro)
            dados["gatilho_ligar_pct"] = self.CONFIG_PADRAO["gatilho_ligar_pct"]
            dados["gatilho_desligar_pct"] = self.CONFIG_PADRAO["gatilho_desligar_pct"]
        return dados

    def _validar_campo(self, campo, valor):
        if campo in self.CAMPOS_TRANSITORIOS:
            if not isinstance(valor, bool):
                raise ValueError("deve ser true ou false")
            return valor

        if campo in self.LIMITES_NUMERICOS:
            if isinstance(valor, bool) or not isinstance(valor, int):
                raise ValueError("deve ser um número inteiro")
            minimo, maximo = self.LIMITES_NUMERICOS[campo]
            if valor < minimo or valor > maximo:
                raise ValueError("fora do intervalo permitido")
            return valor

        if not isinstance(valor, str):
            raise ValueError("deve ser texto")

        if campo == "SSID_ROTEADOR" and len(valor) > 32:
            raise ValueError("SSID deve ter no máximo 32 caracteres")
        if campo == "SENHA_ROTEADOR" and len(valor) > 63:
            raise ValueError("senha deve ter no máximo 63 caracteres")
        if campo == "NOME_AP" and not 1 <= len(valor) <= 32:
            raise ValueError("nome do ponto de acesso deve ter de 1 a 32 caracteres")
        if campo in self.CAMPOS_REDE:
            self._validar_ipv4(valor)
        return valor

    @staticmethod
    def _validar_ipv4(valor):
        partes = valor.split(".")
        if len(partes) != 4:
            raise ValueError("endereço IPv4 inválido")
        for parte in partes:
            if not parte.isdigit() or not 0 <= int(parte) <= 255:
                raise ValueError("endereço IPv4 inválido")

    @staticmethod
    def _validar_gatilhos(dados):
        if dados["gatilho_ligar_pct"] >= dados["gatilho_desligar_pct"]:
            raise ValueError("gatilho de ligar deve ser menor que o de desligar")

    def _salvar(self, dados):
        persistentes = {
            campo: valor for campo, valor in dados.items() if campo not in self.CAMPOS_TRANSITORIOS
        }
        with open(self.ARQUIVO, "w") as arquivo:
            json.dump(persistentes, arquivo)

    def obter(self, chave=None):
        if chave is not None:
            return self.dados.get(chave, self.CONFIG_PADRAO.get(chave))
        return dict(self.dados)

    def obter_publica(self):
        dados = dict(self.dados)
        dados["SENHA_ROTEADOR"] = ""
        return dados

    def atualizar(self, novos_dados):
        if not isinstance(novos_dados, dict) or not novos_dados:
            raise ValueError("envie um objeto de configuração não vazio")

        dados_atualizados = dict(self.dados)
        for campo, valor in novos_dados.items():
            if campo not in self.CONFIG_PADRAO:
                raise ValueError("campo desconhecido: " + str(campo))
            dados_atualizados[campo] = self._validar_campo(campo, valor)

        self._validar_gatilhos(dados_atualizados)
        if any(campo not in self.CAMPOS_TRANSITORIOS for campo in novos_dados):
            self._salvar(dados_atualizados)
        self.dados = dados_atualizados
        return self.obter()
