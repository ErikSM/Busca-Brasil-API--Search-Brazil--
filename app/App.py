from tkinter import *

from access.requests import open_dict
from app.configuration import strings, colors


class App:

    def __init__(self):

        self.color = colors
        self.strings = strings

        self.dict_selected = None

        self.api_address = None
        self.api_need_complement = None
        self.api_string = None

        self.field_toplevel = None
        self.captured_to_toplevel = None

        self.window = Tk()
        self.window.title('Busca Brasil')
        self.window.resizable(True, True)
        self.window.config(bg=self.color['purple'])

        self.label_left = Label(self.window, text=self.strings['label list left'],
                                bg=self.color['purple'], fg=self.color['white'])
        self.label_left.grid(row=0, column=1)

        self.entry = Entry(self.window, width=41, bd=10, state=DISABLED,
                           bg=self.color['grey'], fg=self.color['white'])
        self.entry.grid(row=1, column=1)

        self.listbox_left = Listbox(self.window, height=18, width=41, bd=10,
                                    bg=self.color['grey'], fg=self.color['white'])
        self.listbox_left.grid(row=2, rowspan=10, column=1)
        y_axis = Scrollbar(self.window, orient=VERTICAL, command=self.listbox_left.yview)
        y_axis.grid(row=1, rowspan=10, column=0, sticky=N + S)
        self.listbox_left.config(yscrollcommand=y_axis.set)

        self.botao = Button(self.window, text='Select item', command=self.search)
        self.botao.grid(row=1, column=2)

        cont = 2
        while cont < 10:
            Button(self.window, text=(' ' * 20), state=DISABLED).grid(row=cont, column=2)
            cont += 1

        self.label_right = Label(self.window, text=self.strings['label list right'],
                                 bg=self.color['purple'], fg=self.color['white'])
        self.label_right.grid(row=0, column=3)

        self.listbox_right = Listbox(self.window, height=22, width=111, bd=10,
                                     bg=self.color['grey'], fg=self.color['white'])
        self.listbox_right.grid(row=1, rowspan=10, column=3)
        y_axis = Scrollbar(self.window, orient=VERTICAL, command=self.listbox_right.yview)
        y_axis.grid(row=1, rowspan=10, column=4, sticky=N + S)
        self.listbox_right.config(yscrollcommand=y_axis.set)

        self.text = Text(self.window, height=10, width=145, bd=12,
                         bg=self.color['grey'], fg=self.color['white'])
        self.text.grid(row=12, column=1, columnspan=4)
        y_axis = Scrollbar(self.window, orient=VERTICAL, command=self.text.yview)
        y_axis.grid(row=12, column=0, sticky=N + S)
        self.text.config(yscrollcommand=y_axis.set)

    def clear(self, text_field="all"):
        self.entry.config(state=NORMAL)

        if text_field == "all":
            self.text.delete(1.0, END)
            self.listbox_right.delete(0, END)
            self.listbox_left.delete(0, END)
            self.entry.delete(0, END)
        elif text_field == "listbox left":
            self.listbox_left.delete(0, END)
        elif text_field == "listbox right":
            self.listbox_right.delete(0, END)
        elif text_field == "text":
            self.text.delete(1.0, END)
        elif text_field == "entry":
            self.entry.delete(0, END)
        else:
            pass

        self.entry.config(state=DISABLED)

    def print_text(self, text):
        self.text.insert(END, text)

    def print_entry(self, text):
        self.entry.config(state=NORMAL)
        self.entry.insert(END, text)
        self.entry.config(state=DISABLED)

    def search(self):
        selected = self.listbox_left.get(ANCHOR)

        try:
            self.api_string = self.dict_selected[selected][2]
            self.api_need_complement = self.dict_selected[selected][1]
            self.api_address = self.dict_selected[selected][0]
        except Exception as ex:
            self.listbox_right.insert(END, f'{ex}\nNao disponivel')
        else:

            self.clear("text")
            self.print_text(self.api_string)
            self.print_text("\n\n\n")

            if not self.api_need_complement:

                self.clear("entry")
                self.print_entry(f'../{selected}>')

                self.clear("listbox right")
                dict_opened = open_dict(self.api_address)
                print(type(dict_opened))
                for i in dict_opened:
                    self.listbox_right.insert(END, i)

            else:
                self.clear("entry")
                self.print_entry(f'../{selected}>')
                self._quick_window(selected)

    def _quick_window(self, search):
        self.field_toplevel = Toplevel()

        self.field_toplevel.title(f"{search}")
        self.field_toplevel.resizable(False, False)
        self.field_toplevel.geometry("500x85+300+250")
        self.field_toplevel.config(bg=self.color['grey'])

        Label(self.field_toplevel, text=f"Digite - ({search}):",
              bg=self.color['grey'], fg=self.color['white']).pack(side=LEFT)

        entry = Entry(self.field_toplevel)
        entry.pack(side=LEFT)

        Button(self.field_toplevel, text="OK",
               command=lambda: self._get_to_quick_window(entry)).pack(side=LEFT)

        self.field_toplevel.mainloop()

    def _get_to_quick_window(self, entry: Entry):
        self.captured_to_toplevel = entry.get()

        self.print_entry(self.captured_to_toplevel)

        self.clear("listbox right")
        dict_opened = open_dict(self.api_address, self.captured_to_toplevel)

        for i in dict_opened:
            self.listbox_right.insert(END, i)

            if type(dict_opened) == dict:

                if type(dict_opened[i]) == list:
                    for j in dict_opened[i]:
                        self.listbox_right.insert(END, j)
                else:
                    self.listbox_right.insert(END, dict_opened[i])

            self.listbox_right.insert(END, '\n')

        self.field_toplevel.destroy()
