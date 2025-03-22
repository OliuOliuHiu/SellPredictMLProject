import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class PredictionModel:
    def __init__(self):
        self.rf_model = None
        self.label_encoders = {}
        self.metrics = {}
        self.feature_importances = None
        self.train_df = None
        self.test_df = None
        self.original_df = None

    def set_original_data(self, original_df):
        self.original_df = original_df.copy() if original_df is not None else None

    def preprocess_data(self, df, fit=False):
        print("Starting preprocess_data...")
        try:
            df = df.copy()
            df = df.drop(['order_id', 'pizza_id', 'pizza_ingredients', 'order_time'], axis=1, errors='ignore')

            df['order_date'] = pd.to_datetime(df['order_date'])
            df['day'] = df['order_date'].dt.day
            df['month'] = df['order_date'].dt.month
            df['year'] = df['order_date'].dt.year
            df['day_of_week'] = df['order_date'].dt.dayofweek

            categorical_columns = ['pizza_name', 'pizza_size', 'pizza_category', 'time_period']
            if fit:
                for col in categorical_columns:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.label_encoders[col] = le
                    print(f"LabelEncoder for {col} fitted with classes: {le.classes_}")
            else:
                for col in categorical_columns:
                    if col not in self.label_encoders:
                        raise ValueError(f"LabelEncoder for {col} not found. Please train the model first.")
                    le = self.label_encoders[col]
                    df[col] = df[col].astype(str).apply(lambda x: x if x in le.classes_ else le.classes_[0])
                    df[col] = le.transform(df[col])

            df['is_holiday'] = df['is_holiday'].astype(int)
            return df
        except Exception as e:
            print(f"Error preprocessing data: {e}")
            return None

    def train_model(self, df, train_size=0.8):
        print("Starting train_model...")
        try:
            if df.empty:
                print("No data available for training.")
                return False

            df = self.preprocess_data(df, fit=True)
            if df is None:
                print("Failed to preprocess data.")
                return False

            X = df.drop(['quantity', 'order_date'], axis=1)
            y = df['quantity']

            self.train_df, self.test_df = train_test_split(df, train_size=train_size, random_state=42)
            X_train = self.train_df.drop(['quantity', 'order_date'], axis=1)
            y_train = self.train_df['quantity']
            X_test = self.test_df.drop(['quantity', 'order_date'], axis=1)
            y_test = self.test_df['quantity']

            print(f"Train set size: {len(self.train_df)}, Test set size: {len(self.test_df)}")

            self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.rf_model.fit(X_train, y_train)
            print("Model trained successfully.")

            features = X_train.columns
            self.feature_importances = dict(zip(features, self.rf_model.feature_importances_))
            print("Feature Importances:")
            for feature, importance in self.feature_importances.items():
                print(f"{feature}: {importance:.4f}")

            y_train_pred = self.rf_model.predict(X_train)
            y_train_pred = np.round(y_train_pred).astype(int)
            y_train_pred = np.maximum(0, y_train_pred)
            train_mae = mean_absolute_error(y_train, y_train_pred)
            print(f"Training MAE: {train_mae:.4f}")

            y_pred = self.rf_model.predict(X_test)
            y_pred = np.round(y_pred).astype(int)
            y_pred = np.maximum(0, y_pred)

            self.metrics["MAE"] = mean_absolute_error(y_test, y_pred)
            self.metrics["MSE"] = mean_squared_error(y_test, y_pred)
            self.metrics["RMSE"] = np.sqrt(self.metrics["MSE"])
            self.metrics["R2"] = r2_score(y_test, y_pred)

            print("Evaluation Metrics:")
            print(f"MAE: {self.metrics['MAE']:.4f}")
            print(f"MSE: {self.metrics['MSE']:.4f}")
            print(f"RMSE: {self.metrics['RMSE']:.4f}")
            print(f"R2 Score: {self.metrics['R2']:.4f}")

            return True
        except Exception as e:
            print(f"Error in train_model: {e}")
            return False

    def get_metrics(self):
        return self.metrics

    def get_feature_importances(self):
        return self.feature_importances

    def predict_quantity(self, product, time_period, is_holiday, pizza_category, pizza_size, unit_price, discount,
                         from_date, to_date):
        print("Starting predict_quantity...")
        if self.rf_model is None:
            print("Error: Model is not trained. Cannot make predictions.")
            return []

        try:
            print(f"Inputs: product={product}, time_period={time_period}, is_holiday={is_holiday}, "
                  f"pizza_category={pizza_category}, pizza_size={pizza_size}, unit_price={unit_price}, "
                  f"discount={discount}, from_date={from_date}, to_date={to_date}")

            time_period_mapping = {'Morning': 1, 'Afternoon': 2, 'Evening': 4}
            if time_period not in time_period_mapping:
                print(f"Invalid time_period value: {time_period}. Using default value 0.")
                time_period_value = 0
            else:
                time_period_value = time_period_mapping[time_period]
            print(f"Time period mapped value: {time_period_value}")

            is_holiday_val = 1 if is_holiday else 0
            print(f"Is holiday value: {is_holiday_val}")

            date_range = pd.date_range(start=from_date, end=to_date, freq="D")
            print(f"Date range: {date_range}")

            unit_price_val = float(unit_price) if unit_price else 0.0
            discount_val = float(discount) if discount else 0.0
            total_cost = unit_price_val * (1 - discount_val)
            print(f"Unit price: {unit_price_val}, Discount: {discount_val}, Total cost: {total_cost}")

            # Encode input parameters directly
            print("Encoding input parameters...")
            if 'pizza_name' not in self.label_encoders:
                print("Error: LabelEncoder for pizza_name not found.")
                return []
            print(f"Available pizza_name classes: {self.label_encoders['pizza_name'].classes_}")
            if product not in self.label_encoders['pizza_name'].classes_:
                print(
                    f"Warning: Product '{product}' not seen during training. Using first class: {self.label_encoders['pizza_name'].classes_[0]}")
                product = self.label_encoders['pizza_name'].classes_[0]
            pizza_name_encoded = self.label_encoders['pizza_name'].transform([product])[0]
            print(f"Encoded pizza_name: {pizza_name_encoded}")

            if 'pizza_size' not in self.label_encoders:
                print("Error: LabelEncoder for pizza_size not found.")
                return []
            print(f"Available pizza_size classes: {self.label_encoders['pizza_size'].classes_}")
            pizza_size_str = str(pizza_size)
            if pizza_size_str not in self.label_encoders['pizza_size'].classes_:
                print(
                    f"Warning: Pizza size '{pizza_size_str}' not seen during training. Using first class: {self.label_encoders['pizza_size'].classes_[0]}")
                pizza_size_str = self.label_encoders['pizza_size'].classes_[0]
            pizza_size_encoded = self.label_encoders['pizza_size'].transform([pizza_size_str])[0]
            print(f"Encoded pizza_size: {pizza_size_encoded}")

            if 'pizza_category' not in self.label_encoders:
                print("Error: LabelEncoder for pizza_category not found.")
                return []
            print(f"Available pizza_category classes: {self.label_encoders['pizza_category'].classes_}")
            pizza_category_str = str(pizza_category)
            if pizza_category_str not in self.label_encoders['pizza_category'].classes_:
                print(
                    f"Warning: Pizza category '{pizza_category_str}' not seen during training. Using first class: {self.label_encoders['pizza_category'].classes_[0]}")
                pizza_category_str = self.label_encoders['pizza_category'].classes_[0]
            pizza_category_encoded = self.label_encoders['pizza_category'].transform([pizza_category_str])[0]
            print(f"Encoded pizza_category: {pizza_category_encoded}")

            if 'time_period' not in self.label_encoders:
                print("Error: LabelEncoder for time_period not found.")
                return []
            print(f"Available time_period classes: {self.label_encoders['time_period'].classes_}")
            time_period_str = str(time_period_value)
            if time_period_str not in self.label_encoders['time_period'].classes_:
                print(
                    f"Warning: Time period '{time_period_str}' not seen during training. Using first class: {self.label_encoders['time_period'].classes_[0]}")
                time_period_str = self.label_encoders['time_period'].classes_[0]
            time_period_encoded = self.label_encoders['time_period'].transform([time_period_str])[0]
            print(f"Encoded time_period: {time_period_encoded}")

            predictions = []
            for date in date_range:
                day = date.day
                month_val = date.month
                year_val = date.year
                day_of_week = date.dayofweek

                input_data = pd.DataFrame({
                    'unit_price': [unit_price_val],
                    'discount': [discount_val],
                    'total_price': [unit_price_val * (1 - discount_val)],
                    'pizza_size': [pizza_size_encoded],
                    'pizza_category': [pizza_category_encoded],
                    'pizza_name': [pizza_name_encoded],
                    'total_cost': [total_cost],
                    'is_holiday': [is_holiday_val],
                    'time_period': [time_period_encoded],
                    'day': [day],
                    'month': [month_val],
                    'year': [year_val],
                    'day_of_week': [day_of_week]
                })

                predicted_quantity = self.rf_model.predict(input_data)[0]
                predicted_quantity = max(0, predicted_quantity)
                predictions.append(
                    (date, predicted_quantity, pizza_category, pizza_size, unit_price, discount, total_cost))

            print(f"Predictions generated: {len(predictions)} entries")
            return predictions

        except Exception as e:
            print(f"Error in predict_quantity: {str(e)}")
            return []