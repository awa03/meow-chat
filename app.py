from flask import Flask, request, jsonify, render_template
import requests
import socket
import uuid
import hashlib

app = Flask(__name__)

API_URL = "http://localhost:4343/user/"  # Adjust as needed

@app.route('/user/chats')
def view_all_user_chats():
    userID = get_computer_hash()  # Get user ID based on the current machine
    try: 
        # Fetch chat logs from Go backend
        response = requests.get(f"http://localhost:4343/user/{userID}/chats")
        response.raise_for_status()  # Raise an error if the request failed
        chats = response.json()  # Parse the JSON response
        print(chats)
        
        # Render the chat logs in the HTML template
        return render_template('users_chats.html', chats=chats)
    except requests.RequestException as e:
        return render_template('home.html', name_msg = "Please Enter Name")

@app.route('/user/new/', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({"error": "Name is required."}), 400

        # Generate a unique ID for the user
        new_user = {
            "name": name,
            "id": get_computer_hash()  # Assuming you have this function defined to generate a unique ID
        }

        # Send the new user to the Go backend
        response = requests.post("http://localhost:4343/user/adduser/", json=new_user)

        if response.status_code == 200:
            return jsonify({"message": "User added successfully!", "user": response.json()}), 200
        else:
            return jsonify({"error": "Failed to add user", "details": response.json()}), response.status_code

    except requests.RequestException as exc:
        return jsonify({"error": "Failed to reach backend", "details": str(exc)}), 500


@app.route('/user/send/<name>/chat', methods=['POST'])
def send_chat_by_name(name):
    print("Called")
    try:
        # Parse JSON request data
        data = request.get_json()  # This retrieves the JSON data sent to this endpoint
        message = data.get('chat')  # Change 'message' to 'chat' to match your front-end

        print(data, message)

        # Check if message is provided
        if not message: 
            return jsonify({"error": "Message is required."}), 400

        # Create the new chat object
        new_chat = {
            "chat": message,
            "user": get_computer_hash()  # Include the user ID
        }

        print(new_chat)

        # Send the new chat to the Go backend
        response = requests.post(f"http://localhost:4343/user/name/{name}/chat", json=new_chat)  # Use new_chat directly

        # Handle the response from the backend
        if response.status_code == 200:
            return jsonify({"message": "Chat added successfully!"}), 200
        else:
            return jsonify({"error": "Failed to add chat", "details": response.text}), response.status_code

    except requests.RequestException as exc:
        print(exc)
        return jsonify({"error": "Failed to reach backend", "details": str(exc)}), 500


@app.route('/user/<id>/sendchat', methods=['POST'])
def send_chat(id):
    try:
        # Parse JSON request data
        data = request.get_json()  # This retrieves the JSON data sent to this endpoint
        message = data.get('chat')  # Change 'message' to 'chat' to match your front-end

        print(data, message)

        # Check if message is provided
        if not message: 
            return jsonify({"error": "Message is required."}), 400

        # Create the new chat object
        new_chat = {
            "chat": message,
            "user": get_computer_hash()  # Include the user ID
        }

        print(new_chat)

        # Send the new chat to the Go backend
        response = requests.post(f"{API_URL}{id}/chat", json=new_chat)  # Use new_chat directly

        # Handle the response from the backend
        if response.status_code == 200:
            return jsonify({"message": "Chat added successfully!"}), 200
        else:
            return jsonify({"error": "Failed to add chat", "details": response.text}), response.status_code

    except requests.RequestException as exc:
        print(exc)
        return jsonify({"error": "Failed to reach backend", "details": str(exc)}), 500

@app.route('/user/<id>')
def user(id):
    try:
        # Fetch the user data by ID from the Go backend
        response = requests.get(f"{API_URL}{id}")
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        data = response.json()  # Get JSON data

        return render_template('chatting_page.html', name=data["name"], chat_log=data.get("ChatLog", []))
    except requests.RequestException as exc:  # Catch all request-related exceptions
        print(exc)
        return jsonify({"error": "Failed to retrieve data"}), 500

@app.route('/')
def home():
    print(get_computer_hash())
    return render_template('home.html')

def get_computer_hash():
    # Get the MAC address
    mac = hex(uuid.getnode()).replace('0x', '')
    
    # Get the hostname
    hostname = socket.gethostname()
    
    # Combine MAC and hostname
    identifier = f"{mac}-{hostname}".encode('utf-8')
    
    # Generate a SHA256 hash
    computer_hash = hashlib.sha256(identifier).hexdigest()
    
    return computer_hash

# Start the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

