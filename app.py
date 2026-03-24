from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import subprocess
import os
import pickle
import base64
import hashlib
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "$C%2#3fvms$qu$@z"  # intentionally weak for CTF
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['DEBUG'] = True  # VULN: Debug mode enabled

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -------------------------------
# User class
# -------------------------------
class User(UserMixin):
    def __init__(self, id, username, role="user", email=""):
        self.id = id
        self.username = username
        self.role = role
        self.email = email

# -------------------------------
# Fake database
# -------------------------------
users = {
    "1": {"username": "alvan", "password": "1234", "role": "user", "email": "alvan@kiboswa.com", "balance": 500},
    "2": {"username": "admin", "password": "admin123", "role": "admin", "email": "admin@kiboswa.com", "balance": 999999}
}

# Updated products with more details
products = {
    "1": {"id": "1", "name": "Men stripped button Front Shirt", "price": 21.99, "rating": 4.9, "image": "product1.jpg", "description": "Classic button-front shirt with stylish stripes", "stock": 50},
    "2": {"id": "2", "name": "Cable Knit Shirt", "price": 21.99, "rating": 4.1, "image": "https://i.pinimg.com/736x/8c/8e/64/8c8e64f0258f1a0d36ca04557dad17e8.jpg", "description": "Warm and comfortable cable knit design", "stock": 35},
    "3": {"id": "3", "name": "Short Sleeve Collar Shirt", "price": 23.99, "rating": 5.0, "image": "https://i.pinimg.com/1200x/71/b8/23/71b8232f72c56411092b6d819403b5fa.jpg", "description": "Perfect for summer days", "stock": 45},
    "4": {"id": "4", "name": "Round Neck Knitted Shirt", "price": 24.99, "rating": 4.7, "image": "https://i.pinimg.com/1200x/33/db/d1/33dbd169e15c3c1d666c348d7d6b7d48.jpg", "description": "Soft knitted fabric with round neck", "stock": 40},
    "5": {"id": "5", "name": "Men's Vintage Floral Retro", "price": 27.99, "rating": 4.5, "image": "https://i.pinimg.com/1200x/9a/58/60/9a58604f2f408c9ce0623d6fd0a31e2a.jpg", "description": "Retro floral pattern", "stock": 30},
    "6": {"id": "6", "name": "Men Floral Print", "price": 24.99, "rating": 4.9, "image": "https://i.pinimg.com/736x/6b/9c/2e/6b9c2e4b70d5dada06e298fb2a71d11c.jpg", "description": "Modern floral print design", "stock": 55},
    "7": {"id": "7", "name": "Men Paisley Print Shirt", "price": 23.99, "rating": 4.7, "image": "https://i.pinimg.com/1200x/a6/21/3f/a6213fe3eb13f9ff9852937b15f0213f.jpg", "description": "Elegant paisley pattern", "stock": 38},
    "8": {"id": "8", "name": "Men Graphic Print Shirt", "price": 21.99, "rating": 4.6, "image": "https://i.pinimg.com/1200x/8b/38/bb/8b38bbac8a5e7506688494962bc5c0c4.jpg", "description": "Bold graphic print", "stock": 42},
    "9": {"id": "9", "name": "Men's Denim Shirt", "price": 22.99, "rating": 4.7, "image": "https://i.pinimg.com/736x/db/81/03/db8103f493a381facbc7bfd6eb6bc17d.jpg", "description": "Classic denim shirt", "stock": 33},
    "10": {"id": "10", "name": "Men Skull Graphic Shirt", "price": 26.99, "rating": 4.8, "image": "https://i.pinimg.com/1200x/97/d6/3d/97d63d96cebf86324d734c9777f9a7ef.jpg", "description": "Edgy skull design", "stock": 28},
    "11": {"id": "11", "name": "Plain Black Denim Jacket", "price": 28.99, "rating": 4.7, "image": "https://i.pinimg.com/1200x/1b/b4/59/1bb45918fc4fd96f52d385414c2ae6f9.jpg", "description": "Versatile black denim jacket", "stock": 25},
    "12": {"id": "12", "name": "Blue Denim Jacket", "price": 29.99, "rating": 5.0, "image": "https://i.pinimg.com/736x/3c/c3/b8/3cc3b81e4d594754c3584c3aa1db60d8.jpg", "description": "Classic blue denim jacket", "stock": 32}
}

