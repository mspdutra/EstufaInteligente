
import sys
import json
import threading
import paho.mqtt.client as mqtt

from xmlrpc.server import SimpleXMLRPCServer
from replicacao import ArmazenamentoReplica

BROKER = "localhost"
PORTA_MQTT = 1883

ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
PORTA_RPC = 9000 + ID

armazenamento = ArmazenamentoReplica(ID)
bloqueio = threading.Lock()

dados = armazenamento.carregar()

if not dados:
    dados = {
        "sensores": {},
        "equipamentos": {
            "irrigacao": "DESLIGAR",
            "ventilacao": "DESLIGAR",
            "iluminacao": "DESLIGAR"
        },
        "operacoes": {}
    }

dados.setdefault("sensores", {})
dados.setdefault("equipamentos", {})
dados.setdefault("operacoes", {})


def ao_conectar(cliente, userdata, flags, motivo, propriedades):
    if motivo == 0:
        cliente.subscribe("estufa/sensores/+", qos=1)
        print(f"Controlador {ID} conectado ao MQTT!")


def ao_receber(cliente, userdata, mensagem):
    try:
        leitura = json.loads(mensagem.payload.decode())

        sensor = leitura["sensor"]
        valor = float(leitura["valor"])

        with bloqueio:
            dados["sensores"][sensor] = valor
            armazenamento.salvar(dados)

        print(f"Controlador {ID}: {sensor} = {valor}")

    except Exception as erro:
        print("Erro ao receber leitura:", erro)


cliente_mqtt = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=f"controlador_{ID}"
)

cliente_mqtt.on_connect = ao_conectar
cliente_mqtt.on_message = ao_receber


class Controlador:

    def verificar_vida(self):
        return f"Controlador {ID} ativo"

    def consultar_estado(self):
        with bloqueio:
            return json.dumps(dados)

    def executar_comando(self, operacao_id, equipamento, comando):
        if equipamento not in (
            "irrigacao", "ventilacao", "iluminacao"
        ):
            return "EQUIPAMENTO_INVALIDO"

        if comando not in ("LIGAR", "DESLIGAR"):
            return "COMANDO_INVALIDO"

        with bloqueio:
            if operacao_id in dados["operacoes"]:
                return dados["operacoes"][operacao_id]

            topico = f"estufa/atuadores/{equipamento}"

            resultado = cliente_mqtt.publish(
                topico, comando, qos=1
            )

            try:
                resultado.wait_for_publish(timeout=5)
            except Exception:
                return "FALHA_PUBLICACAO"

            if not resultado.is_published():
                return "FALHA_PUBLICACAO"

            dados["equipamentos"][equipamento] = comando
            dados["operacoes"][operacao_id] = "SUCESSO"

            armazenamento.salvar(dados)

            print(
                f"Controlador {ID}: "
                f"{equipamento} -> {comando}"
            )

            return "SUCESSO"


try:
    cliente_mqtt.connect(BROKER, PORTA_MQTT, 60)
    cliente_mqtt.loop_start()

    servidor = SimpleXMLRPCServer(
        ("localhost", PORTA_RPC),
        allow_none=True,
        logRequests=False
    )

    servidor.register_instance(Controlador())

    print(f"Controlador {ID} iniciado!")
    print(f"Porta XML-RPC: {PORTA_RPC}")

    servidor.serve_forever()

except KeyboardInterrupt:
    print("\nControlador encerrado.")

except Exception as erro:
    print("Erro:", erro)

finally:
    cliente_mqtt.disconnect()
    cliente_mqtt.loop_stop()
