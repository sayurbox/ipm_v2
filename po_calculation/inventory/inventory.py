import json
import os
import random

class Inventory:
    def __init__(self, sku, quantity):
        self.sku = sku
        self.quantity = quantity

class InventoryLoader:
    def load_inventory(self):
        raise NotImplementedError("Subclasses should implement this method.")

class JsonInventoryLoader(InventoryLoader):
    def __init__(self, file_path):
        self.file_path = file_path

    def load_inventory(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
        else:
            return {}        

        inventory = {}
        for sku, quantity in data.items():
            inventory[sku] = Inventory(sku, quantity)

        return inventory

class DatabaseInventoryLoader(InventoryLoader):
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def load_inventory(self):
        # Add your database loading logic here
        pass

class InventoryManager:
    def __init__(self, inventory_loader):
        self.inventory = inventory_loader.load_inventory()

    def get_inventory(self, sku):
        return self.inventory.get(sku)
