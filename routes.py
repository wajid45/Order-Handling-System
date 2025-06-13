from flask import Blueprint, render_template, request, redirect
from db import get_connection, log_action

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    cursor.close()
    return render_template('dashboard.html', orders=orders, logs=logs)

@main_routes.route('/add', methods=['POST'])
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
    cursor.close()
    log_action("Created Order")
    return redirect('/')

@main_routes.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute('''
            UPDATE orders SET num_items = %s, delivery_date = %s, sender_name = %s, recipient_name = %s, recipient_address = %s
            WHERE id = %s
            ''', (request.form['num_items'], request.form['delivery_date'], request.form['sender_name'], request.form['recipient_name'], request.form['recipient_address'], id ))
        conn.commit()
        log_action(f"Edited Order #{id}")
        cursor.close()
        return redirect('/')
    else:
        cursor.execute("SELECT * FROM orders WHERE id = %s", (id,))
        order = cursor.fetchone()
        cursor.close()
        return render_template('edit.html', order=order)

@main_routes.route('/delete/<int:id>')
def delete_order(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    log_action(f"Deleted Order #{id}")
    return redirect('/')

@main_routes.route('/deliver/<int:id>')
def mark_delivered(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = 'Delivered' WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    log_action(f"Marked Delivered Order #{id}")
    return redirect('/')