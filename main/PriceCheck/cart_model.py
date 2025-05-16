import json

class CartModel:
    def _init_(self):
        self.items = []

    def add_item(self, name, qty=1):
        self.items.append({"name": name, "qty": qty})

    def update_item(self, index, name=None, qty=None):
        if 0 <= index < len(self.items):
            if name is not None:
                self.items[index]["name"] = name
            if qty is not None:
                self.items[index]["qty"] = qty

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)

    def to_json(self):
        return json.dumps(self.items, ensure_ascii=False, indent=2)

    def from_json(self, data):
        try:
            self.items = json.loads(data)
        except json.JSONDecodeError:
            self.items = []

    def clear(self):
        self.items = []