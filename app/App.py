from tkinter import *

from access.requests import open_dict
from app.configuration import strings, colors


class App:

    def __init__(self):

        self.color = colors
        self.strings = strings
        self.dict_selected = None

        self.window = Tk()
        self.window.title('Busca Brasil')
        self.window.resizable(True, True)
        self.window.config(bg=self.color['purple'])

        self.label_left = Label(self.window, text=self.strings['label list left'],
                                bg=self.color['purple'], fg=self.color['white'])
        self.label_left.grid(row=0, column=1)

        self.listbox_left = Listbox(self.window, height=22, width=60, bd=10,
                                    bg=self.color['grey'], fg=self.color['white'])

        self.listbox_left.grid(row=1, rowspan=10, column=1)

        self.botao = Button(self.window, text='Select item', command=self.search)
        self.botao.grid(row=1, column=2)
        cont = 2
        while cont < 10:
            Button(self.window, text=(' ' * 20), state=DISABLED).grid(row=cont, column=2)
            cont += 1

        self.label_right = Label(self.window, text=self.strings['label list right'],
                                 bg=self.color['purple'], fg=self.color['white'])
        self.label_right.grid(row=0, column=3)

        self.listbox_right = Listbox(self.window, height=22, width=60, bd=10,
                                     bg=self.color['grey'], fg=self.color['white'])
        self.listbox_right.grid(row=1, rowspan=10, column=3)

        self.text = Text(self.window, height=10, width=115, bd=12,
                         bg=self.color['grey'], fg=self.color['white'])
        self.text.grid(row=12, column=1, columnspan=3)

        y_axis = Scrollbar(self.window, orient=VERTICAL, command=self.text.yview)
        y_axis.grid(row=12, column=0, sticky=N + S)
        self.text.config(yscrollcommand=y_axis.set)

    def clear_left(self):
        self.listbox_left.delete(0, END)

    def clear_right(self):
        self.listbox_right.delete(0, END)

    def clear_text(self):
        self.text.delete(1.0, END)

    def print_information(self, info):
        self.text.insert(END, info)

    def search(self):
        selected = self.listbox_left.get(ANCHOR)

        if not self.dict_selected[selected][1]:

            self.clear_right()

            dict_open = open_dict(self.dict_selected[selected][0])
            for i in dict_open:
                self.listbox_right.insert(END, i)

        else:
            self.listbox_right.insert(END, 'Nao disponivel')
