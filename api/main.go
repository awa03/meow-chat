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

type UsageMessage struct {
	Commands []string `json:"commands"`
	Examples []string `json:"examples"`
}

type Chat struct {
	Chat string `json:"chat"`
	User User   `json:"user"`
}

type User struct {
	Name    string `json:"name"`
	ID      string `json:"id"`
	ChatLog []Chat `json:"chat_log"` // Fixed typo: changed "jason" to "json"
}

var users []User

// getUserByID retrieves a user by their ID
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

// getUserByName retrieves a user by their name
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

// addUser adds a new user
func addUser(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var newUser User
	json.NewDecoder(r.Body).Decode(&newUser)
	newUser.ID = generateID()
	users = append(users, newUser)
	json.NewEncoder(w).Encode(newUser)
}

// updateUser updates an existing user
func updateUser(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var updatedUser User
	json.NewDecoder(r.Body).Decode(&updatedUser)

	for i, user := range users {
		if user.ID == params["id"] {
			users[i].Name = updatedUser.Name // Update the user's name
			json.NewEncoder(w).Encode(users[i])
			return
		}
	}
	http.Error(w, "User not found", http.StatusNotFound)
}

// getAllUsers retrieves all users
func getAllUsers(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(users)
}

// generateID generates a unique ID
func generateID() string {
	bytes := make([]byte, 16)
	if _, err := io.ReadFull(rand.Reader, bytes); err != nil {
		return ""
	}
	return hex.EncodeToString(bytes)
}

// usage displays usage information
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
			"GET /user/{id}/chat - Get user chat log",
      "GET /user/{id}/chats - Get All Users Chats",
		},
		Examples: []string{
			`curl -X POST -d '{"name": "NewUser"}' http://localhost:5000/user/adduser`,
			`curl -X PUT -d '{"name": "UpdatedUser"}' http://localhost:5000/user/{id}`,
			`curl -X POST -d '{"chat": "Hello!"}' http://localhost:5000/user/{id}/chat`,
		},
	}

	json.NewEncoder(w).Encode(usageInfo)
}

// addChat handles adding a chat to a user's chat log
func addChat(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var newChat Chat
	json.NewDecoder(r.Body).Decode(&newChat)

	for i, user := range users {
		if user.ID == params["id"] {
			newChat.User = user // Set the user in the chat
			users[i].ChatLog = append(users[i].ChatLog, newChat) // Append the chat to the user's chat log
			json.NewEncoder(w).Encode(newChat) // Return the added chat
			return
		}
	}
	http.Error(w, "User not found", http.StatusNotFound)
}

// updateChat updates a specific chat in the user's chat log
func updateChat(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var updatedChat Chat
	json.NewDecoder(r.Body).Decode(&updatedChat)

	userID := params["id"]
	chatIndex := params["chatIndex"]

	for i, user := range users {
		if user.ID == userID {
			index, err := strconv.Atoi(chatIndex)
			if err != nil || index < 0 || index >= len(users[i].ChatLog) {
				http.Error(w, "Chat not found", http.StatusNotFound)
				return
			}
			users[i].ChatLog[index] = updatedChat // Update the chat at the specified index
			json.NewEncoder(w).Encode(updatedChat) // Return the updated chat
			return
		}
	}
	http.Error(w, "User not found", http.StatusNotFound)
}

func getChatById(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
  params := mux.Vars(r)
  userID := params["id"]
  for i, user := range users {
    if user.ID == userID {
      res := users[i].ChatLog 
      json.NewEncoder(w).Encode(res)
      return
    }
  } 
  http.Error(w, "User not found", http.StatusNotFound)
}

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
	router.HandleFunc("/usage/", usage).Methods("GET")
	router.HandleFunc("/user/", getAllUsers).Methods("GET")
	router.HandleFunc("/user", getAllUsers).Methods("GET")
	router.HandleFunc("/user/{id}", getUserByID).Methods("GET")
	router.HandleFunc("/user/{id}/", getUserByID).Methods("GET")
	router.HandleFunc("/user/name/{name}", getUserByName).Methods("GET")
	router.HandleFunc("/user/name/{name}/", getUserByName).Methods("GET")
	router.HandleFunc("/user/{id}/chats", getChatById).Methods("GET")
	router.HandleFunc("/user/{id}/chats/", getChatById).Methods("GET")
	router.HandleFunc("/user/adduser", addUser).Methods("POST")
	router.HandleFunc("/user/adduser/", addUser).Methods("POST")
	router.HandleFunc("/user/{id}", updateUser).Methods("PUT")
	router.HandleFunc("/user/{id}/", updateUser).Methods("PUT")
	router.HandleFunc("/user/{id}/chat", addChat).Methods("POST")
	router.HandleFunc("/user/{id}/chat/", addChat).Methods("POST")
	router.HandleFunc("/user/{id}/chat/{chatIndex}", updateChat).Methods("PUT")
	router.HandleFunc("/user/{id}/chat/{chatIndex}/", updateChat).Methods("PUT")

	// Start server on port 5000
	log.Fatal(http.ListenAndServe(":4343", router))
}

