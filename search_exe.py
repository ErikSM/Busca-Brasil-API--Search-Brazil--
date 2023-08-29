from access.about_api import general_information
from app.App import App
from app.menus import create_menus


def start():
    Start()


class Start(App):
    def __init__(self):
        super().__init__()

        create_menus(self)

        self.print_text(general_information)

        self.window.mainloop()


start()
