import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

client = MongoClient(os.environ['MONGO_URI'])
client.admin.command('ping')
db = client[os.environ.get('MONGO_DB_NAME', 'tutedude_db')]
submissions = db['submissions']
todo_items = db['todo_items']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api')
def api():
    with open(DATA_FILE) as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    if not name or not email:
        return render_template('index.html', error='Name and email are required.',
                                name=name, email=email, message=message)

    try:
        submissions.insert_one({'name': name, 'email': email, 'message': message})
    except PyMongoError as e:
        return render_template('index.html', error=f'Error submitting data: {e}',
                                name=name, email=email, message=message)

    return redirect(url_for('success'))


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/submittodoitem', methods=['POST'])
def submit_todo_item():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    item_name = str(data.get('itemName', '')).strip()
    item_description = str(data.get('itemDescription', '')).strip()

    if not item_name:
        return jsonify(error='itemName is required.'), 400

    try:
        todo_items.insert_one({'itemName': item_name, 'itemDescription': item_description})
    except PyMongoError as e:
        return jsonify(error=f'Error submitting item: {e}'), 500

    return jsonify(message='Item submitted successfully.'), 201


if __name__ == '__main__':
    app.run(debug=True)
