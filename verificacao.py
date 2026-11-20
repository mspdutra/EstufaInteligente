
import json
import xmlrpc.client

PORTAS = [9001, 9002, 9003]


def verificar_controladores():
    respostas = []

    for numero, porta in enumerate(PORTAS, start=1):
        try:
            servidor = xmlrpc.client.ServerProxy(
                f"http://localhost:{porta}"
            )

            estado = json.loads(servidor.consultar_estado())

            respostas.append({
                "controlador": numero,
                "equipamentos": estado["equipamentos"]
            })

            print(f"Controlador {numero}: {estado['equipamentos']}")

        except Exception:
            print(f"Controlador {numero} nao respondeu.")

    if len(respostas) < 3:
        print("Nao foi possivel comparar os tres controladores.")
        return

    valores = [
        json.dumps(r["equipamentos"], sort_keys=True)
        for r in respostas
    ]

    if valores[0] == valores[1] == valores[2]:
        print("Todos os controladores concordam.")
    else:
        print("ALERTA: Existem respostas diferentes!")

        for i in range(3):
            outros = [
                valores[j] for j in range(3) if j != i
            ]

            if outros[0] == outros[1] != valores[i]:
                print(
                    f"Controlador {respostas[i]['controlador']} "
                    "apresentou resposta divergente."
                )
                break


verificar_controladores()
