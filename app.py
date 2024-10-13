from flask import Flask, request, jsonify, render_template, session
import requests
import uuid

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Replace with a strong secret key
API_URL = "http://localhost:4343/user/"  # Adjust as needed

def generate_unique_id():
    """Generate a random UUID."""
    return str(uuid.uuid4())

@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = generate_unique_id()
    print(session['user_id'])
    
    return render_template('home.html')

@app.route('/user/chats')
def view_all_user_chats():
    user_id = session.get('user_id')  
    try:
        response = requests.get(f"{API_URL}{user_id}/chats")
        response.raise_for_status()  # Raise an error if the request failed
        chats = response.json()  # Parse the JSON response
        print(chats)
        
        return render_template('users_chats.html', chats=chats)
    except requests.RequestException as e:
        print(f"Error fetching chats: {e}")
        return render_template('home.html', name_msg="Please Enter Name")

@app.route('/user/new/', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({"error": "Name is required."}), 400

        user_id = session.get('user_id')

        new_user = {
            "name": name,
            "id": user_id  # Use the ID stored in the session
        }

        response = requests.post(f"{API_URL}adduser/", json=new_user)

        if response.status_code == 200:
            return jsonify({"message": "User added successfully!", "user": response.json()}), 200
        else:
            return jsonify({"error": "Failed to add user", "details": response.json()}), response.status_code

    except requests.RequestException as exc:
        print(f"Error adding user: {exc}")
        return jsonify({"error": "Failed to reach backend", "details": str(exc)}), 500

@app.route('/user/send/<name>/chat', methods=['POST'])
def send_chat_by_name(name):
    print("Called")
    try:
        data = request.get_json()
        message = data.get('chat')  # Assuming 'chat' is sent from the frontend

        print(data, message)

        if not message: 
            return jsonify({"error": "Message is required."}), 400

        new_chat = {
            "chat": message,
            "user": session.get('user_id')  # Include user ID from the session
        }

        print(new_chat)

        response = requests.post(f"{API_URL}name/{name}/chat", json=new_chat)

        if response.status_code == 200:
            return jsonify({"message": "Chat added successfully!"}), 200
        else:
            return jsonify({"error": "Failed to add chat", "details": response.text}), response.status_code

    except requests.RequestException as exc:
        print(f"Error sending chat: {exc}")
        return jsonify({"error": "Failed to reach backend", "details": str(exc)}), 500

@app.route('/user/<id>/sendchat', methods=['POST'])
def send_chat(id):
    try:
        data = request.get_json()
        message = data.get('chat')  

        print(data, message)

        if not message: 
            return jsonify({"error": "Message is required."}), 400

        new_chat = {
            "chat": message,
            "user": session.get('user_id')  # Include user ID from the session
        }

        print(new_chat)

        response = requests.post(f"{API_URL}{id}/chat", json=new_chat)

        if response.status_code == 200:
            return jsonify({"message": "Chat added successfully!"}), 200
        else:
            return jsonify({"error": "Failed to add chat", "details": response.text}), response.status_code

    except requests.RequestException as exc:
        print(f"Error sending chat: {exc}")
        return jsonify({"error": "Failed to reach backend", "details": str(exc)}), 500

@app.route('/user/<id>')
def user(id):
    try:
        response = requests.get(f"{API_URL}{id}")
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()  # Get JSON data

        return render_template('chatting_page.html', name=data["name"], chat_log=data.get("ChatLog", []))
    except requests.RequestException as exc:
        print(f"Error fetching user data: {exc}")
        return jsonify({"error": "Failed to retrieve data"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

