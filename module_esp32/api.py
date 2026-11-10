import uasyncio as asyncio
import json

class ServidorAPI:
    def __init__(self, config_mgr, estado_tanque, callback_bomba=None, porta=80):
        self.cfg = config_mgr
        self.estado = estado_tanque
        self.porta = porta
        self.callback_bomba = callback_bomba

    async def _enviar_resposta(self, writer, status_code, corpo_dict=None):
        try:
            if corpo_dict is not None:
                corpo = json.dumps(corpo_dict)
                dados_corpo = corpo.encode("utf-8")
                headers_conteudo = (
                    "Content-Type: application/json; charset=utf-8\r\n"
                    f"Content-Length: {len(dados_corpo)}\r\n"
                )
            else:
                corpo = ""
                dados_corpo = b""
                headers_conteudo = "Content-Length: 0\r\n"

            # Cabeçalhos completos com suporte a Private Network e CORS irrestrito
            cabecalho = (
                f"HTTP/1.1 {status_code}\r\n"
                f"{headers_conteudo}"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                "Access-Control-Allow-Headers: *\r\n"
                "Access-Control-Allow-Private-Network: true\r\n"
                "Access-Control-Max-Age: 86400\r\n"
                "Connection: close\r\n\r\n"
            )

            writer.write(cabecalho.encode("utf-8") + dados_corpo)
            await writer.drain()
        except Exception as e:
            print("Erro ao enviar resposta:", e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _ler_exato(self, reader, n_bytes):
        buffer = b""
        # Leitura com proteção contra bloqueio
        while len(buffer) < n_bytes:
            pedaco = await reader.read(n_bytes - len(buffer))
            if not pedaco:
                break
            buffer += pedaco
        return buffer

    async def _handler(self, reader, writer):
        try:
            linha_req = await reader.readline()
            if not linha_req:
                writer.close()
                await writer.wait_closed()
                return

            requisicao = linha_req.decode().strip()
            partes = requisicao.split()
            if len(partes) < 2:
                writer.close()
                await writer.wait_closed()
                return

            metodo, rota = partes[0].upper(), partes[1]

            # Consome todos os cabeçalhos até encontrar a linha em branco
            tamanho_corpo = 0
            while True:
                linha_hdr = await reader.readline()
                if not linha_hdr or linha_hdr == b"\r\n" or linha_hdr == b"\n":
                    break
                texto_hdr = linha_hdr.decode().lower()
                if "content-length:" in texto_hdr:
                    try:
                        tamanho_corpo = int(texto_hdr.split(":")[1].strip())
                    except ValueError:
                        tamanho_corpo = 0

            # 1. TRATA PRE-FLIGHT (OPTIONS)
            if metodo == "OPTIONS":
                await self._enviar_resposta(writer, "204 No Content", corpo_dict=None)
                return

            # 2. ROTA: GET /api/status
            if metodo == "GET" and rota == "/api/status":
                dados_resposta = {
                    "nivel_atual_pct": self.estado.get("nivel", 0),
                    "bomba_ligada": self.estado.get("bomba_ligada", False),
                    "configuracoes": self.cfg.obter()
                }
                await self._enviar_resposta(writer, "200 OK", dados_resposta)
                return

            # 3. TRATA MÉTODOS POST
            if metodo == "POST":
                payload = {}
                if tamanho_corpo > 0:
                    try:
                        corpo_bytes = await self._ler_exato(reader, tamanho_corpo)
                        payload = json.loads(corpo_bytes.decode("utf-8").strip())
                    except Exception as e:
                        print("Erro no parse do JSON:", e)
                        await self._enviar_resposta(writer, "400 Bad Request", {"erro": f"JSON invalido: {str(e)}"})
                        return
                else:
                    await self._enviar_resposta(writer, "400 Bad Request", {"erro": "Corpo da requisicao vazio"})
                    return

                # ROTA: POST /api/config
                if rota == "/api/config":
                    self.cfg.atualizar(payload)
                    await self._enviar_resposta(writer, "200 OK", {
                        "sucesso": True,
                        "novas_configs": self.cfg.obter()
                    })
                    return

                # ROTA: POST /api/bomba
                elif rota == "/api/bomba":
                    if "ligar" not in payload:
                        await self._enviar_resposta(writer, "400 Bad Request", {"erro": "Chave 'ligar' ausente"})
                        return

                    estado_desejado = bool(payload["ligar"])
                    self.estado["bomba_ligada"] = estado_desejado

                    if self.callback_bomba:
                        self.callback_bomba(estado_desejado)

                    await self._enviar_resposta(writer, "200 OK", {
                        "sucesso": True,
                        "mensagem": f"Bomba {'ligada' if estado_desejado else 'desligada'}",
                        "bomba_ligada": self.estado["bomba_ligada"]
                    })
                    return

            # Se não casou com nenhuma rota
            await self._enviar_resposta(writer, "404 Not Found", {"erro": "Rota nao encontrada"})

        except Exception as e:
            print("Erro critico no handler HTTP:", e)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def iniciar(self):
        await asyncio.start_server(self._handler, "0.0.0.0", self.porta)
        print(f"API REST ouvindo na porta {self.porta}")
