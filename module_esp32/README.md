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

Antes de enviar o firmware, copie `device_secrets.example.py` para
`device_secrets.py` e defina um SSID, uma senha WPA2 exclusiva (mínimo de 12 caracteres) e
uma chave aleatória para a API (mínimo de 32 caracteres). O firmware não inicia com os
valores de exemplo. Nunca
versione `device_secrets.py`.

No primeiro boot, `config_manager.py` cria `config.json` com valores padrão e a placa
inicia seu ponto de acesso protegido. Configure SSID/senha do roteador pela rota
`/api/config`; depois da resposta, o dispositivo conecta à rede mantendo o ponto de acesso
ativo. A API publica ambos os endereços em `/api/status`. Conecte o celular à mesma rede do
roteador, informe e teste `http://<IP mostrado no OLED>/api` no app e, somente após a
validação, confirme a troca para desativar o ponto de acesso.

No computador, uma chave pode ser gerada com
`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`. Use o resultado apenas no
arquivo local do dispositivo e no campo de chave do app; não o inclua em capturas, logs ou
no repositório.

O arquivo `config.json` contém credenciais e deve permanecer apenas no dispositivo, fora
do controle de versão. A senha Wi-Fi é removida das respostas da API. Todas as rotas,
exceto o preflight CORS, exigem `X-API-Key`.

## Comportamento atual

- O nível ainda é simulado em passos de 10 pontos percentuais; não há leitura ultrassônica.
- A simulação aumenta com a bomba ligada e diminui com ela desligada.
- O controle automático liga/desliga nos percentuais configurados.
- O modo manual desabilita o controle por gatilhos; a bomba só é comandada pela API.
- O modo manual é volátil: cada reinicialização volta ao modo automático.
- Ao retornar ao modo automático, os gatilhos voltam a controlar o relé.

## Limites de segurança

A chave de API é enviada por HTTP sem criptografia. Ela reduz acesso acidental, mas não
protege contra alguém capaz de observar o tráfego na rede local. Não exponha a API à
internet nem use esta solução como substituta de TLS em uma rede não confiável. CORS não é
autenticação. O ponto de acesso usa WPA2-PSK e a senha deve ser exclusiva por instalação.
O app guarda a chave no armazenamento local do navegador/dispositivo.

## Implantação e validação

Copie os módulos Python para o filesystem da placa e reinicie. Confirme o modelo exato da
placa, versão do MicroPython, numeração dos pinos e polaridade do relé antes da implantação.
O código pode ser verificado sintaticamente em um host com:

```sh
python3 -m py_compile module_esp32/*.py
```

Isso não substitui testes na placa: `machine`, `network`, OLED, Wi-Fi e o relé não são
simulados por essa validação.
