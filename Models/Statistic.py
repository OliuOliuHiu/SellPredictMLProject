from Connectors.Connector import Connector
from .PredictionModel import PredictionModel
import pandas as pd

class Statistic(Connector):
    def __init__(self):
        super().__init__()
        self.cursor = self.connect()
        self.df = self.load_data('pizza_data')
        self.original_df = self.df.copy() if self.df is not None else None
        self.model = PredictionModel()
        self.model.set_original_data(self.original_df)

    def load_data(self, table_name):
        print(f"Loading data from table '{table_name}'...")
        sql = f"SELECT * FROM {table_name};"
        df = self.queryDataset(sql)
        if df is not None:
            print(f"Loaded {len(df)} records from the '{table_name}' table.")
            print("Columns in DataFrame:", df.columns.tolist())
            print("Unique values in pizza_name:", df["pizza_name"].unique())
            print("Unique values in pizza_category:", df["pizza_category"].unique())
            print("Unique values in pizza_size:", df["pizza_size"].unique())
            print("Unique values in unit_price:", df["unit_price"].unique())
            print("Unique values in discount:", df["discount"].unique())
            print("Unique values in quantity:", df["quantity"].unique())
            print("Unique values in is_holiday:", df["is_holiday"].unique())
            print("Unique values in time_period:", df["time_period"].unique())
            print("Distribution of quantity:")
            print(df["quantity"].value_counts())
            print("Average quantity by pizza_name:")
            print(df.groupby("pizza_name")["quantity"].mean())
            print("Average quantity by time_period:")
            print(df.groupby("time_period")["quantity"].mean())
            print("Average quantity by is_holiday:")
            print(df.groupby("is_holiday")["quantity"].mean())
            print("Average quantity by unit_price:")
            print(df.groupby("unit_price")["quantity"].mean())
            print("Average quantity by discount:")
            print(df.groupby("discount")["quantity"].mean())
            print("Correlation with quantity:")
            print(df[['quantity', 'pizza_category', 'pizza_size', 'unit_price', 'discount', 'total_cost', 'is_holiday', 'time_period']].corr()['quantity'])
            if (df["total_cost"] < 0).any():
                print("Warning: Negative total_cost values detected in the database:")
                print(df[df["total_cost"] < 0][["order_date", "pizza_name", "total_cost"]])
            if (df["unit_price"] < 0).any():
                print("Warning: Negative unit_price values detected:")
                print(df[df["unit_price"] < 0][["order_date", "pizza_name", "unit_price"]])
            if (df["quantity"] < 0).any():
                print("Warning: Negative quantity values detected:")
                print(df[df["quantity"] < 0][["order_date", "pizza_name", "quantity"]])
            if (df["discount"] < 0).any() or (df["discount"] > 1).any():
                print("Warning: Invalid discount values detected (should be between 0 and 1):")
                print(df[(df["discount"] < 0) | (df["discount"] > 1)][["order_date", "pizza_name", "discount"]])

            try:
                df['order_date'] = pd.to_datetime(df['order_date'])
            except Exception as e:
                print(f"Error converting order_date to datetime: {e}")
                raise ValueError("Failed to convert order_date to datetime format.")

            return df
        else:
            print(f"Failed to load data from table '{table_name}'.")
            raise ValueError(f"Không thể truy xuất dữ liệu từ bảng {table_name}. Hãy kiểm tra lại tên bảng hoặc kết nối DB.")

    def train_model(self, train_size=0.8):
        return self.model.train_model(self.df, train_size=train_size)

    def get_metrics(self):
        return self.model.get_metrics()

    def get_feature_importances(self):
        return self.model.get_feature_importances()

    def predict_quantity(self, product, time_period, is_holiday, pizza_category, pizza_size, unit_price, discount, from_date, to_date):
        return self.model.predict_quantity(product, time_period, is_holiday, pizza_category, pizza_size, unit_price, discount, from_date, to_date)

    def get_data_in_range(self, product, from_date, to_date):
        try:
            if self.original_df is None or self.original_df.empty:
                print("No data available in original DataFrame.")
                return [], [], [], []

            if not pd.api.types.is_datetime64_any_dtype(self.original_df["order_date"]):
                self.original_df['order_date'] = pd.to_datetime(self.original_df['order_date'])

            mask = (self.original_df["pizza_name"] == product) & (self.original_df["order_date"] >= from_date) & (self.original_df["order_date"] <= to_date)
            filtered_df = self.original_df[mask].copy()

            if filtered_df.empty:
                print(f"No data found for product '{product}' between {from_date} and {to_date}.")
                return [], [], [], []

            aggregated_df = filtered_df.groupby("order_date").agg({
                "total_price": "sum",
                "total_cost": "sum",
                "quantity": "sum"
            }).reset_index()

            aggregated_df.sort_values("order_date", inplace=True)

            dates = aggregated_df["order_date"].dt.strftime("%d/%m/%Y").tolist()
            revenues = aggregated_df["total_price"].tolist()
            costs = aggregated_df["total_cost"].tolist()
            quantities = aggregated_df["quantity"].tolist()

            return dates, revenues, costs, quantities
        except Exception as e:
            print(f"Error in get_data_in_range: {e}")
            return [], [], [], []