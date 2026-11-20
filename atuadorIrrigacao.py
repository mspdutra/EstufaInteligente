
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORTA = 1883
TOPICO = "estufa/atuadores/irrigacao"

def ao_conectar(cliente, userdata, flags, motivo, propriedades):
    if motivo == 0:
        print("Atuador de irrigação conectado ao MQTT!")
        cliente.subscribe(TOPICO, qos=1)
    else:
        print("Falha na conexão:", motivo)

def ao_receber(cliente, userdata, mensagem):
    comando = mensagem.payload.decode().strip().upper()

    if comando == "LIGAR":
        print("IRRIGAÇÃO LIGADA")
    elif comando == "DESLIGAR":
        print("IRRIGAÇÃO DESLIGADA")
    else:
        print("Comando desconhecido:", comando)

cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

cliente.on_connect = ao_conectar
cliente.on_message = ao_receber

try:
    cliente.connect(BROKER, PORTA, 60)
    print("Aguardando comandos de irrigação...")
    cliente.loop_forever()

except KeyboardInterrupt:
    print("\nAtuador interrompido.")

except Exception as erro:
    print("Erro:", erro)

finally:
    cliente.disconnect()
