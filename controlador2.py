
import json
import threading
import paho.mqtt.client as mqtt
from xmlrpc.server import SimpleXMLRPCServer
from banco import criar_bancos, salvar_sensor, salvar_equipamento, carregar_equipamentos

ID = 2
PORTA = 9002

criar_bancos()

sensores = {}
equipamentos = {
    "irrigacao": "DESLIGAR",
    "ventilacao": "DESLIGAR",
    "iluminacao": "DESLIGAR"
}
equipamentos.update(carregar_equipamentos())
operacoes = {}
bloqueio = threading.RLock()

cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=f"controlador_{ID}"
)


def mudar_equipamento(nome, comando):
    if equipamentos[nome] != comando:
        resultado = cliente.publish(
            f"estufa/atuadores/{nome}",
            comando,
            qos=1
        )

        resultado.wait_for_publish(timeout=5)

        if not resultado.is_published():
            return False

        equipamentos[nome] = comando
        salvar_equipamento(nome, comando)

        cliente.publish(
            "estufa/sincronizacao",
            json.dumps({
                "origem": ID,
                "equipamento": nome,
                "comando": comando
            }),
            qos=1
        )

        print(f"{nome}: {comando}")

    return True


def ao_conectar(cliente, userdata, flags, motivo, propriedades):
    if motivo == 0:
        print(f"Controlador {ID} conectado ao MQTT!")

        cliente.subscribe("estufa/sensores/+", qos=1)
        cliente.subscribe("estufa/sincronizacao", qos=1)

    else:
        print("Erro de conexao:", motivo)


def ao_receber(cliente, userdata, mensagem):
    try:
        dados = json.loads(mensagem.payload.decode())

        if mensagem.topic == "estufa/sincronizacao":
            if dados["origem"] == ID:
                return

            nome = dados["equipamento"]
            comando = dados["comando"]

            if nome not in equipamentos:
                return

            if comando not in ("LIGAR", "DESLIGAR"):
                return

            with bloqueio:
                equipamentos[nome] = comando
                salvar_equipamento(nome, comando)

            print(
                f"Controlador {ID} sincronizado: "
                f"{nome} = {comando}"
            )
            return

        nome = dados["sensor"]
        valor = float(dados["valor"])

        with bloqueio:
            sensores[nome] = valor
            salvar_sensor(nome, valor)

            print(f"Controlador {ID}: {nome} = {valor}")

            if nome == "temperatura":
                if valor > 30:
                    mudar_equipamento("ventilacao", "LIGAR")
                elif valor < 26:
                    mudar_equipamento("ventilacao", "DESLIGAR")

            elif nome == "umidade":
                if valor < 30:
                    mudar_equipamento("irrigacao", "LIGAR")
                elif valor > 60:
                    mudar_equipamento("irrigacao", "DESLIGAR")

            elif nome == "luminosidade":
                if valor < 40:
                    mudar_equipamento("iluminacao", "LIGAR")
                elif valor > 70:
                    mudar_equipamento("iluminacao", "DESLIGAR")

    except Exception as erro:
        print("Erro:", erro)


class Controlador:

    def verificar_vida(self):
        return f"Controlador {ID} funcionando"

    def consultar_estado(self):
        with bloqueio:
            return json.dumps({
                "controlador": ID,
                "sensores": sensores,
                "equipamentos": equipamentos
            })

    def executar_comando(self, operacao_id, equipamento, comando):
        if equipamento not in equipamentos:
            return "EQUIPAMENTO_INVALIDO"

        if comando not in ("LIGAR", "DESLIGAR"):
            return "COMANDO_INVALIDO"

        with bloqueio:
            if operacao_id in operacoes:
                return operacoes[operacao_id]

            if mudar_equipamento(equipamento, comando):
                operacoes[operacao_id] = "SUCESSO"
                return "SUCESSO"

            return "FALHA_PUBLICACAO"


cliente.on_connect = ao_conectar
cliente.on_message = ao_receber

try:
    cliente.connect("localhost", 1883, 60)
    cliente.loop_start()

    servidor = SimpleXMLRPCServer(
        ("localhost", PORTA),
        allow_none=True,
        logRequests=False
    )

    servidor.register_instance(Controlador())

    print(f"Controlador {ID} iniciado na porta {PORTA}")

    servidor.serve_forever()

except KeyboardInterrupt:
    print("Controlador encerrado.")

except Exception as erro:
    print("Erro:", erro)

finally:
    cliente.disconnect()
    cliente.loop_stop()
