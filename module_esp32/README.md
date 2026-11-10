# Firmware MicroPython do reservatório

Firmware do dispositivo que serve a API local, controla o relé e mostra o nível no OLED.
Os módulos continuam na raiz para manter simples o carregamento de imports no MicroPython.

## Mapa dos módulos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Compor módulos e iniciar as tarefas |
| `rede.py` | Conectar ao Wi-Fi ou iniciar o ponto de acesso de contingência |
| `api.py` | Atender `/api/status`, `/api/config` e `/api/bomba` |
| `config_manager.py` | Validar e persistir `config.json` |
| `controlador_bomba.py` | Aplicar comandos manuais e gatilhos automáticos |
| `nivel_simulado.py` | Fornecer nível temporário simulado |
| `rele.py` | Controlar o pino físico do relé |
| `display_agua.py` | Renderizar informações no OLED |
| `ssd1306.py` | Driver do controlador OLED SSD1306 |
| `boot.py` | Inicialização MicroPython (reservado; sem lógica duplicada) |

## Configuração inicial

No primeiro boot, `config_manager.py` cria `config.json` com valores padrão. Configure
SSID/senha pela rota `/api/config`; depois da resposta, o dispositivo tenta reconectar.
Se a conexão não estiver configurada ou falhar, ele inicia a rede aberta `ESP_Tanque`.
O IP de contingência depende da configuração de rede do próprio firmware.

O arquivo `config.json` contém credenciais e deve permanecer apenas no dispositivo, fora
do controle de versão. A senha Wi-Fi é removida da resposta de `/api/status`.

## Comportamento atual

- O nível ainda é simulado em passos de 10 pontos percentuais; não há leitura ultrassônica.
- A simulação aumenta com a bomba ligada e diminui com ela desligada.
- O controle automático liga/desliga nos percentuais configurados.
- O comando manual altera diretamente o relé. Na próxima avaliação, os gatilhos automáticos
  continuam valendo; por isso, um comando pode ser revertido se o nível já estiver além do
  respectivo limite.
- No ponto de acesso aberto, não há autenticação na API. Use somente em ambiente confiável
  e defina uma política de senha/autorização antes de expor o dispositivo a outras redes.

## Implantação e validação

Copie os módulos Python para o filesystem da placa e reinicie. Confirme o modelo exato da
placa, versão do MicroPython, numeração dos pinos e polaridade do relé antes da implantação.
O código pode ser verificado sintaticamente em um host com:

```sh
python3 -m py_compile module_esp32/*.py
```

Isso não substitui testes na placa: `machine`, `network`, OLED, Wi-Fi e o relé não são
simulados por essa validação.
