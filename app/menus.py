from access.addresses import *
from app.App import *

menus_list = {
    "Bank/Stockbroker": bank_and_stockbroker,
    "Address/Register": address_and_register,
    "Meteorology(CPTEC)": cptec_meteorology,
    "Holidays": holidays,
    "Vehicles(FIPE)": fipe_vehicles,
    "Books(ISNB)": isnb_books,
    "Products(NCM)": ncm_products,
    "Taxes": taxes
}


def create_menus(self: App):
    self.menu = Menu(self.window, bd=10)
    self.window.config(menu=self.menu)

    for i in menus_list:
        self.menu.add_command(
            label=i, command=lambda dict_select=i: _select_menu(self, menus_list[dict_select])
        )


def _select_menu(self: App, dict_selected: dict):

    self.dict_selected = dict_selected

    self.clear_left()

    for i in dict_selected:
        self.listbox_left.insert(END, i)
