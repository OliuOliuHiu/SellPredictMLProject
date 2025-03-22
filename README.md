🍕 Pizza Sales Analysis and Prediction System
This Python-based project analyzes pizza sales data, provides statistical insights, and builds machine learning models to predict outcomes. It features a user-friendly GUI for administrators and analysts, enabling seamless data access, interaction, and visualization.

**📁 Project Structure**
Edit
├── App.py                         # Main entry point of the application
├── LICENSE                        # Project license
├── README.md                      # Project documentation
│
├── Connectors/                   # Modules for database connection
│   ├── AdminConnector.py
│   ├── Connector.py
│
├── Data/                         # Data files used in the project
│   ├── Pizza_Cleaned.csv
│   ├── Raw_Data.csv
│   ├── pizza_data.sql
│
├── Models/                       # Model-related logic (prediction/statistics/admin)
│   ├── Admin.py
│   ├── PredictionModel.py
│   ├── Statistic.py
│
├── UI/                           # GUI (PyQt6) components and design
│   ├── FINAL_LOGIN.py/.ui
│   ├── FINAL_MAINWINDOW.py/.ui
│   ├── MainLoginWindow.py
│   ├── MainProgramWindowExt.py
│
├── Images/                       # Folder for storing app images and icons

**🛠 Features**
Login UI: Secure login interface for administrators.

Main Window UI: Displays charts, stats, and prediction tools.

Sales Statistics: Analyze number of orders, revenue, growth trends, cancellations, etc.

ML Models: Predict future performance using machine learning.

Admin Tools: Manage access and oversee system activity.

Database Connectivity: Connects to local or remote pizza sales data.

**💻 Technologies Used**
Python 3.x

PyQt6 for UI

Pandas, NumPy for data handling

Matplotlib / Seaborn for visualization

Scikit-learn for machine learning

SQLite/MySQL (via connectors) for database support

**🚀 Getting Started**
Clone the repository:

git clone https://github.com/yourusername/pizza-sales-analyzer.git
cd pizza-sales-analyzer
Install dependencies:

pip install -r requirements.txt
Run the app:

python App.py

**📊 Data Overview**

Raw_Data.csv: Unprocessed sales data.

Pizza_Cleaned.csv: Cleaned dataset ready for analysis.

pizza_data.sql: SQL script to recreate the database schema.

**🧠 Machine Learning**
The PredictionModel.py module handles:

Model training

Evaluation

Predictions for future orders or revenues

📈 Statistics
The Statistic.py module provides functions for:

Sales analysis

Cancellations per category

Revenue per year/product

**👨‍💼 Admin Module**
Admin.py manages:

User roles

Permissions

Secure access

**📌 Notes**
Ensure your Python environment has all dependencies.

Compatible with Windows, macOS, and Linux.

All .ui files are editable via Qt Designer.



