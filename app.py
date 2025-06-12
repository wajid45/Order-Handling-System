from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="order_db"
    )

def log_action(action, user="System"):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (action, performed_by, timestamp) VALUES (%s, %s, %s)",
                   (action, user, timestamp))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', orders=orders, logs=logs)

@app.route('/add', methods=['POST'])
def add_order():
    data = (
        request.form['num_items'],
        request.form['delivery_date'],
        request.form['sender_name'],
        request.form['recipient_name'],
        request.form['recipient_address']
    )
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (num_items, delivery_date, sender_name, recipient_name, recipient_address)
        VALUES (%s, %s, %s, %s, %s)
    ''', data)
    conn.commit()
    conn.close()
    log_action("Created Order")
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute('''
            UPDATE orders SET num_items = %s, delivery_date = %s, sender_name = %s, recipient_name = %s, recipient_address = %s
            WHERE id = %s
            ''', (request.form['num_items'], request.form['delivery_date'], request.form['sender_name'], request.form['recipient_name'], request.form['recipient_address'], id ))
        conn.commit()
        conn.close()
        log_action(f"Edited Order #{id}")
        return redirect('/')
    else:
        cursor.execute("SELECT * FROM orders WHERE id = %s", (id,))
        order = cursor.fetchone()
        conn.close()
        return render_template('edit.html', order=order)

@app.route('/delete/<int:id>')
def delete_order(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    log_action(f"Deleted Order #{id}")
    return redirect('/')

@app.route('/deliver/<int:id>')
def mark_delivered(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = 'Delivered' WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    log_action(f"Marked Delivered Order #{id}")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
