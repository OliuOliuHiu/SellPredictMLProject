import pandas as pd
import pymysql

# Đọc file CSV
file_path = "./Data/Pizza_Cleaned.csv"
df = pd.read_csv(file_path)

# Thông tin kết nối MySQL
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "pizzamanager"
}

conn = None
cursor = None

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS pizza_data (
        order_id INT,
        pizza_id VARCHAR(255),
        quantity INT,
        order_date DATE,
        order_time TIME,
        unit_price FLOAT,
        discount FLOAT,
        total_price FLOAT,
        pizza_size INT,
        pizza_category INT,
        pizza_ingredients TEXT,
        pizza_name VARCHAR(255),
        total_cost FLOAT,
        is_holiday INT,
        time_period INT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    insert_query = """
    INSERT INTO pizza_data (order_id, pizza_id, quantity, order_date, order_time, unit_price, discount, total_price,
                            pizza_size, pizza_category, pizza_ingredients, pizza_name, total_cost, 
                            is_holiday, time_period)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    data = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(insert_query, data)
    conn.commit()

    print("Dữ liệu đã được nạp thành công vào MySQL!")

except Exception as err:
    print(f"Lỗi khi kết nối hoặc ghi dữ liệu: {err}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
