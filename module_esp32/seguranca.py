def validar_segredos(ssid_ap, senha_ap, api_token):
    if not isinstance(ssid_ap, str) or not 1 <= len(ssid_ap) <= 32:
        raise ValueError("AP_SSID deve ter entre 1 e 32 caracteres")
    if not isinstance(senha_ap, str) or len(senha_ap) < 12 or len(senha_ap) > 63:
        raise ValueError("AP_PASSWORD deve ter entre 12 e 63 caracteres")
    if senha_ap.startswith("ALTERE_"):
        raise ValueError("configure uma senha própria para o ponto de acesso")

    validar_token_api(api_token)


def validar_token_api(api_token):
    if not isinstance(api_token, str) or len(api_token) < 32:
        raise ValueError("API_TOKEN deve ter pelo menos 32 caracteres")
    if api_token.startswith("ALTERE_"):
        raise ValueError("configure uma chave própria para a API")


def comparar_segredos(valor, esperado):
    if not isinstance(valor, str) or len(valor) != len(esperado):
        return False
    diferenca = 0
    for indice in range(len(esperado)):
        diferenca |= ord(valor[indice]) ^ ord(esperado[indice])
    return diferenca == 0
