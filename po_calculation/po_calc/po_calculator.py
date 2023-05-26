from datetime import datetime, timedelta
from delivery_date import SupplierManager
from inventory import InventoryManager
import json
import numpy as np
import math
from scipy import stats

from datetime import datetime
import json
import math
import numpy as np
from scipy import stats


class POCalculator:
    def __init__(self):
        self.inventory_manager = InventoryManager()
        self.supplier_manager = SupplierManager()

    def reorder_point_reached(self, sku):
        # Load current inventory level
        current_inventory = self.inventory_manager.get_inventory(sku)

        # Calculate next delivery date and next to next delivery date
        supplier = self.supplier_manager.get_supplier(sku)
        order_date = datetime.now().strftime("%Y-%m-%d")
        next_delivery_date = supplier.next_delivery_date(order_date)
        n2n_delivery_date = supplier.n2n_delivery_date(order_date)

        # Calculate cover period
        next_delivery_date = datetime.strptime(next_delivery_date, "%Y-%m-%d")
        n2n_delivery_date = datetime.strptime(n2n_delivery_date, "%Y-%m-%d")
        cover_period = (n2n_delivery_date - datetime.now()).days

        # Get forecast for cover period
        with open('forecast_data.json', 'r') as f:
            forecast_data = json.load(f)[sku]
        forecast_for_cover_period = sum(forecast_data[:cover_period])

        # Get safety stock for SKU for the given cover period
        safety_stock_value = self.safety_stock(sku, cover_period)

        # Check if reorder point is reached
        return current_inventory <= forecast_for_cover_period + safety_stock_value

    def safety_stock(self, sku, cover_period):
        # Assuming you have a function to get the standard deviation of the forecast
        std_dev_forecast = self.get_standard_deviation_of_forecast(sku, cover_period)

        # Assuming a constant z-score for the desired service level (for example, 1.65 for 95% service level)
        z_score = 1.65

        # Calculate safety stock
        safety_stock_value = z_score * std_dev_forecast

        return safety_stock_value

    def get_po_quantity(self, sku):
        # Add your logic to calculate the purchase order quantity for the given SKU code
        # Example: use reorder point, safety stock, and demand forecast
        current_inventory = self.inventory_manager.get_inventory(sku)

        # Calculate next delivery date and next to next delivery date
        supplier = self.supplier_manager.get_supplier(sku)
        order_date = datetime.now().strftime("%Y-%m-%d")
        next_delivery_date = supplier.next_delivery_date(order_date)
        n2n_delivery_date = supplier.n2n_delivery_date(order_date)

        # Calculate cover period
        next_delivery_date = datetime.strptime(next_delivery_date, "%Y-%m-%d")
        n2n_delivery_date = datetime.strptime(n2n_delivery_date, "%Y-%m-%d")
        cover_period = (n2n_delivery_date - datetime.now()).days

        # Get forecast for cover period
        with open('forecast_data.json', 'r') as f:
            forecast_data = json.load(f)[sku]
        forecast_for_cover_period = sum(forecast_data[:cover_period])

        # Get safety stock for SKU for the given cover period
        safety_stock_value = self.safety_stock(sku, cover_period)

        # Check if reorder point is reached
        return  forecast_for_cover_period + safety_stock_value - current_inventory

    def get_standard_deviation_of_forecast(self, sku, cover_period):
        # Load sales and forecast data
        with open('sales_data.json', 'r') as f:
            sales_data = json.load(f)
        with open('forecast_data.json', 'r') as f:
            forecast_data = json.load(f)

        # Get sales and forecast for the given SKU for the last month (30 days)
        sku_sales = sales_data[str(sku)][:30]
        sku_forecast = forecast_data[str(sku)][:30]

        # Calculate daily difference between sales and forecast
        daily_difference = [sales - forecast for sales, forecast in zip(sku_sales, sku_forecast)]

        # Calculate standard deviation of the daily difference
        std_dev_difference = np.std(daily_difference)

        # Multiply standard deviation by the square root of the cover period
        adjusted_std_dev = std_dev_difference * math.sqrt(cover_period)

        return adjusted_std_dev

    def get_bias_and_significance(self, sku, alpha=0.05):
        # Load sales and forecast data
        with open('sales_data.json', 'r') as f:
            sales_data = json.load(f)
        with open('forecast_data.json', 'r') as f:
            forecast_data = json.load(f)

        # Get sales and forecast for the given SKU for the last month (30 days)
        sku_sales = sales_data[str(sku)][:30]
        sku_forecast = forecast_data[str(sku)][:30]

        # Calculate daily difference between sales and forecast
        daily_difference = [sales - forecast for sales, forecast in zip(sku_sales, sku_forecast)]

        # Calculate bias (mean difference)
        bias = np.mean(daily_difference)

        # Perform paired t-test
        t_stat, p_value = stats.ttest_rel(sku_sales, sku_forecast)

        # Check if the bias is statistically significant
        significant = p_value < alpha

        return bias, significant