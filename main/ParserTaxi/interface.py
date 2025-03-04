import asyncio

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

import graph


class TaxiParser(MDApp):
    def __init__(self, **kwargs):
        super().__init__()

    def build(self):
        self.theme_cls.primary_palette = "Green"

        btn_view = MDButton(MDButtonText(text="Смотреть", ), pos_hint={"center_x": 0.5, "center_y": 0.5},
                            on_release=self.start, style="elevated")

        self.field_filter = MDTextField(text='all')
        self.field_group = MDTextField(text='all')
        self.field_week = MDTextField(text='all')

        setting_layout = MDBoxLayout(self.field_group, self.field_filter, self.field_week, orientation='horizontal', )
        screen = MDScreen(btn_view, setting_layout, md_bg_color=self.theme_cls.surfaceColor)
        return screen

    def start(self, instance):
        graph.render(group=self.field_group.text, day=self.field_filter.text, week=self.field_week.text)


def run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Запускаем цикл событий Kivy
    async_run = asyncio.ensure_future(asyncio.gather(TaxiParser().async_run(async_lib='asyncio')))
    # Планируем остановку цикла, когда Kivy App закроется
    async_run.add_done_callback(lambda *args: loop.stop())

    # Запускаем цикл событий asyncio
    loop.run_forever()


if __name__ == "__main__":
    run_async()
