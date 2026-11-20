
import random
import time
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORTA = 1883
TOPICO = "estufa/sensores/umidade"

cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

def medir_umidade():
    return round(random.uniform(10, 90), 1)

try:
    cliente.connect(BROKER, PORTA, 60)
    cliente.loop_start()

    print("Sensor de umidade conectado ao MQTT!")

    while True:
        umidade = medir_umidade()

        dados = {
            "sensor": "umidade",
            "valor": umidade,
            "unidade": "%"
        }

        mensagem = json.dumps(dados)
        resultado = cliente.publish(TOPICO, mensagem, qos=1)
        resultado.wait_for_publish()

        print(f"Umidade enviada: {umidade}%")
        time.sleep(3)

except KeyboardInterrupt:
    print("\nSensor interrompido.")

except Exception as erro:
    print("Erro:", erro)

finally:
    cliente.disconnect()
    cliente.loop_stop()
