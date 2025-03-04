# -*- coding: utf-8 -*-

from flask import Flask, jsonify
import database as db

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "<p>Hello world!<p>"

@app.route('/users', methods=['GET'])
def get_users_all():
    client = db.connect_to_db()
    users = db.find_all_users(client)
    return jsonify(users)

if __name__ == '__main__':
    app.run()
