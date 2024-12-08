import duckdb
import random
import string
from datetime import datetime, timedelta

conn = duckdb.connect("duckdb.servier")

conn.execute(
    """
    CREATE TABLE PRODUCTS (
        product_id INTEGER PRIMARY KEY,
        product_type VARCHAR(20),
        product_name VARCHAR(255)
    );
"""
)

conn.execute(
    """
    CREATE TABLE TRANSACTIONS (
        date DATE,
        order_id INT PRIMARY KEY,
        client_id INT,
        prod_id INT REFERENCES PRODUCTS(product_id),
        prod_price DECIMAL(10, 2),
        prod_qty INT
    );
"""
)


# Function to generate random strings for product names
def random_string(length=10):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


for i in range(1000):
    product_id = i
    product_type = random.choice(["DECO", "MEUBLE"])
    product_name = f"Product {random_string()}"

    conn.execute(
        """
        INSERT INTO PRODUCTS (product_id, product_type, product_name)
        VALUES (?, ?, ?)
    """,
        (product_id, product_type, product_name),
    )


# Helper function to generate a random date between 1 Jan 2019 and 31 Dec 2019
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


# Prepare to generate 10,000 transactions
start_date = datetime(2019, 1, 1)
end_date = datetime(2021, 12, 31)

# Get the list of available product IDs from the PRODUCTS table
prod_ids = conn.execute("SELECT product_id FROM PRODUCTS").fetchall()

# Generate 10,000 random transactions
for order_id in range(1, 10001):
    transaction_date = random_date(start_date, end_date)

    client_id = random.randint(1, 100)

    prod_id = random.choice(prod_ids)[0]

    prod_price = round(random.uniform(1, 100), 2)

    prod_qty = random.randint(1, 15)

    # Insert the transaction into the TRANSACTIONS table
    conn.execute(
        """
        INSERT INTO TRANSACTIONS (date, order_id, client_id, prod_id, prod_price, prod_qty)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (transaction_date, order_id, client_id, prod_id, prod_price, prod_qty),
    )

# Commit and close the connection
conn.commit()
conn.close()

print("10,000 transactions inserted successfully.")
