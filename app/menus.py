from access.addresses import *
from app.App import *

menus_list = {
    "Bank/Stockbroker": (bank_and_stockbroker, 'Bancos, Corretoras e participantes do pix'),
    "Address/Register": (address_and_register, 'Buscas de informacoes sobre: CEP, CNPJ...'),
    "Meteorology(CPTEC)": (cptec_meteorology, 'Clima em cidades e aeroportos atraves da CPTEC'),
    "Holidays": (holidays, 'Mostra todos os feriados do ano selecionado...'),
    "Vehicles(FIPE)": (fipe_vehicles, 'Preco e informacaoes sobre veiculos pela tabela FIPE'),
    "Books(ISNB)": (isnb_books, 'Informacoes sobre livros atraves da ISNB'),
    "Products(NCM)": (ncm_products, 'Informacoes sobre produtos da NCM'),
    "Taxes": (taxes, 'Taxas oficiais como selic, etc.')
}


def create_menus(self: App):
    self.menu = Menu(self.window, bd=10)
    self.window.config(menu=self.menu)

    for i in menus_list:
        self.menu.add_command(
            label=i, command=lambda tuple_selected=i: _select_menu(self, menus_list[tuple_selected])
        )


def _select_menu(self: App, tuple_selected: tuple):

    self.dict_selected = tuple_selected[0]

    self.clear("all")

    self.print_text(tuple_selected[1])

    for i in tuple_selected[0]:
        self.listbox_left.insert(END, i)
