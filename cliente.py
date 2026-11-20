
import uuid
import json
from middleware import chamar_controlador

print("=== ESTUFA AGRICOLA INTELIGENTE ===")

while True:
    print("\n1 - Consultar estado da estufa")
    print("2 - Ligar equipamento")
    print("3 - Desligar equipamento")
    print("0 - Sair")

    opcao = input("Escolha uma opcao: ")

    if opcao == "1":
        resultado = chamar_controlador("consultar_estado")

        try:
            estado = json.loads(resultado)
            print("\nControlador:", estado["controlador"])
            print("Sensores:", estado["sensores"])
            print("Equipamentos:", estado["equipamentos"])
        except (ValueError, KeyError, TypeError):
            print(resultado)

    elif opcao in ("2", "3"):
        equipamento = input(
            "Equipamento (irrigacao, ventilacao, iluminacao): "
        ).strip().lower()

        comando = "LIGAR" if opcao == "2" else "DESLIGAR"

        operacao_id = str(uuid.uuid4())

        resultado = chamar_controlador(
            "executar_comando",
            operacao_id,
            equipamento,
            comando
        )

        print("Resultado:", resultado)

    elif opcao == "0":
        print("Cliente encerrado.")
        break

    else:
        print("Opcao invalida.")
