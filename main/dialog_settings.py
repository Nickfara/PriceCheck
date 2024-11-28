from kivymd.uix.button import MDIconButton as IconButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout


def dialog_settings_open(self):
    if self.dialog:  # Закрыть диалоговое окно, если оно открыто
        self.dialog.dismiss()

    def content():
        pass

    btn_dismiss = IconButton(icon='dismiss', on_release=self.dialog_cart_open,
                             icon_color='red',
                             line_color='red', text_color='red')
    btn_save = IconButton(icon='save', on_release=self.send_cart, icon_color='green',
                          line_color='green', text_color='green')
    self.dialog = MDDialog(size_hint_y=None, size_hint_max_y=.9, size_hint_min_y=.1)
    self.dialog.add_widget(MDDialogHeadlineText(text='Отправить', halign='left'))
    self.dialog.add_widget(MDDialogContentContainer(content()))
    self.dialog.add_widget(MDDialogButtonContainer(BoxLayout(), btn_dismiss, btn_save))

    self.dialog.open()