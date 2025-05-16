from PriceCheck.cart_model import CartModel
from PriceCheck.cart_item import CartItem  # см. следующий шаг
from kivymd.uix.boxlayout import MDBoxLayout

class CartController:
    def _init_(self, cart_box: MDBoxLayout):
        self.model = CartModel()
        self.cart_box = cart_box

    def load_items(self):
        self.cart_box.clear_widgets()
        for index, item in enumerate(self.model.items):
            self.cart_box.add_widget(
                CartItem(
                    item_name=item["name"],
                    item_qty=item["qty"],
                    on_update=lambda name, qty, i=index: self.model.update_item(i, name, qty),
                    on_delete=lambda i=index: self.remove_item(i)
                )
            )

    def add_item(self, name, qty):
        self.model.add_item(name, qty)
        self.load_items()

    def remove_item(self, index):
        self.model.remove_item(index)
        self.load_items()

    def get_json(self):
        return self.model.to_json()