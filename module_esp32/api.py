import json
import uasyncio as asyncio

from seguranca import comparar_segredos, validar_token_api


class ServidorAPI:
    MAX_CORPO_BYTES = 2048

    def __init__(
        self,
        config,
        estado,
        callback_bomba=None,
        reconectar_rede=None,
        rede=None,
        api_token=None,
        porta=80,
    ):
        self.cfg = config
        self.estado = estado
        self.porta = porta
        self.callback_bomba = callback_bomba
        self.reconectar_rede = reconectar_rede
        validar_token_api(api_token)
        self.api_token = api_token
        self.rede = rede

    async def _enviar_resposta(self, writer, status, corpo=None):
        if corpo is None:
            dados_corpo = b""
            headers_conteudo = "Content-Length: 0\r\n"
        else:
            dados_corpo = json.dumps(corpo).encode("utf-8")
            headers_conteudo = (
                "Content-Type: application/json; charset=utf-8\r\n"
                "Content-Length: {}\r\n".format(len(dados_corpo))
            )

        cabecalho = (
            "HTTP/1.1 {}\r\n".format(status)
            + headers_conteudo
            + "Access-Control-Allow-Origin: *\r\n"
            + "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            + "Access-Control-Allow-Headers: Content-Type, X-API-Key\r\n"
            + "Access-Control-Allow-Private-Network: true\r\n"
            + "Access-Control-Max-Age: 86400\r\n"
            + "Connection: close\r\n\r\n"
        )

        try:
            writer.write(cabecalho.encode("utf-8") + dados_corpo)
            await writer.drain()
        except OSError as erro:
            print("Falha ao enviar resposta HTTP:", erro)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _ler_corpo(self, reader, tamanho):
        partes = []
        restante = tamanho
        while restante:
            parte = await reader.read(restante)
            if not parte:
                raise ValueError("corpo da requisição incompleto")
            partes.append(parte)
            restante -= len(parte)
        return b"".join(partes)

    async def _handler(self, reader, writer):
        try:
            linha = await reader.readline()
            partes = linha.decode("utf-8").strip().split()
            if len(partes) != 3:
                await self._enviar_resposta(writer, "400 Bad Request", {"erro": "Linha HTTP inválida"})
                return

            metodo, rota = partes[0].upper(), partes[1]
            tamanho_corpo = 0
            api_token = None
            while True:
                linha_header = await reader.readline()
                if not linha_header or linha_header in (b"\r\n", b"\n"):
                    break
                texto_header = linha_header.decode("utf-8").strip()
                if ":" not in texto_header:
                    continue
                nome, valor = texto_header.split(":", 1)
                if nome.lower() == "content-length":
                    try:
                        tamanho_corpo = int(valor.strip())
                    except ValueError:
                        await self._enviar_resposta(
                            writer, "400 Bad Request", {"erro": "Content-Length inválido"}
                        )
                        return
                elif nome.lower() == "x-api-key":
                    api_token = valor.strip()

            if metodo == "OPTIONS":
                await self._enviar_resposta(writer, "204 No Content")
                return

            if not comparar_segredos(api_token, self.api_token):
                await self._enviar_resposta(writer, "401 Unauthorized", {"erro": "Chave de API inválida"})
                return

            if metodo == "GET" and rota == "/api/status":
                dados = {
                    "nivel_atual_pct": self.estado.get("nivel", 0),
                    "bomba_ligada": self.estado.get("bomba_ligada", False),
                    "configuracoes": self.cfg.obter_publica(),
                }
                if self.rede is not None:
                    dados["rede"] = self.rede.status()
                await self._enviar_resposta(writer, "200 OK", dados)
                return

            if metodo != "POST" or rota not in (
                "/api/config",
                "/api/bomba",
                "/api/rede/confirmar",
            ):
                await self._enviar_resposta(writer, "404 Not Found", {"erro": "Rota não encontrada"})
                return

            if tamanho_corpo <= 0:
                await self._enviar_resposta(writer, "400 Bad Request", {"erro": "Corpo da requisição vazio"})
                return
            if tamanho_corpo > self.MAX_CORPO_BYTES:
                await self._enviar_resposta(writer, "413 Payload Too Large", {"erro": "Corpo muito grande"})
                return

            try:
                corpo = await self._ler_corpo(reader, tamanho_corpo)
                payload = json.loads(corpo.decode("utf-8"))
            except (ValueError, UnicodeError) as erro:
                await self._enviar_resposta(writer, "400 Bad Request", {"erro": "JSON inválido: " + str(erro)})
                return

            if not isinstance(payload, dict):
                await self._enviar_resposta(writer, "400 Bad Request", {"erro": "O JSON deve ser um objeto"})
                return

            if rota == "/api/config":
                await self._atualizar_configuracao(writer, payload)
                return

            if rota == "/api/rede/confirmar":
                await self._confirmar_rede(writer, payload)
                return

            await self._acionar_bomba(writer, payload)
        except Exception as erro:
            print("Erro ao processar requisição HTTP:", erro)
            try:
                await self._enviar_resposta(writer, "500 Internal Server Error", {"erro": "Erro interno"})
            except Exception as erro_resposta:
                print("Falha ao responder erro HTTP:", erro_resposta)

    async def _atualizar_configuracao(self, writer, payload):
        alterou_wifi = "SSID_ROTEADOR" in payload or "SENHA_ROTEADOR" in payload
        try:
            self.cfg.atualizar(payload)
            configuracoes = self.cfg.obter_publica()
        except ValueError as erro:
            await self._enviar_resposta(writer, "400 Bad Request", {"erro": str(erro)})
            return
        except OSError as erro:
            print("Falha ao persistir configuração:", erro)
            await self._enviar_resposta(
                writer, "500 Internal Server Error", {"erro": "Não foi possível salvar a configuração"}
            )
            return

        await self._enviar_resposta(
            writer,
            "200 OK",
            {"sucesso": True, "novas_configs": configuracoes},
        )
        if alterou_wifi and self.reconectar_rede is not None:
            asyncio.create_task(self._reconectar_depois_da_resposta())

    async def _reconectar_depois_da_resposta(self):
        await asyncio.sleep(1)
        try:
            await self.reconectar_rede()
        except Exception as erro:
            print("Falha ao reconectar à rede após atualizar Wi-Fi:", erro)

    async def _acionar_bomba(self, writer, payload):
        if not self.cfg.obter("controle_manual"):
            await self._enviar_resposta(
                writer,
                "409 Conflict",
                {"erro": "Acionamento manual indisponível no modo automático"},
            )
            return

        if "ligar" not in payload or not isinstance(payload["ligar"], bool):
            await self._enviar_resposta(
                writer, "400 Bad Request", {"erro": "O campo 'ligar' deve ser true ou false"}
            )
            return

        ligar = payload["ligar"]
        try:
            if self.callback_bomba is not None:
                self.callback_bomba(ligar)
            else:
                self.estado["bomba_ligada"] = ligar
        except Exception as erro:
            print("Falha ao acionar a bomba:", erro)
            await self._enviar_resposta(
                writer, "500 Internal Server Error", {"erro": "Não foi possível acionar a bomba"}
            )
            return

        await self._enviar_resposta(
            writer,
            "200 OK",
            {
                "sucesso": True,
                "mensagem": "Bomba ligada" if ligar else "Bomba desligada",
                "bomba_ligada": self.estado.get("bomba_ligada", ligar),
            },
        )

    async def _confirmar_rede(self, writer, payload):
        if payload.get("confirmar") is not True or len(payload) != 1 or self.rede is None:
            await self._enviar_resposta(
                writer, "400 Bad Request", {"erro": "Confirmação de rede inválida"}
            )
            return

        if not self.rede.confirmar_conexao_sta():
            await self._enviar_resposta(
                writer,
                "409 Conflict",
                {"erro": "Conecte-se ao IP do Wi-Fi do roteador antes de confirmar"},
            )
            return

        await self._enviar_resposta(writer, "200 OK", {"sucesso": True, "ap_ativo": False})

    async def iniciar(self):
        await asyncio.start_server(self._handler, "0.0.0.0", self.porta)
        print("API REST ouvindo na porta", self.porta)
