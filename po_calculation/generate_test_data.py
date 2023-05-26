# sales_data.py
import json
import os
import random
from delivery_date import supplier as sp
sku_file_path = 'skudata.json'
supplier_file_path = 'supplier_lead_times.json'
output_file_path = 'sku_supplier_mapping.json'
num_sku = 100000
sku_codes = None
sales_data = None
def generate_sku_codes(n):
    skus = []
    for _ in range(n):
        sku = random.randint(100000, 999999)
        while sku in skus:
            sku = random.randint(100000, 999999)
        skus.append(sku)
    return skus
def decorate_sku_codes(skus):
    sku_data = {}
    for key in skus:
        shelf_life = random.randint(1, 180)
        yield_factor = round(random.uniform(0.60, 1), 2)
        
        sku_data[key] = {
            "shelf_life": shelf_life,
            "yield_factor": yield_factor
    }
    return sku_data    

    

def load_or_generate_sku_codes(filename, n):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            sku_codes = json.load(file)
    else:
        sku_codes = generate_sku_codes(n)
        sku_data = decorate_sku_codes(sku_codes)
        with open(filename, "w") as file:
            json.dump(sku_data, file, indent= 2)
    return sku_codes

def load_or_generate_sales_data(sales_filename,sku_codes, days, min_avg_sales, max_avg_sales, stdev_factor):
    if os.path.exists(sales_filename):
        with open(sales_filename, "r") as file:
            sales_data = json.load(file)
    else:
        sales_data = generate_sales_data(sku_codes, days, min_avg_sales, max_avg_sales, stdev_factor)
        with open(sales_filename, "w") as file:
            json.dump(sales_data, file)
    return sales_data

def load_or_generate_forecast(filename, n):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            skus = json.load(file)
    else:
        skus = generate_sku_codes(n)
        with open(filename, "w") as file:
            json.dump(skus, file)
    return skus

def generate_sales_data(skus, days, min_avg_sales, max_avg_sales, stdev_factor):
    sales_data = {}
    for sku in skus:
        sku_sales = []
        avg_daily_sales = random.randint(min_avg_sales, max_avg_sales)
        stdev = avg_daily_sales * stdev_factor
        for _ in range(days):
            daily_sales = int(random.gauss(avg_daily_sales, stdev))
            while daily_sales < 0:
                daily_sales = int(random.gauss(avg_daily_sales, stdev))
            sku_sales.append(daily_sales)
        sales_data[str(sku)] = sku_sales
    save_data_to_json(sales_data, 'sales_data.json')    
    return sales_data

def generate_past_sales_data(skus, days = 30):
    sku_filename = 'sku_data.json'
    min_avg_sales = 10
    max_avg_sales = 1000
    stdev_factor = 0.2
    sales_filename = 'sales_data.json'
    sales_data = load_or_generate_sales_data(sales_filename, skus, days, min_avg_sales, max_avg_sales, stdev_factor)
    return sales_data


def generate_forecast_data(sales_data):
    forecast_data = {}
    for sku, daily_sales in sales_data.items():
        forecast_data[sku] = [round(sales * (1 + random.uniform(-0.3, 0.3))) for sales in daily_sales]
    save_data_to_json(forecast_data, 'forecast_data.json')    
    return forecast_data

def save_data_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)

def save_sales_and_forecast_data(sales_data, forecast_data):
    save_data_to_json(sales_data, 'sales_data.json')
    save_data_to_json(forecast_data, 'forecast_data.json')


def assign_suppliers_to_skus(skus, suppManager, output_file):
#    sku_data = load_or_generate_sku_codes(sku_file)
    if os.path.exists(output_file):
        sku_supplier_mapping = load_json_data(output_file)
    else:
        suppliers = suppManager.get_suppliers().keys()
        sku_supplier_mapping = {}
        for sku in skus:
            assigned_supplier = random.choice(list(suppliers))
            sku_supplier_mapping[sku] = assigned_supplier

        with open(output_file, 'w') as f:
            json.dump(sku_supplier_mapping, f, indent=2)    
    return sku_supplier_mapping


def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
def generate_inventory_data(sku_file, sales_file, lead_times_file, sku_supplier_mapping_file, output_file):
    sku_data = load_json_data(sku_file)
    sales_data = load_json_data(sales_file)
    lead_times = load_json_data(lead_times_file)
    sku_supp_map = load_json_data(sku_supplier_mapping_file)

    inventory_data = {}
    for sku in sku_data:
        # Calculate the average daily sales
        daily_sales = sales_data[str(sku)]
        avg_daily_sales = sum(daily_sales) / len(daily_sales)

        # Get the supplier's lead time
        supplier_id = sku_supp_map[str(sku)]
        lead_time = lead_times[supplier_id]['lead_time']

        # Calculate the inventory range
        min_inventory = 0
        max_inventory = int(2 * lead_time * avg_daily_sales)

        # Generate a random inventory value within the range
        inventory_value = random.randint(min_inventory, max_inventory)
        inventory_data[sku] = inventory_value

    with open(output_file, 'w') as f:
        json.dump(inventory_data, f, indent=2)        