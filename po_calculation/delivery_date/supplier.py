from datetime import date, timedelta
import json

class Supplier:
    def __init__(self, supplier_id, lead_time, delivery_days, holidays):
        self.supplier_id = supplier_id
        self.lead_time = lead_time
        self.delivery_days = delivery_days
        self.holidays = holidays

    def next_delivery_date(self, order_date):
        delivery_date = order_date + timedelta(days=self.lead_time)

        while True:
            if delivery_date.weekday() not in self.delivery_days or delivery_date.isoformat() in self.holidays:
                delivery_date += timedelta(days=1)
            else:
                break

        return delivery_date
        
    def n2n_delivery_date(self, order_date):
        next_order_date = order_date + timedelta(days=1)
        delivery_date_1 = self.next_delivery_date(order_date)
        delivery_date_2 = self.next_delivery_date(next_order_date)

        while delivery_date_1 == delivery_date_2:
            next_order_date += timedelta(days=1)
            delivery_date_2 = self.next_delivery_date(next_order_date)

        return delivery_date_2


class SupplierManager:
    def __init__(self, supplier_loader):
        self.suppliers = supplier_loader.load_suppliers()

    def get_supplier(self, supplier_id):
        return self.suppliers.get(supplier_id)
    def get_suppliers(self):
        return self.suppliers

#adding different supplier loades for 

class SupplierLoader:
    def load_suppliers(self):
        raise NotImplementedError("Subclasses should implement this method.")


class JsonSupplierLoader(SupplierLoader):
    def __init__(self, file_path):
        self.file_path = file_path

    def load_suppliers(self):
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        suppliers = {}
        for supplier_id, info in data.items():
            lead_time = info.get('lead_time', 0)
            delivery_days = info.get('delivery_days', list(range(7)))
            holidays = info.get('holidays', [])
            suppliers[supplier_id] = Supplier(supplier_id, lead_time, delivery_days, holidays)

        return suppliers


class DatabaseSupplierLoader(SupplierLoader):
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def load_suppliers(self):
        # Add your database loading logic here
        pass
