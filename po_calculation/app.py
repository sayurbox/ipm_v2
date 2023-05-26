from datetime import date
from flask import Flask, jsonify, request, render_template
from delivery_date.leadtime import next_delivery_date_api
from delivery_date.supplier import SupplierManager, JsonSupplierLoader, Supplier
from po_calculator import get_proposed_po_quantity
import generate_test_data as gtd
from inventory.inventory import JsonInventoryLoader, InventoryManager

app = Flask(__name__)

#############
#
#test data setup
#
#
#############

inventory_file_path = 'inventory_data.json'
sku_file_path = 'skudata.json'
supplier_file_path = 'supplier_lead_times.json'
sku_supplier_mapping_file = 'sku_supplier_mapping.json'
sales_file_path = 'sales_data.json'
sku_count = 100
num_days = 60

json_loader = JsonInventoryLoader(inventory_file_path)
inventory_manager = InventoryManager(json_loader)

sku = '507602'
inventory_item = inventory_manager.get_inventory(sku)
#print(inventory_item.quantity)


json_loader = JsonSupplierLoader(supplier_file_path)
supplier_manager = SupplierManager(json_loader)
sku_codes = gtd.load_or_generate_sku_codes(sku_file_path,sku_count)
sku_supplier_mapping = gtd.assign_suppliers_to_skus(sku_codes,supplier_manager,sku_supplier_mapping_file)

order_date = date(2023, 12, 1)
supplier_id = 'G7H8I9'

supplier = supplier_manager.get_supplier(supplier_id)
next_delivery = supplier.next_delivery_date(order_date)
print("test for next delibvery date:- " +supplier_id +"  " +next_delivery.strftime('%Y-%m-%d %H:%M'))
gtd.generate_past_sales_data( sku_codes,num_days)

gtd.generate_inventory_data(sku_file_path,sales_file_path,supplier_file_path, sku_supplier_mapping_file, inventory_file_path)

###----------------------------------

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "OK"})

@app.route('/', methods=['GET'])
def index():
    health_status = healthcheck().get_json()
    return render_template('index.html', health_status=health_status)

@app.route('/next_delivery_date/<string:supplier_id>', methods=['GET'])
def next_delivery_date(supplier_id):
    return next_delivery_date_api(supplier_id)  # Use the function

@app.route('/po_quantity/<string:sku_code>', methods=['GET'])
def po_quantity(sku_code):
    quantity = get_proposed_po_quantity(sku_code)
    return jsonify({"sku_code": sku_code, "proposed_po_quantity": quantity})

@app.route('/generate_forecast_data', methods=['GET'])
def get_forecast_data():
    days = 30
    sales_data = gtd.generate_past_sales_data(days)
    forecast_data = gtd.generate_forecast_data(sales_data)
#   save_sales_and_forecast_data(sales_data, forecast_data)
    return jsonify(forecast_data)

# New API to generate sample sales data
@app.route('/generate_sample_sales_data', methods=['GET'])
def generate_sample_sales_data():
    days = 30
    past_sales_data = gtd.generate_past_sales_data(days)
    return jsonify(past_sales_data)

# get SKU codes
@app.route('/get_sku_codes', methods=['GET'])
def get_sku_data():
    count = 100000
    return jsonify(sku_codes)

if __name__ == '__main__':
    app.run(debug=False)
