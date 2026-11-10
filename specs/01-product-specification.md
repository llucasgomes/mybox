# 01. Especificação de Produto — Mybox

## Visão geral

O Mybox é um aplicativo web/mobile de supervisão de um reservatório conectado a um
dispositivo. A interface consulta o status do dispositivo, apresenta o nível e a
capacidade da caixa e permite configurar parâmetros, rede Wi-Fi e comando da bomba.

## Usuários e necessidades

- **Operador:** precisa ver o nível/capacidade atuais e o estado da bomba.
- **Responsável pela instalação:** precisa definir a capacidade e os parâmetros do sensor
  e da bomba.
- **Operador da rede:** precisa informar as credenciais Wi-Fi do dispositivo sem que o
  aplicativo tente revelar credenciais previamente armazenadas.

## Comportamentos funcionais existentes

### Supervisão (`/home`)

- Consulta `GET /status` ao abrir a tela.
- Apresenta o nível atual em percentual, estado da bomba e capacidade recebidos do
  dispositivo; volume em litros é calculado pelo nível vezes a capacidade.
- Atualiza novamente de acordo com `delay_leitura_s`, com intervalo de contingência após
  falha de consulta.
- Apresenta alertas de nível baixo e de nível próximo ao máximo.
- Envia comandos de ligar/desligar bomba pela rota documentada em
  [API e integração](./04-api-and-device-contracts.md).
- O comando manual só fica disponível quando o dispositivo confirma o modo manual.
- Exibe o endereço do ponto de acesso e o endereço STA informados pelo dispositivo.

### Configuração (`/config`)

- Carrega os valores atuais a partir de `GET /status`.
- Permite selecionar a capacidade da caixa em litros e salvá-la no dispositivo.
- Permite salvar individualmente os gatilhos percentuais e parâmetros do sensor.
- Permite enviar SSID e senha Wi-Fi juntos.
- Permite testar e salvar localmente um endereço de API e a chave do dispositivo.
- Permite confirmar a transição de rede pelo endereço STA testado.
- Permite alternar entre controle automático e manual; a seleção manual é volátil e volta
  para automática após reiniciar o firmware.
- Exibe feedback de sucesso/erro e validação dos campos.

## Regras de negócio conhecidas

- O nível é percentual e deve estar entre 0 e 100.
- O volume exibido é derivado: `capacidade_litros * nivel_atual_pct / 100`.
- A capacidade exibida deve refletir o valor persistido/retornado pela API, não apenas uma
  seleção temporária da interface.
- O intervalo de atualização vem de `delay_leitura_s`; valores inválidos devem usar um
  intervalo de contingência seguro.
- A bomba não deve aparentar ter mudado de estado antes de a API confirmar o comando e o
  status ser atualizado.
- No modo manual, o controle automático não pode reverter o comando da bomba.
- O ponto de acesso permanece ativo durante a transição para STA e só é desligado após
  confirmação autenticada feita pelo endereço STA.

## Fora do escopo confirmado

Não presumir histórico, cadastro de múltiplos dispositivos, controle manual de drenagem,
funcionamento offline ou regras autônomas de acionamento. Especificar esses comportamentos
somente após decisão de produto e confirmação do backend/firmware.

## Critérios de aceite para mudanças de produto

Cada feature deve incluir critérios observáveis para sucesso, falha de rede, carregamento,
valores ausentes ou inválidos e acessibilidade de controles. Registrar decisões em
especificações específicas antes de tratá-las como requisitos implementados.
