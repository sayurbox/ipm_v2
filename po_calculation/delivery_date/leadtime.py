from flask import jsonify
import json
from datetime import datetime, timedelta
from .supplier import Supplier, SupplierManager



def next_delivery_date_api(supplier_id):
    order_date = datetime.today()
    supp = SupplierManager.get_supplier(supplier_id)
    next_del_date = supp.next_delivery_date(order_date)
    return next_del_date