# Cart storage (in-memory for demo)
carts = {}

# Orders storage
orders_db = {}

# Store for XSS messages
xss_messages = []

# Reset tokens storage
reset_tokens = {}

# Initialize SQLite for additional challenges
def init_sqlite_db():
    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_sql (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            is_admin INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            username TEXT,
            message TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products_sql (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            secret_flag TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM users_sql")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users_sql VALUES (1, 'alvan', '1234', 'alvan@kiboswa.com', 0)")
        cursor.execute("INSERT INTO users_sql VALUES (2, 'admin', 'admin123', 'admin@kiboswa.com', 1)")
        cursor.execute("INSERT INTO users_sql VALUES (3, 'test_user', 'password', 'test@example.com', 0)")
        cursor.execute("INSERT INTO products_sql VALUES (1, 'SQLi Practice Product', 19.99, 'FTA{sql1nj3ct10n_fl4g}')")
        cursor.execute("INSERT INTO products_sql VALUES (2, 'Hidden Product', 999.99, 'FTA{4n0th3r_s3cr3t}')")
    
    conn.commit()
    conn.close()

init_sqlite_db()

# -------------------------------
# User loader for Flask-Login
# -------------------------------
@login_manager.user_loader
def load_user(user_id):
    user_info = users.get(user_id)
    if user_info:
        return User(id=user_id, username=user_info["username"], role=user_info.get("role", "user"), email=user_info.get("email", ""))
    return None

# -------------------------------
# Main Routes (Public)
# -------------------------------
@app.route("/")
def index():
    # Public homepage without login
    featured_products = list(products.values())[:6]
    return render_template("index.html", products=featured_products)

@app.route("/products")
def products_page():
    # Public products page without login
    return render_template("products.html", products=products.values())

@app.route("/product/<product_id>")
def product_detail(product_id):
    product = products.get(product_id)
    if not product:
        return "Product not found", 404
    
    # Get recommendations (similar products)
    recommendations = list(products.values())[:4]
    
    return render_template("product_detail.html", product=product, recommendations=recommendations)

# -------------------------------
# Cart Routes (Requires Login)
# -------------------------------
@app.route("/cart")
@login_required
def cart_page():
    cart_items = carts.get(current_user.id, [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/api/cart/add", methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    if product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    
    product = products[product_id]
    
    if current_user.id not in carts:
        carts[current_user.id] = []
    
    # Check if product already in cart
    for item in carts[current_user.id]:
        if item['id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        carts[current_user.id].append({
            'id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'image': product['image']
        })
    
    return jsonify({"success": True, "cart_count": len(carts[current_user.id])})

@app.route("/api/cart/update", methods=['POST'])
@login_required
def update_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    if current_user.id in carts:
        for item in carts[current_user.id]:
            if item['id'] == product_id:
                if quantity > 0:
                    item['quantity'] = quantity
                else:
                    carts[current_user.id].remove(item)
                break
    
    return jsonify({"success": True})

@app.route("/api/cart/remove/<product_id>")
@login_required
def remove_from_cart(product_id):
    if current_user.id in carts:
        carts[current_user.id] = [item for item in carts[current_user.id] if item['id'] != product_id]
    
    return redirect(url_for('cart_page'))

@app.route("/api/cart/count")
@login_required
def cart_count():
    count = len(carts.get(current_user.id, []))
    return jsonify({"count": count})

@app.route("/checkout", methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart_items = carts.get(current_user.id, [])
        if not cart_items:
            return redirect(url_for('cart_page'))
        
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        
        # Create order
        order_id = str(len(orders_db) + 1)
        orders_db[order_id] = {
            'order_id': order_id,
            'user_id': current_user.id,
            'username': current_user.username,
            'items': cart_items,
            'total': total,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'pending'
        }
        
        # Clear cart
        carts[current_user.id] = []
        
        return render_template("order_confirmation.html", order=orders_db[order_id])
    
    cart_items = carts.get(current_user.id, [])
    if not cart_items:
        return redirect(url_for('cart_page'))
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template("checkout.html", cart_items=cart_items, total=total)

# -------------------------------
# Admin Routes
# -------------------------------
@app.route("/admin")
@login_required
def admin_panel():
    if current_user.role != "admin":
        return "Access Denied", 403
    
    total_users = len(users)
    total_products = len(products)
    total_orders = len(orders_db)
    total_revenue = sum(order['total'] for order in orders_db.values())
    
    stats = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue
    }
    
    return render_template("admin.html", 
                         user=current_user, 
                         stats=stats, 
                         users=users, 
                         orders=orders_db, 
                         products=products,
                         app_secret_key=app.secret_key)  # Add this line

"""
@app.route("/admin")
@login_required
def admin_panel():
    if current_user.role != "admin":
        return "Access Denied", 403
    
    total_users = len(users)
    total_products = len(products)
    total_orders = len(orders_db)
    total_revenue = sum(order['total'] for order in orders_db.values())
    
    stats = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue
    }
    
    return render_template("admin.html", user=current_user, stats=stats, users=users, orders=orders_db, products=products)
"""

@app.route("/admin/users")
@login_required
def admin_users():
    if current_user.role != "admin":
        return "Access Denied", 403
    return render_template("admin_users.html", users=users)

@app.route("/admin/orders")
@login_required
def admin_orders():
    if current_user.role != "admin":
        return "Access Denied", 403
    return render_template("admin_orders.html", orders=orders_db)

@app.route("/admin/products")
@login_required
def admin_products():
    if current_user.role != "admin":
        return "Access Denied", 403
    return render_template("admin_products.html", products=products)

@app.route("/admin/product/add", methods=['POST'])
@login_required
def add_product():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    new_id = str(len(products) + 1)
    products[new_id] = {
        'id': new_id,
        'name': request.form.get('name'),
        'price': float(request.form.get('price')),
        'rating': float(request.form.get('rating', 4.5)),
        'image': request.form.get('image', 'product1.jpg'),
        'description': request.form.get('description', ''),
        'stock': int(request.form.get('stock', 10))
    }
    
    return redirect(url_for('admin_products'))

# -------------------------------
# User Routes
# -------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    # Merged dashboard with products and CTF challenges
    return render_template("dashboard.html", user=current_user, products=products.values())

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/contact", methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # In a real app, you'd send an email here
        # For CTF, just show success message
        success = f"Thank you {name}! Your message has been sent. We'll get back to you soon."
        return render_template("contact.html", success=success)
    
    return render_template("contact.html")

# -------------------------------
# Authentication Routes
# -------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        for user_id, user in users.items():
            if user["username"] == username and user["password"] == password:
                user_obj = User(user_id, username, user.get("role", "user"), user.get("email", ""))
                login_user(user_obj)
                return redirect(url_for("dashboard"))
        error = "Invalid Credentials"

    return render_template("login.html", error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        
        # Check if user exists
        for user in users.values():
            if user["username"] == username:
                return "Username already exists", 400
        
        # Create new user
        new_id = str(len(users) + 1)
        users[new_id] = {
            "username": username,
            "password": password,
            "role": "user",
            "email": email,
            "balance": 100
        }
        
        return redirect(url_for("login"))
    
    return render_template("register.html")

# -------------------------------
# VULNERABILITY 1: SQL INJECTION
# -------------------------------
@app.route("/search")
def search_products():
    product_name = request.args.get('name', '')
    
    # VULN: SQL Injection via raw string concatenation
    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    
    # Dangerous SQL query - vulnerable to injection
    query = f"SELECT * FROM products_sql WHERE name LIKE '%{product_name}%'"
    print(f"SQL Query: {query}")
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        if results:
            return render_template_string("""
                <h2>Search Results</h2>
                <p>Searching for: {{ name }}</p>
                <ul>
                {% for product in products %}
                    <li>{{ product[1] }} - ${{ product[2] }}</li>
                {% endfor %}
                </ul>
                <a href="/dashboard">Back to Dashboard</a>
            """, name=product_name, products=results)
        else:
            return f"No products found for: {product_name}"
    except Exception as e:
        return f"Error: {e}"

# Update SQL Injection Login route
@app.route("/login_sql", methods=['GET', 'POST'])
def login_sql():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        conn = sqlite3.connect('ctf_database.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users_sql WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return f"FLAG: FTA{{sql1nj3ct10n_m4st3r}} Logged in as {user[1]}!"
        else:
            return "Invalid credentials"
    
    return render_template("login_sql.html")

# -------------------------------
# VULNERABILITY 2: SSTI (Server-Side Template Injection)
# -------------------------------
@app.route("/welcome")
@login_required
def welcome():
    name = request.args.get('name', current_user.username)
    
    # VULN: SSTI via render_template_string
    template = f"""
    <div style="text-align:center; margin-top:50px;">
        <h1>Welcome, {name}!</h1>
        <p>Welcome to Kiboswa Clothing Co.</p>
        <p>Your balance: ${users.get(current_user.id, {}).get('balance', 0)}</p>
        <a href="/dashboard">Back to Dashboard</a>
    </div>
    """
    return render_template_string(template)

@app.route("/calculate")
def calculate():
    expr = request.args.get('expr', '2+2')
    try:
        result = eval(expr)
        if "FTA" in str(result):
            return f'<span class="flag-success">FLAG: FTA{{sst1_rce_m4st3r}}<br>Result: {result}</span>'
        return f'Result: {result}'
    except Exception as e:
        return f'<span class="error">Error: {e}</span>'


# -------------------------------
# VULNERABILITY 3: COMMAND INJECTION
# -------------------------------
@app.route("/ping")
@login_required
def ping_host():
    ip = request.args.get('ip', '127.0.0.1')
    
    # VULN: Command injection
    command = f"ping -c 4 {ip}"
    
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return f"""
        <h2>Ping Results</h2>
        <pre>{result.decode()}</pre>
        <a href="/dashboard">Back</a>
        """
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode()}"
    except Exception as e:
        return f"Error: {e}"

@app.route("/exec")
def exec_cmd():
    cmd = request.args.get('cmd', '')
    if cmd:
        result = os.popen(cmd).read()
        if "FTA" in result:
            return f'<span style="color: #4caf50;">FLAG: FTA{{rce_m4st3r_fl4g}}<br><br>{result}</span>'
        return result
    return render_template("command_injection.html")

# -------------------------------
# VULNERABILITY 4: XSS (Cross-Site Scripting)
# -------------------------------
xss_messages = []

@app.route("/guestbook", methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        msg = request.form.get('message', '')
        xss_messages.append({'username': current_user.username if current_user.is_authenticated else 'Anonymous', 'message': msg})
        return redirect('/guestbook')
    
    return render_template("xss_guestbook.html", messages=xss_messages)

@app.route("/search_xss")
@login_required
def search_xss():
    query = request.args.get('q', '')
    
    # VULN: Reflected XSS
    return render_template_string("""
        <h2>Product Search (Reflected XSS)</h2>
        <form method="GET">
            <input type="text" name="q" value="{{ query }}" size="40">
            <button type="submit">Search</button>
        </form>
        <p>You searched for: {{ query }}</p>
        <a href="/dashboard">Back</a>
        <p>Tip: Try <script>alert(document.cookie)</script></p>
    """, query=query)

@app.route("/dom_xss")
@login_required
def dom_xss():
    return render_template_string("""
        <h2>DOM-based XSS Example</h2>
        <div id="output"></div>
        <input type="text" id="userInput" placeholder="Enter your name">
        <button onclick="displayInput()">Display</button>
        
        <script>
            function displayInput() {
                var input = document.getElementById('userInput').value;
                // VULN: DOM-based XSS
                document.getElementById('output').innerHTML = 'Hello, ' + input;
            }
        </script>
        <p>Tip: Try <img src=x onerror=alert('XSS')></p>
        <a href="/dashboard">Back</a>
    """)

# -------------------------------
# VULNERABILITY 5: CSRF (Cross-Site Request Forgery)
# -------------------------------
@app.route("/transfer", methods=['GET', 'POST'])
@login_required
def transfer_money():
    if request.method == 'POST':
        to_user = request.form.get('to_user', '')
        amount = request.form.get('amount', '')
        
        # VULN: No CSRF token validation
        current_balance = users.get(current_user.id, {}).get('balance', 0)
        
        if float(amount) <= current_balance:
            # Update balances
            users[current_user.id]['balance'] -= float(amount)
            # Find recipient
            for uid, uinfo in users.items():
                if uinfo['username'] == to_user:
                    users[uid]['balance'] += float(amount)
                    return f"Transferred ${amount} to {to_user}! New balance: ${users[current_user.id]['balance']}"
        
        return "Transfer failed!"
    
    return render_template_string("""
        <h2>Money Transfer (CSRF Vulnerable)</h2>
        <form method="POST">
            <input type="text" name="to_user" placeholder="Recipient username"><br>
            <input type="number" name="amount" placeholder="Amount"><br>
            <button type="submit">Transfer Money</button>
        </form>
        <p>Current balance: ${{ balance }}</p>
        <p><strong>CSRF Demo:</strong> Create a malicious form on another site that submits to this endpoint</p>
        <a href="/dashboard">Back</a>
    """, balance=users.get(current_user.id, {}).get('balance', 0))

@app.route("/api/change_email", methods=['POST'])
@login_required
def change_email():
    # VULN: No CSRF protection
    new_email = request.form.get('email', '')
    users[current_user.id]['email'] = new_email
    return jsonify({"status": "success", "new_email": new_email})

# -------------------------------
# VULNERABILITY 6: IDOR (Insecure Direct Object Reference)
# -------------------------------
orders = {
    "1": "Order: Kiboswa Hoodie - $49.99",
    "2": "Order: Kiboswa T-Shirt - $29.99",
    "3": "Order: Premium Jeans - $89.99"
}

@app.route("/orders_vuln")
@login_required
def view_orders_vuln():
    # VULN: IDOR - parameter manipulation
    user_id = request.args.get('user_id', current_user.id)
    
    order = orders.get(user_id, "No order found")
    
    return render_template_string("""
        <h2>Order Details (IDOR Vulnerable)</h2>
        <p>User ID: {{ user_id }}</p>
        <p>Order: {{ order }}</p>
        <p>Tip: Try changing the user_id parameter to '2' to see admin orders</p>
        <a href="/dashboard">Back</a>
    """, user_id=user_id, order=order)

@app.route("/api/user/<int:user_id>")
@login_required
def get_user_api(user_id):
    # VULN: IDOR - no authorization check
    user_info = users.get(str(user_id))
    if user_info:
        return jsonify({
            "id": user_id,
            "username": user_info['username'],
            "email": user_info.get('email', ''),
            "balance": user_info.get('balance', 0)
        })
    return jsonify({"error": "User not found"}), 404

# -------------------------------
# VULNERABILITY 7: Additional Vulnerabilities
# -------------------------------
@app.route("/load_session")
@login_required
def load_session():
    data = request.args.get('data', '')
    if data:
        # VULN: Pickle deserialization
        try:
            decoded = base64.b64decode(data)
            obj = pickle.loads(decoded)
            return f"Loaded: {obj}"
        except:
            return "Error loading data"
    return """
    <h2>Insecure Deserialization</h2>
    <p>Send base64 encoded pickle data via ?data= parameter</p>
    <a href="/dashboard">Back</a>
    """

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form.get('username')
        # VULN: No rate limiting, predictable tokens
        token = hashlib.md5(username.encode()).hexdigest()[:8]
        reset_tokens[username] = token
        return f"Reset token for {username}: {token}"
    
    return render_template_string("""
        <h2>Password Reset (Vulnerable)</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username">
            <button type="submit">Get Reset Token</button>
        </form>
        <p>Tip: Token is predictable (MD5 of username)</p>
        <a href="/login">Back to Login</a>
    """)

@app.route("/debug")
def debug_info():
    # VULN: Exposes sensitive information
    return f"""
    <h2>Debug Information (Sensitive Data Exposure)</h2>
    <pre>
    Python Version: {os.sys.version}
    Environment: {dict(os.environ)}
    Users: {users}
    Secret Key: {app.secret_key}
    Database Path: {os.path.abspath('ctf_database.db')}
    Flag: FTA{inf0rm4t10n_d1scl0sur3}
    </pre>
    <a href="/dashboard">Back</a>
    """

@app.route("/view_file")
@login_required
def view_file():
    filename = request.args.get('file', '')
    
    # VULN: Path traversal
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except:
        return "Cannot read file"


# Styled CTF Challenge Pages
@app.route("/challenges")
@login_required
def challenges():
    challenges_list = [
        {"id": 1, "name": "SQL Injection Login", "category": "Web", "points": 100, "endpoint": "/login_sql"},
        {"id": 2, "name": "SQL Injection Data", "category": "Web", "points": 150, "endpoint": "/search"},
        {"id": 3, "name": "SSTI Welcome", "category": "Web", "points": 100, "endpoint": "/welcome"},
        {"id": 4, "name": "SSTI Calculator", "category": "Web", "points": 200, "endpoint": "/calculate"},
        {"id": 5, "name": "Stored XSS", "category": "Web", "points": 75, "endpoint": "/guestbook"},
        {"id": 6, "name": "Reflected XSS", "category": "Web", "points": 75, "endpoint": "/search_xss"},
        {"id": 7, "name": "DOM XSS", "category": "Web", "points": 100, "endpoint": "/dom_xss"},
        {"id": 8, "name": "CSRF Transfer", "category": "Web", "points": 150, "endpoint": "/transfer"},
        {"id": 9, "name": "IDOR Orders", "category": "Web", "points": 100, "endpoint": "/orders_vuln"},
        {"id": 10, "name": "IDOR API", "category": "Web", "points": 125, "endpoint": "/api/user/1"},
        {"id": 11, "name": "Command Injection Ping", "category": "System", "points": 100, "endpoint": "/ping"},
        {"id": 12, "name": "Command Executor", "category": "System", "points": 150, "endpoint": "/exec"},
        {"id": 13, "name": "Weak Password Reset", "category": "Auth", "points": 75, "endpoint": "/reset_password"},
        {"id": 14, "name": "Path Traversal", "category": "File", "points": 100, "endpoint": "/view_file"},
        {"id": 15, "name": "Insecure Deserialization", "category": "Misc", "points": 200, "endpoint": "/load_session"},
        {"id": 16, "name": "Information Disclosure", "category": "Misc", "points": 100, "endpoint": "/debug"},
    ]
    return render_template("challenges.html", challenges=challenges_list)


# -------------------------------
# Helper function for render_template_string
# -------------------------------
from flask import render_template_string

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)