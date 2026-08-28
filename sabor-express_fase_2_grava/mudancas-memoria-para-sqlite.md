# 🔄 De memória para SQLite - o que muda

> Ponto de partida: a versão POO com `Restaurante` + `SaborExpress` + `Menu` guardando tudo numa lista em memória (`app_poo.py`).
> Objetivo: os dados persistirem em `restaurantes.db`, sobrevivendo ao fechar o programa (`app_poo_sqlite.py`).
>
> Nesta versão, todo trecho **Antes** e **Depois** é o código **completo** do método/bloco em questão — nada resumido com `...`. Quando um bloco é **novo** (não existia antes), isso é dito explicitamente, e não existe um "Antes" para ele.

---

## 1 — A classe `Restaurante` deixa de existir (apague inteira)

Na versão em memória, cada restaurante era um objeto completo, com seus próprios dados e comportamento:

```python
# app_poo.py — APAGAR esta classe inteira

# Classe que representa um único restaurante cadastrado no sistema.
# Cada objeto dessa classe guarda seus próprios dados (nome, categoria, ativo).
class Restaurante:

    # Construtor: roda automaticamente quando um novo Restaurante é criado.
    # Recebe nome e categoria, e já define ativo como False por padrão.
    def __init__(self, nome, categoria):
        self.nome = nome
        self.categoria = categoria
        self.ativo = False  # todo restaurante começa desativado

    # Método que inverte o estado do restaurante (ativo <-> inativo).
    # Não recebe parâmetros além de self porque só mexe nos próprios dados.
    def alternar_estado(self):
        self.ativo = not self.ativo

    # Método especial: define como o objeto aparece quando usado em
    # print(restaurante) ou dentro de uma f-string. Evita repetir a
    # formatação toda vez que for exibir um restaurante na tela.
    def __str__(self):
        status = "ativado" if self.ativo else "desativado"
        return f"-{self.nome.ljust(20)} | {self.categoria.ljust(20)} | {status}"
```

Na versão com banco, cada restaurante passa a ser uma **linha da tabela**, e o SQLite já devolve os dados prontos como tupla `(nome, categoria, ativo)`. Criar um objeto `Restaurante` para cada linha só duplicaria um dado que já está estruturado — por isso a classe inteira desaparece em `app_poo_sqlite.py`.

**Não há "depois" para este bloco: ele simplesmente não existe mais no arquivo.** Guarde isso na cabeça, porque os dois métodos que ela continha (`alternar_estado` e a formatação de exibição) não somem — eles **migram** para outros lugares, como você vai ver nas seções 3.3 e 4.5.

---

## 2 — `SaborExpress` troca a lista por conexões com o banco

### 2.1 — Imports

**Antes** (`app_poo.py`):

```python

# Sabor Express - Versão Orientada a Objetos
# Sistema de cadastro e gerenciamento de restaurantes

import os


# Classe que representa um único restaurante cadastrado no sistema.
# Cada objeto dessa classe guarda seus próprios dados (nome, categoria, ativo).

```

**Depois** (`app_poo_sqlite.py`):

```python

# Sabor Express - Versão Orientada a Objetos com SQLite
# Sistema de cadastro e gerenciamento de restaurantes

import os
import sqlite3


# Classe responsável por toda a comunicação com o banco de dados.
# Nenhum método aqui usa input()/print() de menu — só SQL puro.
# Isso mantém a lógica de banco isolada da lógica de interface.

```

### 2.2 — Construtor e inicialização do banco

**Antes** — guardava tudo em `self.restaurantes` (lista de objetos), já povoada na criação:

```python
# app_poo.py

class SaborExpress:

    # Construtor: cria a lista de restaurantes já com alguns itens iniciais.
    def __init__(self):
        self.restaurantes = [
            Restaurante("Praça", "Japonesa"),
            Restaurante("Pizza Suprema", "Pizza"),
            Restaurante("Cantina", "Italiano"),
        ]
```

