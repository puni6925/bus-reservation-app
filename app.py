from flask import Flask, render_template, request, redirect, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallbacksecretkey')

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')  # Show login if not logged in
    return render_template('home.html')  # Show home after login

# View All Buses
@app.route('/buses')
def show_buses():
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buses")
    buses = cursor.fetchall()
    conn.close()
    return render_template('buses.html', buses=buses)

# Book a Bus
@app.route('/book', methods=['GET', 'POST'])
def book_bus():
    if request.method == 'POST':
        name = request.form['name']
        bus_id = request.form['bus_id']
        conn = sqlite3.connect('bus.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bookings (name, bus_id) VALUES (?, ?)", (name, bus_id))
        conn.commit()
        conn.close()
        return "Booking Confirmed!"
    return render_template('book.html')

# Search Buses
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        conn = sqlite3.connect('bus.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM buses WHERE source=? AND destination=?", (source, destination))
        results = cursor.fetchall()
        conn.close()
        return render_template('search_result.html', results=results)
    return render_template('search.html')

# Admin Login
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            conn = sqlite3.connect('bus.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings")
            bookings = cursor.fetchall()
            conn.close()
            return render_template('admin_panel.html', bookings=bookings)
        else:
            return "Invalid Credentials"
    return render_template('admin_login.html')

# 404 Error Page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.route('/admin/add_bus', methods=['GET', 'POST'])
def add_bus():
    if request.method == 'POST':
        bus_name = request.form['bus_name']
        source = request.form['source']
        destination = request.form['destination']
        time = request.form['time']
        conn = sqlite3.connect('bus.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO buses (bus_name, source, destination, time) VALUES (?, ?, ?, ?)",
                       (bus_name, source, destination, time))
        conn.commit()
        conn.close()
        return "✅ Bus added successfully!"
    return render_template('add_bus.html')
@app.route('/admin/view_bookings')
def view_bookings():
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bookings.id, bookings.name, buses.bus_name, buses.source, buses.destination, buses.time
        FROM bookings
        JOIN buses ON bookings.bus_id = buses.id
    ''')
    bookings = cursor.fetchall()
    conn.close()
    return render_template('view_bookings.html', bookings=bookings)
@app.route('/admin/delete_bus/<int:bus_id>')
def delete_bus(bus_id):
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM buses WHERE id=?", (bus_id,))
    conn.commit()
    conn.close()
    return redirect('/buses')  # Or to /admin/view_buses if you have that page
@app.route('/admin/edit_bus/<int:bus_id>', methods=['GET', 'POST'])
def edit_bus(bus_id):
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        bus_name = request.form['bus_name']
        source = request.form['source']
        destination = request.form['destination']
        time = request.form['time']
        cursor.execute('''
            UPDATE buses SET bus_name=?, source=?, destination=?, time=?
            WHERE id=?
        ''', (bus_name, source, destination, time, bus_id))
        conn.commit()
        conn.close()
        return redirect('/buses')

    cursor.execute("SELECT * FROM buses WHERE id=?", (bus_id,))
    bus = cursor.fetchone()
    conn.close()
    return render_template('edit_bus.html', bus=bus)
@app.route('/admin/delete_booking/<int:booking_id>')
def delete_booking(booking_id):
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/view_bookings')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':  # ← ✅ POST block starts here
        username = request.form['username']
        password = request.form['password']

        # ✅ You can add this here to ensure the folder exists
        os.makedirs('static/profile_pics', exist_ok=True)

        file = request.files['profile_pic']
        filename = None

        if file and file.filename:
            filename = f"{username}.jpg"
            file.save(os.path.join('static/profile_pics', filename))

        conn = sqlite3.connect('bus.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user:
            return "Username already exists!"
        else:
            cursor.execute("INSERT INTO users (username, password, profile_pic) VALUES (?, ?, ?)",
                           (username, password, filename))
            conn.commit()
            conn.close()
            return redirect('/login')

    return render_template('signup.html')  # ← This runs when it's a GET request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('bus.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/user/dashboard')
        else:
            return "Invalid login credentials!"
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bookings.id, buses.bus_name, buses.source, buses.destination, buses.time
        FROM bookings
        JOIN buses ON bookings.bus_id = buses.id
        WHERE bookings.name = ?
    ''', (session['username'],))
    bookings = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', bookings=bookings)
from openpyxl import Workbook
import os

@app.route('/admin/export_bookings')
def export_bookings():
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bookings.id, bookings.name, buses.bus_name, buses.source, buses.destination, buses.time
        FROM bookings
        JOIN buses ON bookings.bus_id = buses.id
    ''')
    bookings = cursor.fetchall()
    conn.close()

    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Bookings"

    # Header row
    ws.append(['Booking ID', 'User Name', 'Bus Name', 'Source', 'Destination', 'Time'])

    # Add data
    for booking in bookings:
        ws.append(booking)

    # Save file
    file_path = os.path.join("bus_booking_app", "bookings_export.xlsx")
    wb.save(file_path)

    return f"✅ Bookings exported to {file_path}"
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@app.route('/admin/export_bookings_pdf')
def export_bookings_pdf():
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bookings.id, bookings.name, buses.bus_name, buses.source, buses.destination, buses.time
        FROM bookings
        JOIN buses ON bookings.bus_id = buses.id
    ''')
    bookings = cursor.fetchall()
    conn.close()

    file_path = "bus_booking_app/bookings_report.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 40, "Bookings Report")

    c.setFont("Helvetica", 10)
    y = height - 80
    for booking in bookings:
        text = f"ID: {booking[0]} | Name: {booking[1]} | Bus: {booking[2]} | {booking[3]} → {booking[4]} at {booking[5]}"
        c.drawString(30, y, text)
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()

    return f"✅ PDF exported: {file_path}"
@app.route('/user/profile')
def user_profile():
    if 'user_id' not in session:
        return redirect('/login')

    username = session['username']
    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bookings.id, buses.bus_name, buses.source, buses.destination, buses.time
        FROM bookings
        JOIN buses ON bookings.bus_id = buses.id
        WHERE bookings.name = ?
    ''', (username,))
    bookings = cursor.fetchall()
    conn.close()
    return render_template('profile.html', username=username, bookings=bookings)
@app.route('/user/delete_booking/<int:booking_id>')
def user_delete_booking(booking_id):
    if 'username' not in session:
        return redirect('/login')

    username = session['username']

    conn = sqlite3.connect('bus.db')
    cursor = conn.cursor()

    # Only delete if the booking belongs to the logged-in user
    cursor.execute("DELETE FROM bookings WHERE id=? AND name=?", (booking_id, username))
    conn.commit()
    conn.close()
    
    return redirect('/user/profile')

if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
