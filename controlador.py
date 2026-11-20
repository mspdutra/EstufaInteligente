
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORTA = 1883

TOPICO_SENSORES = "estufa/sensores/+"

estados = {
    "irrigacao": "DESLIGAR",
    "ventilacao": "DESLIGAR",
    "iluminacao": "DESLIGAR"
}

def controlar(equipamento, comando, cliente):
    if estados[equipamento] != comando:
        estados[equipamento] = comando

        topico = f"estufa/atuadores/{equipamento}"
        cliente.publish(topico, comando, qos=1)

        print(f"{equipamento.upper()}: {comando}")

def ao_conectar(cliente, userdata, flags, motivo, propriedades):
    if motivo == 0:
        print("Controlador conectado ao MQTT!")
        cliente.subscribe(TOPICO_SENSORES, qos=1)
    else:
        print("Erro de conexão:", motivo)

def ao_receber(cliente, userdata, mensagem):
    try:
        dados = json.loads(mensagem.payload.decode())

        sensor = dados["sensor"]
        valor = float(dados["valor"])

        print(f"Sensor {sensor}: {valor}")

        if sensor == "temperatura":
            if valor > 30:
                controlar("ventilacao", "LIGAR", cliente)
            elif valor < 26:
                controlar("ventilacao", "DESLIGAR", cliente)

        elif sensor == "umidade":
            if valor < 30:
                controlar("irrigacao", "LIGAR", cliente)
            elif valor > 60:
                controlar("irrigacao", "DESLIGAR", cliente)

        elif sensor == "luminosidade":
            if valor < 40:
                controlar("iluminacao", "LIGAR", cliente)
            elif valor > 70:
                controlar("iluminacao", "DESLIGAR", cliente)

    except Exception as erro:
        print("Erro ao processar mensagem:", erro)

cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

cliente.on_connect = ao_conectar
cliente.on_message = ao_receber

try:
    cliente.connect(BROKER, PORTA, 60)
    print("Controlador aguardando dados dos sensores...")
    cliente.loop_forever()

except KeyboardInterrupt:
    print("\nControlador interrompido.")

except Exception as erro:
    print("Erro:", erro)

finally:
    cliente.disconnect()
