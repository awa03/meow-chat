use std::{time::Duration, io::{self, Write}};
use crossterm::{
    execute,
    terminal::{enable_raw_mode, disable_raw_mode, Clear, ClearType, size},
    event::{poll, read, Event, KeyCode, KeyModifiers, KeyEvent},
    cursor, style::{Print, SetForegroundColor, Color},
};
use std::process::Command;
use sha2::{Sha256, Digest};
use mac_address::get_mac_address;

mod request; 
use request::{add_user, get_user_by_id};

fn get_computer_hash() -> String {
    // Get the MAC address
    let mac = get_mac_address()
        .expect("Failed to get MAC address")
        .expect("No MAC address found");

    // Get the hostname
    let hostname = Command::new("hostname")
        .output()
        .expect("Failed to get hostname")
        .stdout;

    let hostname = String::from_utf8_lossy(&hostname).trim().to_string();

    // Combine MAC and hostname
    let identifier = format!("{}-{}", mac, hostname);
    
    // Generate a SHA256 hash
    let mut hasher = Sha256::new();
    hasher.update(identifier.as_bytes());
    let result = hasher.finalize();

    // Convert the hash to hex format
    format!("{:x}", result)
}

fn generate_id() -> String {get_computer_hash()}


fn main() -> io::Result<()> {
    let hash = get_computer_hash();
    enable_raw_mode().unwrap(); // Enable raw mode to capture key presses directly

    let (cols, rows) = size()?; // Get terminal size
    let mut stdout = io::stdout(); // Use stdout for output

    // Clear the screen
    execute!(stdout, Clear(ClearType::All))?;

    // Draw the input box
    let input_line = rows - 2; // The line for input
    execute!(stdout, Print("+".to_string() + &"-".repeat((cols - 3) as usize) + "+\n"))?; // Top of the box
    execute!(stdout, Print("|".to_string() + &" ".repeat((cols - 3) as usize) + "|\n"))?; // Empty line
    
    // Move cursor to the input line
    execute!(stdout, cursor::MoveTo(1, input_line))?;

    // Get username input
    let mut username = String::new();
    execute!(stdout, Print("Enter your username: "))?;
    
    // Read characters for the username input
    loop {
        if poll(Duration::from_millis(500))? {
            match read()? {
                Event::Key(KeyEvent { code: KeyCode::Enter, .. }) => {
                    break; // Break on Enter
                }
                Event::Key(KeyEvent { code: KeyCode::Backspace, .. }) => {
                    if !username.is_empty() {
                        username.pop(); // Remove the last character
                        execute!(stdout, cursor::MoveTo(1, input_line), Clear(ClearType::CurrentLine))?;
                        execute!(stdout, Print(format!("Enter your username: {}", username)))?; // Print the updated username
                    }
                }
                Event::Key(KeyEvent { code: KeyCode::Char(c), .. }) => {
                    username.push(c); // Append the character to the username
                    execute!(stdout, Print(c))?; // Print the character
                }
                _ => {}
            }
        }
    }

    // Clear the input line
    execute!(stdout, cursor::MoveTo(0, input_line + 1), Clear(ClearType::CurrentLine))?;
    
    // Print the entered username and hash in the top right corner
    execute!(stdout, cursor::MoveTo(cols - 30, 0), Print(format!("Username: {}", username)))?;

    add_user(username);
    
    // Main loop for input handling
    let mut message = String::new(); // Store current input message
    let mut message_line = 0; // Track the message line to print above the input box

    loop {
        // Poll for events every 500 ms
        if poll(Duration::from_millis(500))? {
            match read()? {
                // Handle key events
                Event::Key(key_event) => {
                    match key_event {
                        // Exit on Ctrl+Q
                        KeyEvent { code: KeyCode::Char('q'), modifiers: KeyModifiers::CONTROL, .. } => {
                            break;
                        }
                        KeyEvent { code: KeyCode::Char('m'), modifiers: KeyModifiers::CONTROL, .. } => {
                            break;
                        }
                        KeyEvent { code: KeyCode::Char('w'), modifiers: KeyModifiers::CONTROL, .. } => {
                            // Clear the input line and prompt for ID
                            execute!(stdout, Clear(ClearType::CurrentLine))?;
                            execute!(stdout, cursor::MoveTo(1, input_line), Print("What ID? "))?;

                            let mut id_input = String::new(); // To store the user's input for the ID
                            // Read characters for the ID input
                            loop {
                                if poll(Duration::from_millis(500))? {
                                    match read()? {
                                        Event::Key(KeyEvent { code, modifiers, .. }) => {
                                            match (code, modifiers) {
                                                (KeyCode::Enter, _) => {
                                                    break; // Break on Enter
                                                }
                                                (KeyCode::Backspace, _) => {
                                                    if !id_input.is_empty() {
                                                        id_input.pop(); // Remove the last character
                                                        // Clear the ID input line
                                                        execute!(stdout, cursor::MoveTo(1, input_line), Clear(ClearType::CurrentLine))?;
                                                        execute!(stdout, cursor::MoveTo(1, input_line), Print("What ID? "))?; // Reprint the prompt
                                                        execute!(stdout, Print(&id_input))?; // Print the updated ID
                                                        // Move cursor to the end of the ID input
                                                        execute!(stdout, cursor::MoveTo((id_input.len() + 1) as u16, input_line))?;
                                                    }
                                                }
                                                (KeyCode::Char(c), _) => {
                                                    id_input.push(c); // Append the character to the ID input
                                                    execute!(stdout, Print(c))?; // Print the character
                                                }
                                                _ => {}
                                            }
                                        }
                                        _ => {}
                                    }
                                }
                            }

                            // After getting the ID, you can do something with it, like print it
                            execute!(stdout, cursor::MoveTo(0, input_line + 1), Clear(ClearType::CurrentLine))?; // Clear the line below the input
                            execute!(stdout, Print(format!("You entered ID: {}", id_input)))?; // Print the entered ID
                        }
                        // Handle Enter key: send/print the message
                        KeyEvent { code: KeyCode::Enter, .. } => {
                            // If the message line is at the top, we can scroll down
                            if message_line < input_line - 2 {
                                message_line += 1; // Move to the next line for the next message
                            } else {
                                // Clear the screen and redraw the box and messages
                                execute!(stdout, Clear(ClearType::All), cursor::MoveTo(0, 0))?;
                                execute!(stdout, Print("+".to_string() + &"-".repeat((cols - 2) as usize) + "+\n"))?;
                                execute!(stdout, Print("|".to_string() + &" ".repeat((cols - 2) as usize) + "|\n"))?;
                                execute!(stdout, Print("+".to_string() + &"-".repeat((cols - 2) as usize) + "+\n"))?;
                                
                                // Reset message line position to allow for new messages
                                message_line = 0;
                            }

                            // Move to the next line to print the message
                            execute!(stdout, cursor::MoveTo(1, message_line), Print(&message))?;

                            // Clear the message input line
                            message.clear(); // Clear the message in memory
                            
                            // Move back to the input line
                            execute!(
                                stdout,
                                cursor::MoveTo(1, input_line),         // Move cursor to input line
                                Clear(ClearType::CurrentLine)         // Clear the current line
                            )?;
                        }
                        // Handle regular character input
                        KeyEvent { code: KeyCode::Char(c), .. } => {
                            // Append the character to the message string
                            message.push(c);
                            // Print the character on the screen
                            execute!(stdout, Print(c))?;
                        }
                        // Handle Backspace key
                        KeyEvent { code: KeyCode::Backspace, .. } => {
                            if !message.is_empty() {
                                message.pop(); // Remove the last character from the message
                            }

                            // Clear the area of the input box
                            execute!(stdout, cursor::MoveTo(1, input_line), Clear(ClearType::CurrentLine))?;

                            // Print the updated message
                            execute!(stdout, Print(&message))?;

                            // Move the cursor back to the end of the input line
                            execute!(stdout, cursor::MoveTo((message.len() + 1) as u16, input_line))?;
                        }
                        _ => {} // Handle other keys that are not defined
                    }
                }
                _ => {}
            }
        }
    }

    // Disable raw mode before exiting
    disable_raw_mode()?;
    Ok(())
}

