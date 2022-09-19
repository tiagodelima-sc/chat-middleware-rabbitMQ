import time
from threading import Thread
try:
    from tkinter import *
    from tkinter import messagebox
except:
    input('Parece que o Tkinter não está instalado na sua maquina. Por favor, instale a lib para continuar a execução.')
    exit()

import pika

PRIVADO = False
EMGRUPO = False
REMETENTE = input('Remetente: ')
control = True

while control:

    opt = int(input('[1] - Privado \t [2] - Grupo\n '))
    if opt == 1:
        DESTINATARIO = input('Destinatario: ')
        PRIVADO = True
        control = False
    else:
        if opt == 2:
            GRUPO = input('Grupo: ')
            EMGRUPO = True
            control = False
        else:
            print('ERRO! Digite uma opção válida.\n')

def receiver():

    def chamada(ch, method, propreties, body):
        if opt == 1:
            lista_mensagem.insert(END, f"{DESTINATARIO} disse: " + body.decode('utf-8'))
        else:
            lista_mensagem.insert(END, " [x] " + body.decode('utf-8'))


    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    if EMGRUPO:
        channel.exchange_declare(exchange=GRUPO, exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=GRUPO, queue=queue_name)

        channel.basic_consume(queue=queue_name, on_message_callback=chamada, auto_ack=True)
        lista_mensagem.insert(END,"Aguarde as pessoas entrar no grupo... ")
        time.sleep(2)
        messagebox.showinfo("Atenção", "O Chat está On-line")
        lista_mensagem.delete(0,END)

    if PRIVADO:
        channel.queue_declare(queue=REMETENTE)
        channel.basic_consume(queue=REMETENTE, on_message_callback=chamada, auto_ack=True)
        lista_mensagem.insert(END,"Aguarde... ")
        time.sleep(2)
        messagebox.showinfo("Atenção", "O Chat está On-line")
        lista_mensagem.delete(0,END)

    channel.start_consuming()
    connection.close()



def send():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    if EMGRUPO:
        live = entry_field.get()
        channel.exchange_declare(exchange=GRUPO, exchange_type='fanout')
        channel.basic_publish(exchange=GRUPO, routing_key='', body= f'{REMETENTE}:' + live)

    if PRIVADO:
        channel.queue_declare(queue=DESTINATARIO)
        live = entry_field.get()
        lista_mensagem.insert(END, f"Voce falou: " + live)
        channel.basic_publish(exchange='', routing_key=DESTINATARIO, body= live.encode('utf-8'))

    connection.close()


# Iniciando layout

tela = Tk()
tela.title(f'Chat Ao Vivo - {REMETENTE}')
tela.geometry("500x325+300+100")
tela.configure(bg = "#474440")

# Definindo se pode aumentar ou diminuir
tela.resizable(False, False)

# icon
# tela.iconbitmap("img/icon-whats.ico")

# Funcao e Botao Sair

def sair():
    lista_mensagem.delete(0,END)
    tela.destroy()
    messagebox.showinfo("Aviso", f"{REMETENTE} Deslogou")


botao_sair = Button(tela, text = "Sair Agora", command= sair, fg="#fff" , bg="#FF2511")
botao_sair.pack(side = TOP, anchor = NE, pady = 5, padx = 5)

# Apresenta as mensagens na tela

messages_frame = Frame(tela)
scrollbar = Scrollbar(messages_frame)
lista_mensagem = Listbox(messages_frame, height=10, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side= RIGHT, fill=Y)
lista_mensagem.pack(side=LEFT, fill=BOTH)
lista_mensagem.pack()
messages_frame.pack()

# Vai Receber os valores que o usuario digitar com a caixa de texto

botao_frame = Frame(tela)
botao_frame.configure(bg="#474440")
lb = Label(botao_frame,text = "Digite sua mensagem: ", fg="#fff", bg = "#474440")
lb.pack(side = LEFT, anchor= S, pady = 15, padx=5)
entry_field = Entry(botao_frame, textvariable = '', bg = "#fff")
entry_field.pack(side = LEFT, anchor = SE,pady = 15)

# Botao enviar a mensagem
botao_enviar = Button(botao_frame, text= "Enviar", command=send,fg="#fff", bg = "#32CD30")
botao_enviar.pack(side = LEFT, anchor = S, pady = 15, padx = 5)

botao_frame.pack()

receber = Thread(target= receiver)
#mandar = Thread(target= send)
receber.start()
#mandar.start()
tela.mainloop()
