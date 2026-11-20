
import random
import time
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORTA = 1883
TOPICO = "estufa/sensores/luminosidade"

cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

def medir_luminosidade():
    return round(random.uniform(0, 100), 1)

try:
    cliente.connect(BROKER, PORTA, 60)
    cliente.loop_start()

    print("Sensor de luminosidade conectado ao MQTT!")

    while True:
        luminosidade = medir_luminosidade()

        dados = {
            "sensor": "luminosidade",
            "valor": luminosidade,
            "unidade": "%"
        }

        mensagem = json.dumps(dados)
        resultado = cliente.publish(TOPICO, mensagem, qos=1)
        resultado.wait_for_publish()

        print(f"Luminosidade enviada: {luminosidade}%")
        time.sleep(3)

except KeyboardInterrupt:
    print("\nSensor interrompido.")

except Exception as erro:
    print("Erro:", erro)

finally:
    cliente.disconnect()
    cliente.loop_stop()
