# Digitar (Aqui)

# Texto especial para usar no projeto (abaixo)
# 𝕊𝕒𝕓𝕠𝕣 𝕖𝕩𝕡𝕣𝕖𝕤𝕤

# Sabor Express - Versão Orientada a Objetos
# Sistema de cadastro e gerenciamento de restaurantes

import os
import sqlite3

# Classe que representa um único restaurante cadastrado no sistema.
# Cada objeto dessa classe guarda seus próprios dados
# (nome, categoria, ativo).

class Restaurante:

    # Construtor: roda automaticamente quando um novo Restaurante é criado.
    # Recebe nome e categoria, e já define ativo como False por padrão.

    def __init__(self, nome, categoria):
        self.nome = nome
        self.categoria = categoria
        self.ativo = False  # Todos os restaurantes começam inativos

    # Método que inverte o estado do restaurante (ativo <-> inativo).
    # Não recebe parâmetros além de self porque só mexe nos próprios dados.

    def alternar_estado(self):
        self.ativo = not self.ativo

    # Método especial: define como o objeto aparece quando usado em
    # print(restaurante) ou dentro de uma f-string.

    def __str__(self):
        status = "ativado" if self.ativo else "desativado"
        return f"-{self.nome.ljust(20)} | {self.categoria.ljust(20)} | {status}"


# Classe principal do sistema.
# Guarda a lista de restaurantes e concentra as regras de negócio:
# cadastrar, buscar e listar.

class SaborExpress:

    # Construtor: cria a lista de restaurantes já com alguns itens iniciais.

    def __init__(self, caminho_banco="restaurantes.db"):
        self.caminho_banco = caminho_banco
        self.inicializar_banco()

    # Cria a tabela restaurantes caso ainda não exista, e popula com
    # dados iniciais apenas na primeira execução (tabela vazia).
    def inicializar_banco(self):
        conn = sqlite3.connect(self.caminho_banco)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS restaurantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                ativo BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )

        # Só insere os dados iniciais se a tabela ainda estiver vazia,
        # para não duplicar restaurantes a cada vez que o programa roda
        cursor.execute("SELECT COUNT(*) FROM restaurantes")
        total = cursor.fetchone()[0]

        if total == 0:
            restaurantes_iniciais = [
                ("Praça", "Japonesa", False),
                ("Pizza Suprema", "Pizza", True),
                ("Cantina", "Italiano", False),
            ]
            cursor.executemany(
                "INSERT INTO restaurantes (nome, categoria, ativo) VALUES (?, ?, ?)",
                restaurantes_iniciais,
            )

        conn.commit()
        conn.close()

    # Cria um novo objeto Restaurante e adiciona na lista interna.

    def cadastrar_restaurante(self, nome, categoria):
        try:
            conn = sqlite3.connect(self.caminho_banco)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO restaurantes (nome, categoria, ativo) VALUES (?, ?, ?)",
                (nome, categoria, False),
            )

            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as erro:
            print(f"Erro ao cadastrar restaurante: {erro}")
            return False

    # Percorre a lista de restaurantes cadastrados.
    # Retorna o objeto restaurante se achar, ou None se não encontrar.

    def buscar_estado(self, nome):
        conn = sqlite3.connect(self.caminho_banco)
        cursor = conn.cursor()

        cursor.execute("SELECT ativo FROM restaurantes WHERE nome = ?", (nome,))
        resultado = cursor.fetchone()

        conn.close()

    # fetchone() retorna uma tupla como (0,) ou (1,) — pegamos só o valor
        return resultado[0] if resultado is not None else None

    # Inverte o estado (ativo <-> inativo) de um restaurante.
    # Retorna o novo estado (True/False) se encontrou, ou None se não existir.
    def alternar_estado(self, nome):
        estado_atual = self.buscar_estado(nome)

        if estado_atual is None:
            return None

        novo_estado = not estado_atual

        conn = sqlite3.connect(self.caminho_banco)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE restaurantes SET ativo = ? WHERE nome = ?", (novo_estado, nome)
        )

        conn.commit()
        conn.close()

        return novo_estado


    def listar_restaurantes(self):
        conn = sqlite3.connect(self.caminho_banco)
        cursor = conn.cursor()

        cursor.execute("SELECT nome, categoria, ativo FROM restaurantes ORDER BY nome")
        restaurantes = cursor.fetchall()

        conn.close()
        return restaurantes


    # Verifica se um restaurante existe pelo nome.
    # Retorna True/False — usado antes de pedir confirmação de exclusão.
    def restaurante_existe(self, nome):
        conn = sqlite3.connect(self.caminho_banco)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM restaurantes WHERE nome = ?", (nome,))
        resultado = cursor.fetchone()

        conn.close()
        return resultado is not None

    # Remove um restaurante do banco pelo nome.
    def excluir_restaurante(self, nome):
        conn = sqlite3.connect(self.caminho_banco)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM restaurantes WHERE nome = ?", (nome,))

        conn.commit()
        conn.close()
    
# Classe responsável por toda a interação com o usuário: exibir textos
# ler as opções digitadas e chamar os métodos do SaborExpress.

