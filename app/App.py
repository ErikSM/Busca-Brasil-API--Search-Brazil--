from tkinter import *
from queue import Empty, Queue
from threading import Thread

from access.requests import open_dict
from app.configuration import strings, colors
from app.input_validation import VALIDATORS


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
        self._quick_selection = None

        self._query_results = None
        self._query_selection = None
        self._query_with_complement = False
        self._query_after_id = None
        self._closed = False

        self.window = Tk()
        self.window.protocol("WM_DELETE_WINDOW", self._close)
        self.window.bind("<Destroy>", self._on_window_destroy, add="+")
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
        self.listbox_left.bind("<<ListboxSelect>>", self._on_operation_selected)

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
        if text_field in ("all", "listbox left"):
            self._invalidate_query()
            self._close_quick_window()
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
        if self._closed:
            return
        self._invalidate_query()
        self._close_quick_window()
        selected = self.listbox_left.get(ANCHOR)

        try:
            self.api_string = self.dict_selected[selected][2]
            self.api_need_complement = self.dict_selected[selected][1]
            self.api_address = self.dict_selected[selected][0]
        except Exception as ex:
            self.clear("text")
            self.print_text(f"Error:{ex}..\n\n-Item nao selecionado ou invalido")

            self.clear("listbox right")
            self.listbox_right.insert(END, "Erro de acesso")
        else:
            self.clear("text")
            self.print_text(self.api_string)
            self.print_text("\n\n\n")

            if not self.api_need_complement:
                self.clear("entry")
                self.print_entry(f'../{selected}>')
                self.clear("listbox right")
                self._start_query(self.api_address)
            else:
                self.clear("entry")
                self.print_entry(f'../{selected}>')
                self._quick_window(selected)

    def _start_query(self, address, complement=None):
        self._invalidate_query()
        results = Queue()
        self._query_results = results
        self._query_selection = (self.listbox_left.curselection() if complement is None
                                 else self._quick_selection)
        self._query_with_complement = complement is not None
        Thread(target=self._fetch_query, args=(address, results, complement), daemon=True).start()
        self._query_after_id = self.window.after(100, self._poll_query, results)

    @staticmethod
    def _fetch_query(address, results, complement=None):
        # The worker receives only request data and the queue, never Tk widgets.
        try:
            result = open_dict(address) if complement is None else open_dict(address, complement)
        except Exception as ex:
            results.put((None, ex))
        else:
            results.put((result, None))

    def _poll_query(self, results):
        # A queue identifies one request, including repeated searches of the same item.
        if self._closed or results is not self._query_results:
            return
        self._query_after_id = None
        try:
            result, error = results.get_nowait()
        except Empty:
            self._query_after_id = self.window.after(100, self._poll_query, results)
            return

        with_complement = self._query_with_complement
        self._invalidate_query()
        if with_complement:
            self._finish_quick_query(result, error)
        elif error is not None:
            self.clear("text")
            self.print_text(error)
        else:
            for item in result:
                self.listbox_right.insert(END, item)

    def _invalidate_query(self):
        self._query_results = None
        self._query_selection = None
        self._query_with_complement = False
        if self._query_after_id is not None:
            try:
                self.window.after_cancel(self._query_after_id)
            except TclError:
                # The root may already be in the process of being destroyed.
                pass
            self._query_after_id = None

    def _on_operation_selected(self, event):
        if self._closed:
            return
        selection = self.listbox_left.curselection()
        # Selecting Entry text can take PRIMARY selection without choosing another operation.
        if self.field_toplevel is not None and not selection:
            return
        if ((self._query_results is not None and selection != self._query_selection)
                or (self.field_toplevel is not None and selection != self._quick_selection)):
            self._invalidate_query()
            self._close_quick_window()

    def _close(self):
        if self._closed:
            return
        self._closed = True
        self._invalidate_query()
        self._close_quick_window()
        self.window.destroy()

    def _on_window_destroy(self, event):
        if event.widget is self.window:
            self._closed = True
            self.field_toplevel = None
            self._quick_selection = None
            self._invalidate_query()
        elif event.widget is self.field_toplevel:
            self.field_toplevel = None
            self._quick_selection = None
            self._invalidate_query()

    def _close_quick_window(self, dialog=None):
        if dialog is not None and dialog is not self.field_toplevel:
            return
        dialog = self.field_toplevel
        self.field_toplevel = None
        self._quick_selection = None
        if dialog is not None:
            self._invalidate_query()
            dialog.destroy()

    def _quick_window(self, search):
        if self._closed:
            return
        self._close_quick_window()
        self.selected_operation = search
        dialog = self.field_toplevel = Toplevel(self.window)
        self._quick_selection = self.listbox_left.curselection()
        dialog.protocol("WM_DELETE_WINDOW", lambda: self._close_quick_window(dialog))
        dialog.bind("<Destroy>", self._on_window_destroy, add="+")

        self.field_toplevel.title(f"{search}")
        self.field_toplevel.resizable(False, False)
        self.field_toplevel.geometry("500x85+300+250")
        self.field_toplevel.config(bg=self.color['grey'])

        Label(self.field_toplevel, text=f"Digite - ({search}):",
              bg=self.color['grey'], fg=self.color['white']).pack(side=LEFT)

        entry = Entry(self.field_toplevel)
        entry.pack(side=LEFT)

        Button(self.field_toplevel, text="OK",
               command=lambda: self._get_to_quick_window(entry, dialog)).pack(side=LEFT)

    def _get_to_quick_window(self, entry: Entry, dialog=None):
        if (self._closed or self.field_toplevel is None
                or (dialog is not None and dialog is not self.field_toplevel)):
            return
        self._invalidate_query()
        self.captured_to_toplevel = entry.get()

        validator = VALIDATORS.get(self.selected_operation)
        if validator is not None:
            try:
                self.captured_to_toplevel = validator(self.captured_to_toplevel)
            except ValueError as ex:
                self.clear("text")
                self.print_text(str(ex))
                self._close_quick_window()
                return

        self.clear("entry")
        self.print_entry(f'../{self.selected_operation}>')
        self.print_entry(self.captured_to_toplevel)

        self.clear("listbox right")

        self._start_query(self.api_address, self.captured_to_toplevel)

    def _finish_quick_query(self, dict_opened, error):
        if error is not None:
            self.clear("text")
            self.print_text(f'Error:{error}   \n\n-Em branco ou invalido')

            self.clear("listbox right")
            self.listbox_right. insert(END, 'Erro de acesso')

        else:
            for i in dict_opened:
                self.listbox_right.insert(END, i)

                if type(dict_opened) == dict:

                    if type(dict_opened[i]) == list:
                        for j in dict_opened[i]:
                            self.listbox_right.insert(END, j)
                    else:
                        self.listbox_right.insert(END, dict_opened[i])

                self.listbox_right.insert(END, '\n')
        self._close_quick_window()