**Depois** — guarda só o caminho do arquivo do banco, e delega a criação/verificação da tabela para `inicializar_banco`. Repare que `inicializar_banco` é um método **novo**, sem equivalente "antes": na versão em memória a lista já nascia pronta dentro do `__init__`, sem precisar checar se "já tinha dados".

```python
# app_poo_sqlite.py

class SaborExpress:

    # Construtor: guarda o nome do arquivo do banco e garante que a
    # tabela exista assim que o objeto é criado.
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
```

---

## 3 — Cada método de `SaborExpress` vira uma consulta SQL

O padrão se repete em quase todos os métodos: **abrir conexão → executar SQL → fechar conexão**.

### 3.1 — Cadastrar restaurante

**Antes:**
```python
# app_poo.py

# Cria um novo objeto Restaurante e adiciona na lista interna.
def cadastrar_restaurante(self, nome, categoria):
    novo_restaurante = Restaurante(nome, categoria)
    self.restaurantes.append(novo_restaurante)
    return novo_restaurante
```

**Depois:**
```python
# app_poo_sqlite.py

# Insere um novo restaurante no banco.
# Retorna True se deu certo, False se houve erro (ex: conexão falhou).
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
```

Repare que o tipo de retorno muda: antes devolvia o objeto `Restaurante` criado; depois devolve `True`/`False`, porque não existe mais um objeto para devolver — só o sinal de sucesso ou falha da escrita no banco.

### 3.2 — Buscar restaurante vira buscar só o estado

**Antes** — buscava o objeto inteiro, percorrendo a lista à mão:
```python
# app_poo.py

# Percorre a lista de restaurantes procurando um nome específico.
# Retorna o objeto Restaurante se achar, ou None se não encontrar.
def buscar_restaurante(self, nome):
    for restaurante in self.restaurantes:
        if restaurante.nome == nome:
            return restaurante
    return None
```

**Depois** — `buscar_restaurante` some do arquivo. Não existe mais um "trazer o restaurante inteiro para o Python"; o SQL já filtra a linha certa com `WHERE`, então o método novo busca **só o campo que interessa** (`ativo`):

```python
# app_poo_sqlite.py

# Busca o estado atual (ativo/inativo) de um restaurante pelo nome.
# Retorna 0/1 se encontrar, ou None se não existir.
def buscar_estado(self, nome):
    conn = sqlite3.connect(self.caminho_banco)
    cursor = conn.cursor()

    cursor.execute("SELECT ativo FROM restaurantes WHERE nome = ?", (nome,))
    resultado = cursor.fetchone()

    conn.close()

    # fetchone() retorna uma tupla como (0,) ou (1,) — pegamos só o valor
    return resultado[0] if resultado is not None else None
```

`buscar_estado` é usado logo a seguir, dentro de `alternar_estado` (seção 3.3).

### 3.3 — Alternar estado passa a viver em `SaborExpress`

**Antes** — não existia um método de "alternar estado" em `SaborExpress`. Essa responsabilidade estava dentro do próprio objeto `Restaurante` (veja a seção 1): quem alternava era `restaurante.alternar_estado()`, e o `Menu` só lia o atributo `restaurante.ativo` depois. Ou seja: o "antes" deste bloco já foi apagado na seção 1 — não há nada equivalente para copiar aqui, só para lembrar de onde a lógica saiu.

**Depois** — como não existe mais objeto `Restaurante`, alternar o estado agora é responsabilidade de `SaborExpress`. O método reaproveita `buscar_estado` para saber o valor atual, calcula o inverso em Python, e grava esse inverso no banco com `UPDATE`:

```python
# app_poo_sqlite.py

# Inverte o estado (ativo <-> inativo) de um restaurante.
# Retorna o novo estado (True/False) se encontrou, ou None se não existir.
# Dica: Logo após:  def buscar_estado(self, nome): (Linha 86)
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
```