class Menu:

    # Construtor: cria um SaborExpress para o Menu poder operar sobre ele.

    def __init__(self):
        self.app = SaborExpress()

    # ---------- Métodos de exibição ----------

    # Limpa a tela e mostra um subtítulo formatado com asteriscos em volta.

    def exibir_subtitulo(self, texto):
        os.system("cls")  # Limpa a tela no Windows
        linha = "*" * len(texto)
        print(linha)
        print(texto)
        print(linha)
        print()

    # Mostra o nome estilizado do programa na tela.
    def exibir_nome_do_programa(self):
        print(
            """
        𝕊𝕒𝕓𝕠𝕣 𝕖𝕩𝕡𝕣𝕖𝕤𝕤
        """
        )

    # Mostra as opções do menu principal para o usuário escolher.
    def exibir_opcoes(self):
        print("1. Cadastrar restaurante")
        print("2. Listar restaurante")
        print("3. Alternar estado do restaurante")
        print("4. Excluir restaurante")
        print("5. Sair\n")

    # ---------- Métodos de ação(chama a partir do menu) ----------

    # Pede nome e categoria ao usuário e manda o SaborExpress cadastrar.

    def cadastrar_novo_restaurante(self):
        self.exibir_subtitulo("Cadastro de novos restaurantes\n")
        nome = input("Digite o nome do restaurante que deseja cadastrar: ")
        categoria = input(f"Digite o nome da categoria do restaurante {nome}: ")

        sucesso = self.app.cadastrar_restaurante(nome, categoria)

        if sucesso:
            print(f"O restaurante {nome} foi cadastrado com sucesso!")

        self.voltar_ao_menu_principal()

    # Pede o nome de um restaurante e alterna seu estado(ativo/inativo).
    def alternar_estado_do_restaurante(self):
        self.exibir_subtitulo("Alternando estado do restaurante\n")
        nome = input("Digite o nome do restaurante que deseja alterar o estado: ")

        novo_estado = self.app.alternar_estado(nome)

        # None significa que o restaurante não foi encontrado no banco
        if novo_estado is None:
            print("O restaurante não foi encontrado!")
        else:
            status = "ativado" if novo_estado else "desativado"
            print(f"O restaurante {nome} foi {status} com sucesso!")

        self.voltar_ao_menu_principal()

    def excluir_restaurante(self):
        self.exibir_subtitulo("Excluir restaurante\n")

        restaurantes = self.app.listar_restaurantes()

        if not restaurantes:
            print("Nenhum restaurante cadastrado para excluir.")
            self.voltar_ao_menu_principal()
            return

        print("Restaurantes cadastrados:")
        print("-" * 40)
        for nome, categoria, _ in restaurantes:
            print(f"• {nome} ({categoria})")
        print()

        nome = input("Digite o nome do restaurante que deseja excluir: ")

        if self.app.restaurante_existe(nome):
            confirmacao = input(
                f'Tem certeza que deseja excluir o restaurante "{nome}"? (s/n): '
            )

            if confirmacao.lower() == "s":
                self.app.excluir_restaurante(nome)
                print(f"O restaurante {nome} foi excluído com sucesso!")
            else:
                print("Exclusão cancelada.")
        else:
            print("O restaurante não foi encontrado!")

        self.voltar_ao_menu_principal()

    # Lista todos os restaurantes cadastrados, um por linha.
    def listar_restaurantes(self):
        self.exibir_subtitulo("Listando os restaurantes\n")

        restaurantes = self.app.listar_restaurantes()

        if restaurantes:
            print(f"{'Nome do Restaurante'.ljust(21)} | {'Categoria'.ljust(20)} | Status")
            print("-" * 65)

            for nome, categoria, ativo in restaurantes:
                status = "ativado" if ativo else "desativado"
                print(f"{nome.ljust(21)} | {categoria.ljust(20)} | {status}")
        else:
            print("Nenhum restaurante cadastrado.")

        self.voltar_ao_menu_principal()


    
    # Pausa a execução esperando o usuário apertar uma tecla,
    # depois chama main() de novo para reiniciar o ciclo do menu.
    def voltar_ao_menu_principal(self):
        input("\nDigite uma tecla para voltar ao menu principal")
        self.main()

    # Lê a opção digitada e decide qual método chamar.
    # Usa try/except para tratar o caso de o usuário digitar algo não numérico.
    def escolher_opcao(self):
        try:
            opcao_escolhida = int(input("Escolha uma opção: "))

            if opcao_escolhida == 1:
                self.cadastrar_novo_restaurante()
            elif opcao_escolhida == 2:
                self.listar_restaurantes()
            elif opcao_escolhida == 3:
                self.alternar_estado_do_restaurante()
            elif opcao_escolhida == 4:
                self.excluir_restaurante()
            elif opcao_escolhida == 5:
                self.finalizar_app()
            else:
                self.opcao_invalida()
        except ValueError:
            # Captura especificamente erro de conversão int() (texto não numérico)
            self.opcao_invalida()

    # Função principal: limpa a tela, mostra o nome do programa,
    # as opções e processa a escolha do usuário.
    def main(self):
        os.system("cls")
        self.exibir_nome_do_programa()
        self.exibir_opcoes()
        self.escolher_opcao()


# Ponto de entrada do programa:
# só roda o menu se o arquivo for executado diretamente.
if __name__ == "__main__":
    menu = Menu()
    menu.main()
