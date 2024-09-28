from flask import Flask, jsonify, render_template, request
import json
import requests

app = Flask(__name__)

API_URL = 'http://localhost:4343/user/'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user/name/', methods=['POST'])
def user_page_btn():
    name = request.form['name']
    print(name)
    try: 
        response = requests.get(f"http://localhost:4343/user/name/{name}")
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        data = response.json()  # Get JSON data
        return render_template('users.html', name=data["name"])

    except requests.RequestException as exc:  # Catch all request-related exceptions
        return jsonify({"error": "Failed to retrieve data"}), 500 



@app.route('/user/<id>')
def user(id):
    try: 
        response = requests.get(f"http://localhost:4343/user/{id}")
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        data = response.json()  # Get JSON data
        
        return render_template('chatting_page.html', name=data["name"])
    except requests.RequestException as exc:  # Catch all request-related exceptions
        print(exc)
        return jsonify({"error": "Failed to retrieve data"}), 500 


@app.route('/api/users')  # Added leading slash
def users():
    try: 
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        data = response.json()  # Get JSON data
        return jsonify(data)  # Return JSON response
    except requests.RequestException as exc:  # Catch all request-related exceptions
        print(exc)
        return jsonify({"error": "Failed to retrieve data"}), 500 

if __name__ == '__main__':
    app.run(debug=True)
