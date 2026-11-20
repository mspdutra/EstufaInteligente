
import xmlrpc.client
import socket

CONTROLADORES = [
    "http://localhost:9001",
    "http://localhost:9002",
    "http://localhost:9003"
]


def chamar_controlador(metodo, *argumentos):
    for numero, endereco in enumerate(CONTROLADORES, start=1):
        try:
            print(f"Tentando controlador {numero}...")

            socket.setdefaulttimeout(3)

            servidor = xmlrpc.client.ServerProxy(
                endereco, allow_none=True
            )

            funcao = getattr(servidor, metodo)
            resultado = funcao(*argumentos)

            print(f"Controlador {numero} respondeu!")
            return resultado

        except (
            OSError,
            xmlrpc.client.Fault,
            xmlrpc.client.ProtocolError
        ):
            print(f"Controlador {numero} indisponivel.")

    return "ERRO: Nenhum controlador disponivel"
