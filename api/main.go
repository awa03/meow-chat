package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"strconv"
	"github.com/gorilla/mux"
)

// Chat represents a chat message with the user's ID.
type Chat struct {
	Chat   string `json:"chat"`
	UserID string `json:"user"`
  UserName string `json:"name"`
}

// User represents a user with a name, ID, and chat log.
type User struct {
	Name    string `json:"name"`
	ID      string `json:"id"`
	ChatLog []Chat `json:"chats"`
}

// UsageMessage provides usage information about available commands and examples.
type UsageMessage struct {
	Commands []string `json:"commands"`
	Examples []string `json:"examples"`
}

var users []User

// Utility functions

// generateID generates a unique ID using crypto/rand.
func generateID() string {
	bytes := make([]byte, 16)
	if _, err := io.ReadFull(rand.Reader, bytes); err != nil {
		return ""
	}
	return hex.EncodeToString(bytes)
}

// Handlers

// getUserByID retrieves a user by their ID.
func getUserByID(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	for _, item := range users {
		if item.ID == params["id"] {
			json.NewEncoder(w).Encode(item)
			return
		}
	}
	http.Error(w, "User not found", http.StatusNotFound)
}

// getUserByName retrieves a user by their name.
func getUserByName(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	for _, item := range users {
		if item.Name == params["name"] {
			json.NewEncoder(w).Encode(item)
			return
		}
	}
	http.Error(w, "User not found", http.StatusNotFound)
}

// addUser adds a new user.
func addUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    var newUser User

    if err := json.NewDecoder(r.Body).Decode(&newUser); err != nil {
        http.Error(w, "Invalid input", http.StatusBadRequest)
        return
    }

    for i, user := range users {
      if user.ID == newUser.ID{
        users[i].Name = newUser.Name; 
        return
      }
    }

    // Check if ID is provided
    if newUser.ID == "" {
        http.Error(w, "ID is required", http.StatusBadRequest)
        return
    }

    // Append the new user to the users slice
    users = append(users, newUser)
    json.NewEncoder(w).Encode(newUser)
}

// updateUser updates an existing user.
func updateUser(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var updatedUser User
	if err := json.NewDecoder(r.Body).Decode(&updatedUser); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	for i, user := range users {
		if user.ID == params["id"] {
			users[i].Name = updatedUser.Name
			json.NewEncoder(w).Encode(users[i])
			return
		}
	}
	http.Error(w, "User not found", http.StatusNotFound)
}

// getAllUsers retrieves all users.
func getAllUsers(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(users)
}

// usage provides usage information about available API endpoints.
func usage(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	usageInfo := UsageMessage{
		Commands: []string{
			"GET /user/ - Get all users",
			"GET /user/{id} - Get user by ID",
			"GET /user/name/{name} - Get user by name",
			"POST /user/adduser - Add a new user",
			"PUT /user/{id} - Update an existing user",
			"POST /user/{id}/chat - Add a chat to user",
			"PUT /user/{id}/chat/{chatIndex} - Update a chat in user's chat log",
			"GET /user/{id}/chats - Get all chats for a user",
		},
		Examples: []string{
			`curl -X POST -d '{"name": "NewUser"}' http://localhost:4343/user/adduser`,
			`curl -X PUT -d '{"name": "UpdatedUser"}' http://localhost:4343/user/{id}`,
			`curl -X POST -d '{"chat": "Hello!"}' http://localhost:4343/user/{id}/chat`,
		},
	}

	json.NewEncoder(w).Encode(usageInfo)
}

// addChat adds a new chat message to a user's chat log.
func addChat(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    params := mux.Vars(r)
    var newChat Chat

    if err := json.NewDecoder(r.Body).Decode(&newChat); err != nil {
        http.Error(w, "Invalid input", http.StatusBadRequest)
        return
    }

    for i, user := range users {
        if user.ID == params["id"] {
            newChat.UserID = user.ID
            newChat.UserName = user.Name;
            users[i].ChatLog = append(users[i].ChatLog, newChat)
            json.NewEncoder(w).Encode(newChat)
            return
        }
    }

    http.Error(w, "User not found", http.StatusNotFound)
}

func addChatByName(w http.ResponseWriter, r *http.Request) {

    println("Conntected to chatbyname")

    w.Header().Set("Content-Type", "application/json")
    params := mux.Vars(r)
    var newChat Chat

    if err := json.NewDecoder(r.Body).Decode(&newChat); err != nil {
        http.Error(w, "Invalid input", http.StatusBadRequest)
        return
    }

    for i, user := range users {
        if user.Name == params["name"] || user.ID == params["name"] {
            newChat.UserID = user.ID
            newChat.UserName = user.Name;
            users[i].ChatLog = append(users[i].ChatLog, newChat)
            json.NewEncoder(w).Encode(newChat)
            return
        }
    }

    http.Error(w, "User not found", http.StatusNotFound)
}




// updateChat updates a specific chat message in a user's chat log.
func updateChat(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var updatedChat Chat
	if err := json.NewDecoder(r.Body).Decode(&updatedChat); err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	userID := params["id"]
	chatIndex := params["chatIndex"]

	for i, user := range users {
		if user.ID == userID {
			index, err := strconv.Atoi(chatIndex)
			if err != nil || index < 0 || index >= len(users[i].ChatLog) {
				http.Error(w, "Chat not found", http.StatusNotFound)
				return
			}
			users[i].ChatLog[index] = updatedChat
			json.NewEncoder(w).Encode(updatedChat)
			return
		}
	}
	http.Error(w, "User not found", http.StatusNotFound)
}

// getChatById retrieves all chats for a given user.
func getChatById(w http.ResponseWriter, r *http.Request) {
  print("Testing")
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	for _, user := range users {
		if user.ID == params["id"] {
			json.NewEncoder(w).Encode(user.ChatLog)
			return
		}
	}
	http.Error(w, "User not found", http.StatusNotFound)
}

func checkUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    params := mux.Vars(r)
    for _, item := range users {
        if item.Name == params["name"] {
            w.WriteHeader(http.StatusOK) // User exists
            return
        }
    }
    w.WriteHeader(http.StatusNotFound) // User does not exist
}

// Entry point
func main() {


	// Initialize with some users
	users = append(users, User{
		Name: "awa03",
		ID:   generateID(),
	})
	users = append(users, User{
		Name: "TestUser3",
		ID:   generateID(),
	})

	// Initialize the router
	router := mux.NewRouter()

	// Define routes
	router.HandleFunc("/", usage).Methods("GET")
	router.HandleFunc("/user/", getAllUsers).Methods("GET")
	router.HandleFunc("/user/{id}", getUserByID).Methods("GET")
	router.HandleFunc("/user/name/{name}", getUserByName).Methods("GET")
	router.HandleFunc("/user/adduser/", addUser).Methods("POST")
	router.HandleFunc("/user/{id}", updateUser).Methods("PUT")
	router.HandleFunc("/user/{id}/chat", addChat).Methods("POST")
	router.HandleFunc("/user/name/{name}/chat", addChatByName).Methods("POST")
	router.HandleFunc("/user/{id}/chat/{chatIndex}", updateChat).Methods("PUT")
	router.HandleFunc("/user/{id}/chats", getChatById).Methods("GET")
  router.HandleFunc("/user/check/{name}", checkUser).Methods("GET")

	// Start the server
	log.Fatal(http.ListenAndServe(":4343", router))
}

