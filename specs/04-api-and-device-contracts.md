# 04. API e Integração com o Dispositivo

O cliente HTTP está centralizado em `DeviceApiService`. A URL base é fornecida pelo
ambiente e as rotas abaixo são as chamadas observadas no código.

## Rotas conhecidas

| Método | Rota | Request conhecido | Uso |
|---|---|---|---|
| `GET` | `/status` | — | Retorna `DeviceStatus` |
| `POST` | `/config` | Um ou mais campos de `DeviceConfiguration` | Atualiza configuração; modo manual é volátil |
| `POST` | `/bomba` | `{ "ligar": boolean }` | Solicita ligar/desligar bomba |
| `POST` | `/rede/confirmar` | `{ "confirmar": true }` | Desativa AP se STA estiver conectada |

A atualização de Wi-Fi chama `/config` com `SSID_ROTEADOR` e `SENHA_ROTEADOR`. A resposta
de sucesso das operações de escrita inclui os dados pertinentes, sem retornar senha Wi-Fi.
Todas as rotas, exceto o preflight `OPTIONS`, exigem o header `X-API-Key` configurado em
`device_secrets.py`.

## Exemplo de leitura tipada

```json
{
  "bomba_ligada": false,
  "nivel_atual_pct": 45,
  "configuracoes": {
    "capacidade_litros": 1000,
    "gatilho_ligar_pct": 30,
    "gatilho_desligar_pct": 100,
    "dist_sensor_cheio_cm": 20,
    "dist_sensor_vazio_cm": 120,
    "delay_leitura_s": 1,
    "SSID_ROTEADOR": "rede-configurada",
    "SENHA_ROTEADOR": "",
    "controle_manual": false
  },
  "rede": {
    "ip_ap": "192.168.4.1",
    "ip_sta": null,
    "ap_ativo": true
  }
}
```

Senhas não são retornadas pelo firmware.

## Requisitos para integrações

- Usar `/status` como fonte de verdade depois de salvar ou comandar a bomba, se a tela
  precisar confirmar o estado efetivo.
- Exibir erro ao usuário quando a conexão falhar ou a API responder com erro.
- Não presumir que um `POST` de escrita retorne o estado atualizado.
- Não enviar propriedades que não fazem parte do escopo da alteração.
- Nunca incluir senha em feedback, logs, telemetria ou snapshots de teste.
- O modo `controle_manual` só pode comandar o relé quando ativo; após reboot volta a
  automático.
- O AP WPA2 permanece ativo até `POST /rede/confirmar` autenticado, recebido enquanto STA
  está conectada.
- Manter o período de polling válido e limitado conforme requisitos acordados com o
  dispositivo.

## Lacunas do contrato

O repositório não documenta esquemas de erro, autenticação, CORS, timeout, limites do
firmware, confirmação de persistência nem garantias sobre atualizações parciais. Verifique
esses pontos com o responsável pelo backend antes de criar requisitos dependentes deles.

Neste firmware, a chave compartilhada é enviada em HTTP sem TLS; ela não impede captura
por um observador da rede local. Não expor a API à internet.
