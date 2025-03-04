from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.screen import Screen
from log import log


# creating Demo Class(base class)
class Demo(MDApp):
    def build(self):
        screen = Screen()
        Window.size = (100, 50)

        btn = MDRectangleFlatButton(text="Submit", pos_hint={
            'center_x': 0.5, 'center_y': 0.5},
                                    on_release=self.btnfunc)

        screen.add_widget(btn)
        return screen

    # defining a btnfun() for the button to
    # call when clicked on it
    def btnfunc(self, obj):
        log('Бот запущен!', 1)


if __name__ == "__main__":
    Demo().run()
