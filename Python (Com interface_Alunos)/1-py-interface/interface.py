# Exemplo de Interface — versão orientada a objetos
# Janela simples: digita um texto, clica no botão, o texto aparece no rótulo.

import tkinter as tk

#Classe Principal
class InterfaceExemplo:
    #Método construtor (Para criar janela "Tela" principal)
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Exemplo de Interface")
        self.janela.geometry("400x150")
        self.criar_widgets()

    #Montar todos os elementos visuais da tela
    def criar_widgets(self):
        #Caixa de entrada "Entry" ou input onde o usuário digita algo "Texto"
        self.caixa_texto = tk.Entry(self.janela, width=60)
        self.caixa_texto.pack(pady=10)

        #Botão que dispara mostrar_mensagem() ao ser clicado
        self.botao = tk.Button(
            self.janela, text="Mostrar Texto", command=self.mostrar_mensagem
        )
        self.botao.pack(pady=5)

        # Rótulo "Label" que mostra a mensagem se o usuário clicar no botão
        self.label_resultado = tk.Label(self.janela, text="")
        self.label_resultado.pack(pady=10)

    #Captura o texto digitado pelo usuário (No Entry ou "Input") e tranfere ele para variável texto para ser exibido
    def mostrar_mensagem(self):
        texto = self.caixa_texto.get()
        self.label_resultado.config(text=texto)

    #Inicia o loop principal da Tela (Isso mantém a tela sendo exibida)
    def executar(self):
        self.janela.mainloop()

#Conecta a classe principal "InterfaceExemplo" e roda o método "executar" para fazer o programa funcionar
if __name__== "__main__":
    app = InterfaceExemplo()
    app.executar()
