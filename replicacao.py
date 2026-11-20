
import json
import os
import tempfile
import threading

class ArmazenamentoReplica:

    def __init__(self, identificador):
        self.identificador = identificador
        self.arquivo = f"dados_controlador_{identificador}.json"
        self.bloqueio = threading.Lock()

    def salvar(self, dados):
        with self.bloqueio:
            pasta = os.path.dirname(
                os.path.abspath(self.arquivo)
            )

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=pasta,
                delete=False
            ) as temporario:
                json.dump(dados, temporario, indent=4)
                caminho_temporario = temporario.name

            os.replace(caminho_temporario, self.arquivo)

    def carregar(self):
        with self.bloqueio:
            if not os.path.exists(self.arquivo):
                return {}

            with open(
                self.arquivo,
                "r",
                encoding="utf-8"
            ) as arquivo:
                return json.load(arquivo)
