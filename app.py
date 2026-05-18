from flask import Flask, render_template, request, jsonify
from database import init_db, add_product, get_all_products, update_price, delete_product, get_price_history
from scraper import fetch_price
from predictor import predict_price
from notifier import send_alert
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
init_db()

def check_prices():
    products = get_all_products()
    for p in products:
        try:
            current_price = fetch_price(p['url'])
            if current_price:
                update_price(p['id'], current_price)
                if current_price <= p['target_price']:
                    send_alert(p['email'], p['name'], current_price, p['target_price'], p['url'])
        except Exception as e:
            print(f"Error checking {p['name']}: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_prices, trigger="interval", minutes=30)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    products = get_all_products()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add():
    data = request.json
    name = data.get('name')
    url = data.get('url')
    target_price = float(data.get('target_price'))
    email = data.get('email')

    current_price = fetch_price(url)
    if current_price is None:
        return jsonify({'error': 'Could not fetch price from URL. Please check the URL.'}), 400

    product_id = add_product(name, url, current_price, target_price, email)
    return jsonify({'success': True, 'id': product_id, 'current_price': current_price})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def remove(product_id):
    delete_product(product_id)
    return jsonify({'success': True})

@app.route('/api/refresh/<int:product_id>', methods=['POST'])
def refresh(product_id):
    products = get_all_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    current_price = fetch_price(product['url'])
    if current_price is None:
        return jsonify({'error': 'Could not fetch price'}), 400
    update_price(product_id, current_price)
    if current_price <= product['target_price']:
        send_alert(product['email'], product['name'], current_price, product['target_price'], product['url'])
    return jsonify({'success': True, 'current_price': current_price})

@app.route('/api/history/<int:product_id>', methods=['GET'])
def history(product_id):
    data = get_price_history(product_id)
    return jsonify(data)

@app.route('/api/predict/<int:product_id>', methods=['GET'])
def predict(product_id):
    history = get_price_history(product_id)
    if len(history) < 2:
        return jsonify({'error': 'Not enough data to predict'}), 400
    prediction = predict_price(history)
    return jsonify({'predicted_price': prediction})

if __name__ == '__main__':
    app.run(debug=True)