### 3.4 — Listar restaurantes

**Antes** — a lista já vivia pronta em memória, então o método só devolvia a referência a ela:
```python
# app_poo.py

# Retorna a lista de restaurantes cadastrados.
# A formatação da exibição é responsabilidade da classe Menu.
def listar_restaurantes(self):
    return self.restaurantes
```

**Depois** — busca todas as linhas no banco, já ordenadas por nome. Cada item volta como tupla `(nome, categoria, ativo)`, no lugar dos objetos `Restaurante` de antes:
```python
# app_poo_sqlite.py

# Retorna todos os restaurantes cadastrados, ordenados por nome.
# Cada item vem como tupla: (nome, categoria, ativo)
def listar_restaurantes(self):
    conn = sqlite3.connect(self.caminho_banco)
    cursor = conn.cursor()

    cursor.execute("SELECT nome, categoria, ativo FROM restaurantes ORDER BY nome")
    restaurantes = cursor.fetchall()

    conn.close()
    return restaurantes
```

### 3.5 — Dois métodos totalmente novos: `restaurante_existe` e `excluir_restaurante`

Estes dois **não têm "antes"** — a versão em memória não tinha a opção de excluir restaurante. Eles existem só para dar suporte à nova opção 4 do menu (seção 4.4).

```python
# app_poo_sqlite.py

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
```

`restaurante_existe` é chamado primeiro pelo `Menu` para decidir se vale a pena pedir confirmação; só depois da confirmação o `Menu` chama `excluir_restaurante`. Você vai ver essa sequência completa na seção 4.4.

---

## 4 — `Menu`: muda como interpreta os retornos, e ganha uma opção nova

O `Menu` continua só com `input`/`print` — ele nunca fala SQL diretamente, só chama métodos de `self.app` (o `SaborExpress`). O que muda é o **formato dos dados** que ele recebe de volta, e o fato de ganhar uma opção nova (excluir).

### 4.1 — Opções exibidas

**Antes:**
```python
# app_poo.py

def exibir_opcoes(self):
    print("1. Cadastrar restaurante")
    print("2. Listar restaurante")
    print("3. Alternar estado do restaurante")
    print("4. Sair\n")
```

**Depois** — ganha a opção 4 (Excluir), e "Sair" desloca para 5:
```python
# app_poo_sqlite.py

def exibir_opcoes(self):
    print("1. Cadastrar restaurante")
    print("2. Listar restaurante")
    print("3. Alternar estado do restaurante")
    print("4. Excluir restaurante")
    print("5. Sair\n")
```

### 4.2 — Cadastrar novo restaurante

**Antes** — não checava sucesso, porque cadastrar numa lista em Python não falha:
```python
# app_poo.py

# Pede nome e categoria ao usuário e manda o SaborExpress cadastrar.
def cadastrar_novo_restaurante(self):
    self.exibir_subtitulo("Cadastro de novos restaurantes\n")
    nome = input("Digite o nome do restaurante que deseja cadastrar: ")
    categoria = input(f"Digite o nome da categoria do restaurante {nome}: ")

    self.app.cadastrar_restaurante(nome, categoria)
    print(f"O restaurante {nome} foi cadastrado com sucesso!")

    self.voltar_ao_menu_principal()
```

**Depois** — agora `cadastrar_restaurante` pode devolver `False` (erro de banco), então o `Menu` só imprime a mensagem de sucesso se `sucesso` for verdadeiro:
```python
# app_poo_sqlite.py

# Pede nome e categoria ao usuário e manda o SaborExpress cadastrar.
def cadastrar_novo_restaurante(self):
    self.exibir_subtitulo("Cadastro de novos restaurantes\n")
    nome = input("Digite o nome do restaurante que deseja cadastrar: ")
    categoria = input(f"Digite o nome da categoria do restaurante {nome}: ")

    sucesso = self.app.cadastrar_restaurante(nome, categoria)

    if sucesso:
        print(f"O restaurante {nome} foi cadastrado com sucesso!")

    self.voltar_ao_menu_principal()
```

