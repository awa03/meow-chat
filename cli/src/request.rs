// src/requests.rs

use serde::{Deserialize, Serialize};
use crate::generate_id; // Import the generateID function from main

#[derive(Clone)]
pub struct Chat {
    pub chat: String,
    pub user_id: String,
    pub user_name: String,
}

#[derive(Clone)]
pub struct User {
    pub name: String,
    pub id: String,
    pub chat_log: Vec<Chat>,
}

pub static mut USERS: Vec<User> = Vec::new();

pub fn add_user(name: String) {
    let new_user = User {
        name,
        id: generate_id(), // Use the existing generateID function
        chat_log: Vec::new(),
    };

    unsafe {
        USERS.push(new_user);
    }
}

pub fn get_user_by_id(user_id: &str) -> Option<User> {
    unsafe {
        USERS.iter().cloned().find(|user| user.id == user_id)
    }
}


