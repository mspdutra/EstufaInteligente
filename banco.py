
import sqlite3

def conectar(numero):
    return sqlite3.connect(f"banco{numero}.db")

def criar_bancos():
    for numero in [1, 2]:
        conexao = conectar(numero)
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensores (
                nome TEXT PRIMARY KEY,
                valor REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipamentos (
                nome TEXT PRIMARY KEY,
                estado TEXT
            )
        """)

        conexao.commit()
        conexao.close()


def salvar_sensor(nome, valor):
    for numero in [1, 2]:
        conexao = conectar(numero)
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO sensores (nome, valor)
            VALUES (?, ?)
        """, (nome, valor))

        conexao.commit()
        conexao.close()


def salvar_equipamento(nome, estado):
    for numero in [1, 2]:
        conexao = conectar(numero)
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO equipamentos (nome, estado)
            VALUES (?, ?)
        """, (nome, estado))

        conexao.commit()
        conexao.close()


def carregar_equipamentos():
    conexao = conectar(1)
    cursor = conexao.cursor()

    cursor.execute("SELECT nome, estado FROM equipamentos")
    registros = cursor.fetchall()

    conexao.close()

    return dict(registros)



