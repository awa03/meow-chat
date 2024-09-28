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

@app.route('/user/<id>/sendchat', methods=['POST'])
def send_chat(id):
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415  # 415 Unsupported Media Type

    try:
        # Parse JSON request data
        data = request.get_json()
        name = data.get('name')
        message = data.get('message')

        if not name or not message:
            return jsonify({"error": "Name and message are required."}), 400

        # Create the new chat object
        new_chat = {
            "chat": message,
            "user": {
                "name": name,
                "id": id,
                "chat_log": []  # Optional, as the backend handles the log
            }
        }

        new_chat = jsonify(new_chat)

        # Send the new chat to the backend
        response = requests.post(f"http://localhost:4343/user/{id}/chat", json=new_chat)

        # Handle the response from the backend
        if response.status_code == 200:
            return 'Success', 200
        else:
            return jsonify({"error": "Failed to add chat", "details": response.text}), response.status_code

    except requests.RequestException as exc:
        return jsonify({"error": "Failed to reach backend", "details": str(exc)}), 500

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


