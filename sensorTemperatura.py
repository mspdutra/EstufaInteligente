
import random
import time
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORTA = 1883
TOPICO = "estufa/sensores/temperatura"

cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

def medir_temperatura():
    return round(random.uniform(18, 40), 1)

try:
    cliente.connect(BROKER, PORTA, 60)
    cliente.loop_start()

    print("Sensor de temperatura conectado ao MQTT!")

    while True:
        temperatura = medir_temperatura()

        dados = {
            "sensor": "temperatura",
            "valor": temperatura,
            "unidade": "C"
        }

        mensagem = json.dumps(dados)
        resultado = cliente.publish(TOPICO, mensagem, qos=1)
        resultado.wait_for_publish()

        print(f"Temperatura enviada: {temperatura} °C")
        time.sleep(3)

except KeyboardInterrupt:
    print("\nSensor interrompido.")

except Exception as erro:
    print("Erro:", erro)

finally:
    cliente.disconnect()
    cliente.loop_stop()
