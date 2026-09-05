import sqlite3
from datetime import datetime

conn = sqlite3.connect("recovery.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT OR REPLACE INTO recovered_payments
    (
        payment_id,
        amount,
        timestamp
    )
    VALUES (?, ?, ?)
""", (
    "PAY001",
    5000,
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
))

conn.commit()

print("PAY001 marked as recovered")

cursor.execute("""
    SELECT payment_id, amount, timestamp
    FROM recovered_payments
""")

rows = cursor.fetchall()

print("\nRecovered payments:")
print(rows)

conn.close()