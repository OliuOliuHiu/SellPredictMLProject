from PyQt6 import QtWidgets
from UI.FINAL_MAINWINDOW import Ui_MainWindow
from Models.Statistic import Statistic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime

class MainProgramWindowExt(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Initialize the Statistic model
        self.statistic_model = Statistic()

        # Populate comboboxes with values from data
        if not self.statistic_model.df.empty:
            # Populate product types
            product_types = self.statistic_model.df["pizza_name"].unique().tolist()
            self.cbolistTypeofProduct.addItems(product_types)

            # Populate pizza categories (as strings)
            pizza_categories = [str(cat) for cat in self.statistic_model.df["pizza_category"].unique()]
            self.cboIsHoliday_2.clear()
            self.cboIsHoliday_2.addItems(pizza_categories)

            # Populate pizza sizes (as strings)
            pizza_sizes = [str(size) for size in self.statistic_model.df["pizza_size"].unique()]
            self.cboIsHoliday_3.clear()
            self.cboIsHoliday_3.addItems(pizza_sizes)

            # Populate time periods
            time_periods = self.statistic_model.df["time_period"].unique().tolist()
            time_period_mapping = {1: 'Morning', 2: 'Afternoon', 4: 'Evening'}
            time_periods = [time_period_mapping.get(tp, str(tp)) for tp in time_periods]
            self.cboPeriod.addItems(time_periods)

            # Populate is_holiday
            self.cboIsHoliday.addItems(["Yes", "No"])
        else:
            print("No data available to populate comboboxes.")

        # Set up the tableWidgetStatistic_Predict with 9 columns to include Total Cost
        self.tableWidgetStatistic_Predict.setColumnCount(9)
        self.tableWidgetStatistic_Predict.setHorizontalHeaderLabels([
            "Product Type", "Pizza Category", "Pizza Size", "Unit Price", "Date",
            "Time Period", "Is Holiday", "Predicted Quantity", "Total Cost"
        ])

        # Initialize plots for Revenue/Cost and Quantity (Statistic tab)
        self.figure_revenue = Figure()
        self.canvas_revenue = FigureCanvas(self.figure_revenue)
        self.verticalLayoutPlot_2.addWidget(self.canvas_revenue)

        self.figure_quantity = Figure()
        self.canvas_quantity = FigureCanvas(self.figure_quantity)
        self.verticalLayoutPlot_3.addWidget(self.canvas_quantity)

        # Initialize plot for Prediction tab
        self.figure_prediction = Figure()
        self.canvas_prediction = FigureCanvas(self.figure_prediction)
        self.verticalLayoutPlot_6.addWidget(self.canvas_prediction)

        # Connect the Execute button (Statistic tab)
        self.pushButtonExecute.clicked.connect(self.update_statistic_tab)

        # Connect the Predict button (Prediction tab)
        self.pushButtonPredict.clicked.connect(self.update_prediction_tab)

        # Connect the Train button (Prediction tab)
        self.pushButtonPredict_4.clicked.connect(self.train_model)

        # Connect the Evaluate button (Prediction tab)
        self.pushButtonPredict_3.clicked.connect(self.evaluate_model)

    def train_model(self):
        try:
            # Get train and test sizes from UI
            train_size = int(self.lineEditTestSize_2.text()) / 100  # Train Size in percentage
            test_size = int(self.lineEditTestSize.text()) / 100  # Test Size in percentage

            # Validate train and test sizes
            if train_size + test_size != 1.0:
                QtWidgets.QMessageBox.warning(self.MainWindow, "Invalid Input",
                                              "Train Size and Test Size must sum to 100%.")
                return

            # Train the model
            success = self.statistic_model.train_model(train_size=train_size)
            if success:
                QtWidgets.QMessageBox.information(self.MainWindow, "Success", "Model has been trained successfully.")
            else:
                QtWidgets.QMessageBox.critical(self.MainWindow, "Error", "Failed to train model.")
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self.MainWindow, "Invalid Input",
                                          "Train Size and Test Size must be valid numbers.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.MainWindow, "Error", f"Failed to train model: {str(e)}")

    def evaluate_model(self):
        try:
            # Get evaluation metrics
            metrics = self.statistic_model.get_metrics()
            if not metrics:
                QtWidgets.QMessageBox.warning(self.MainWindow, "No Metrics",
                                              "Please train the model first.")
                return

            # Display metrics on the UI
            self.lineEdit_9.setText(str(round(metrics["MAE"], 4)))  # MAE
            self.lineEdit_10.setText(str(round(metrics["MSE"], 4)))  # MSE
            self.lineEdit_11.setText(str(round(metrics["RMSE"], 4)))  # RMSE
            self.lineEdit_12.setText(str(round(metrics["R2"], 4)))  # R2 Score

            # Display feature importances in a message box
            feature_importances = self.statistic_model.get_feature_importances()
            if feature_importances:
                importance_text = "Feature Importances:\n"
                for feature, importance in feature_importances.items():
                    importance_text += f"{feature}: {importance:.4f}\n"
                QtWidgets.QMessageBox.information(self.MainWindow, "Feature Importances", importance_text)

            QtWidgets.QMessageBox.information(self.MainWindow, "Success", "Model evaluation metrics updated.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.MainWindow, "Error", f"Failed to evaluate model: {str(e)}")

    def update_statistic_tab(self):
        # Get inputs from the UI
        pizza_name = self.listProduct.currentText()
        from_day = self.spinBox.value()
        from_month = self.spinBox_3.value()
        to_day = self.spinBox_2.value()
        to_month = self.spinBox_4.value()

        # Define the date range (assume year 2015 as in UI)
        try:
            from_date = pd.to_datetime(f"2015-{from_month}-{from_day}")
            to_date = pd.to_datetime(f"2015-{to_month}-{to_day}")
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self.MainWindow, "Invalid Date",
                                          "Please enter a valid date range.")
            return

        # Ensure from_date is before to_date
        if from_date > to_date:
            QtWidgets.QMessageBox.warning(self.MainWindow, "Invalid Date Range",
                                          "The 'From' date must be before the 'To' date.")
            return

        # Get data in range
        dates, revenues, costs, quantities = self.statistic_model.get_data_in_range(pizza_name, from_date, to_date)

        if not dates:
            QtWidgets.QMessageBox.information(self.MainWindow, "No Data",
                                              "No data available for the selected product and date range.")
            # Clear the table and plots
            self.tableWidgetStatistic.setRowCount(0)
            self.figure_revenue.clear()
            self.canvas_revenue.draw()
            self.figure_quantity.clear()
            self.canvas_quantity.draw()
            return

        # Update the table
        self.tableWidgetStatistic.setRowCount(len(dates))
        for row, (date, revenue, cost, quantity) in enumerate(zip(dates, revenues, costs, quantities)):
            self.tableWidgetStatistic.setItem(row, 0, QtWidgets.QTableWidgetItem(pizza_name))
            self.tableWidgetStatistic.setItem(row, 1, QtWidgets.QTableWidgetItem(date))
            self.tableWidgetStatistic.setItem(row, 2, QtWidgets.QTableWidgetItem(str(revenue)))
            self.tableWidgetStatistic.setItem(row, 3, QtWidgets.QTableWidgetItem(str(cost)))
            self.tableWidgetStatistic.setItem(row, 4, QtWidgets.QTableWidgetItem(str(quantity)))

        # Update the revenue and cost plot
        self.figure_revenue.clear()
        ax1 = self.figure_revenue.add_subplot(111)
        ax1.plot(dates, revenues, label="Revenue", color="green")
        ax1.plot(dates, costs, label="Cost", color="red")
        ax1.set_title(f"Revenue and Cost of {pizza_name}")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Amount")
        ax1.legend()
        ax1.grid(True)
        self.figure_revenue.autofmt_xdate()
        self.canvas_revenue.draw()

        # Update the quantity plot
        self.figure_quantity.clear()
        ax2 = self.figure_quantity.add_subplot(111)
        ax2.plot(dates, quantities, marker='o', color="blue")
        ax2.set_title(f"Quantity of {pizza_name} Over Time")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Quantity")
        ax2.grid(True)
        self.figure_quantity.autofmt_xdate()
        self.canvas_quantity.draw()

    def update_prediction_tab(self):
        try:
            # Get inputs from the UI
            pizza_name = self.cbolistTypeofProduct.currentText()
            time_period = self.cboPeriod.currentText()
            is_holiday = self.cboIsHoliday.currentText() == "Yes"
            pizza_category = self.cboIsHoliday_2.currentText()  # Should be renamed to cboPizzaCategory in UI
            pizza_size = self.cboIsHoliday_3.currentText()  # Should be renamed to cboPizzaSize in UI
            unit_price = self.lineEdit.text()
            discount = self.lineEdit_2.text()
            from_day = self.spinBoxFromDay.value()
            from_month = self.spinBoxFromMonth.value()
            to_day = self.spinBoxToDay.value()
            to_month = self.spinBoxToMonth.value()

            # Validate unit_price and discount
            try:
                unit_price = float(unit_price) if unit_price else 0.0
            except ValueError:
                QtWidgets.QMessageBox.warning(self.MainWindow, "Invalid Input", "Unit Price must be a number.")
                return

            try:
                discount = float(discount) if discount else 0.0
            except ValueError:
                QtWidgets.QMessageBox.warning(self.MainWindow, "Invalid Input", "Discount must be a number.")
                return

            # Define the date range (year 2016 as in UI)
            try:
                from_date = pd.to_datetime(f"2016-{from_month}-{from_day}")
                to_date = pd.to_datetime(f"2016-{to_month}-{to_day}")
            except ValueError as e:
                QtWidgets.QMessageBox.warning(self.MainWindow, "Invalid Date", "Please enter a valid date range.")
                return

            # Ensure from_date is before to_date
            if from_date > to_date:
                QtWidgets.QMessageBox.warning(self.MainWindow, "Invalid Date Range",
                                              "The 'From' date must be before the 'To' date.")
                return

            # Predict quantities
            predictions = self.statistic_model.predict_quantity(
                pizza_name, time_period, is_holiday, pizza_category, pizza_size, unit_price, discount, from_date, to_date
            )

            # Check if predictions are empty
            if not predictions:
                QtWidgets.QMessageBox.information(self.MainWindow, "No Prediction",
                                                  "Could not predict quantities for the given inputs.")
                self.tableWidgetStatistic_Predict.setRowCount(0)
                self.figure_prediction.clear()
                self.canvas_prediction.draw()
                return

            # Update the table with floating-point quantities
            self.tableWidgetStatistic_Predict.setRowCount(len(predictions))
            for row, (date, quantity, pred_pizza_category, pred_pizza_size, pred_unit_price, pred_discount,
                      pred_total_cost) in enumerate(predictions):
                self.tableWidgetStatistic_Predict.setItem(row, 0, QtWidgets.QTableWidgetItem(pizza_name))
                self.tableWidgetStatistic_Predict.setItem(row, 1, QtWidgets.QTableWidgetItem(str(pred_pizza_category)))
                self.tableWidgetStatistic_Predict.setItem(row, 2, QtWidgets.QTableWidgetItem(str(pred_pizza_size)))
                self.tableWidgetStatistic_Predict.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{pred_unit_price:.2f}"))
                self.tableWidgetStatistic_Predict.setItem(row, 4, QtWidgets.QTableWidgetItem(date.strftime("%Y-%m-%d")))
                self.tableWidgetStatistic_Predict.setItem(row, 5, QtWidgets.QTableWidgetItem(time_period))
                self.tableWidgetStatistic_Predict.setItem(row, 6,
                                                          QtWidgets.QTableWidgetItem("Yes" if is_holiday else "No"))
                self.tableWidgetStatistic_Predict.setItem(row, 7, QtWidgets.QTableWidgetItem(f"{quantity:.2f}"))
                self.tableWidgetStatistic_Predict.setItem(row, 8,
                                                          QtWidgets.QTableWidgetItem(f"{pred_total_cost:.2f}"))

            # Sum daily predictions by month for the plot
            pred_df = pd.DataFrame(predictions, columns=['date', 'quantity', 'category', 'size', 'unit_price', 'discount', 'total_cost'])
            pred_df['date'] = pd.to_datetime(pred_df['date'])
            pred_df['month'] = pred_df['date'].dt.month
            monthly_totals = pred_df.groupby('month')['quantity'].sum().reindex(range(1, 13), fill_value=0)

            # Update the plot as a line chart with monthly totals
            self.figure_prediction.clear()
            ax = self.figure_prediction.add_subplot(111)
            ax.plot(range(1, 13), monthly_totals, marker='o', color='blue', label='Total Predicted Quantity')
            ax.set_title(f"Total Predicted Sales Quantity per Month for {pizza_name} ({time_period})")
            ax.set_xlabel("Month")
            ax.set_ylabel("Total Quantity")
            ax.grid(True)
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels([f"Tháng {m}" for m in range(1, 13)])
            ax.legend()
            self.figure_prediction.tight_layout()
            self.canvas_prediction.draw()

        except Exception as e:
            print(f"Error in update_prediction_tab: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(self.MainWindow, "Error",
                                           f"An error occurred while predicting: {str(e)}")

    def showWindow(self):
        self.MainWindow.show()