### 4.3 — Alternar estado do restaurante

**Antes** — recebia um objeto `Restaurante` ou `None`, e quem alternava o estado era o próprio objeto (`restaurante.alternar_estado()`); o `Menu` só lia `restaurante.ativo` depois para montar a mensagem:
```python
# app_poo.py

# Pede o nome de um restaurante e alterna seu estado (ativo/inativo).
def alternar_estado_do_restaurante(self):
    self.exibir_subtitulo("Alternando estado do restaurante\n")
    nome_restaurante = input(
        "Digite o nome do restaurante que deseja alterar o estado: "
    )

    restaurante = self.app.buscar_restaurante(nome_restaurante)

    # Só mexe no estado se o restaurante realmente foi encontrado
    if restaurante:
        restaurante.alternar_estado()
        status = "ativado" if restaurante.ativo else "desativado"
        print(f"O restaurante {nome_restaurante} foi {status} com sucesso!")
    else:
        print("O restaurante não foi encontrado!")

    self.voltar_ao_menu_principal()
```

**Depois** — não existe mais objeto para carregar o estado; `self.app.alternar_estado(nome)` já faz a busca, a inversão e a gravação no banco (seção 3.3), e devolve direto `True`/`False`/`None`:
```python
# app_poo_sqlite.py

# Pede o nome de um restaurante e alterna seu estado (ativo/inativo).
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
```

### 4.4 — Excluir restaurante (opção nova, sem "antes")

Este método **não existe** em `app_poo.py` — é uma tela nova, criada para usar `restaurante_existe` e `excluir_restaurante` (seção 3.5). Ele lista os restaurantes, pede o nome, confirma com o usuário antes de apagar de fato, e só então chama a exclusão:

```python
# app_poo_sqlite.py

# Lista os restaurantes cadastrados e permite excluir um pelo nome,
# com uma etapa de confirmação antes de apagar de fato.
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
```

### 4.5 — Listar restaurantes (Menu)

**Antes** — cada restaurante sabia se formatar sozinho (`__str__`, definido lá na classe `Restaurante`), então o `Menu` só chamava `print(restaurante)` para cada item:
```python
# app_poo.py

# Lista todos os restaurantes cadastrados, um por linha.
# Dica: Após def excluir_restaurante(self) (Linha 247)
def listar_restaurantes(self):
    self.exibir_subtitulo("Listando os restaurantes\n")

    print(f"{'nome_restaurante'.ljust(21)} | {'categoria'.ljust(20)} | Status")

    # print(restaurante) aqui já usa o __str__ definido na classe Restaurante,
    # não precisa formatar a linha manualmente de novo
    for restaurante in self.app.listar_restaurantes():
        print(restaurante)

    self.voltar_ao_menu_principal()
```

**Depois** — como a classe `Restaurante` não existe mais (seção 1), não há mais `__str__` para reaproveitar. Cada linha chega como tupla `(nome, categoria, ativo)`, então o próprio `Menu` monta a formatação na mão. O método também passa a tratar o caso de tabela vazia, algo que a lista em memória nunca tinha (ela sempre nascia com 3 itens):
```python
# app_poo_sqlite.py

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
```

### 4.6 — Roteamento das opções (`escolher_opcao`)

**Antes** — só ia até a opção 4 (Sair):
```python
# app_poo.py

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
            self.finalizar_app()
        else:
            self.opcao_invalida()
    except ValueError:
        # Captura especificamente erro de conversão int() (texto não numérico)
        self.opcao_invalida()
```

**Depois** — ganha o `elif` da opção 4 (Excluir), e "Sair" passa a ser a opção 5:
```python
# app_poo_sqlite.py

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
```

---

