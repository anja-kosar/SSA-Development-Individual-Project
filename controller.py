import socket
import logging
import re
import random
import string
from datetime import datetime

# Logging failed attempts to a file
logging.basicConfig(
    filename="failed_attempts.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# Password security standards using regular expressions
def is_password_secure(password):
    """Check if the password meets industry standards."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isupper() for char in password):
        return "Password must include at least one uppercase letter."
    if not any(char.islower() for char in password):
        return "Password must include at least one lowercase letter."
    if not any(char.isdigit() for char in password):
        return "Password must include at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must include at least one special character (!@#$%^&*(), etc.)."
    return None

# Log failed login attempts with client address and timestamp
def log_failed_attempt(addr):
    """Log a failed login attempt with client address and timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Failed login attempt from {addr} at {timestamp}")

# Function to generate a random OTP (One-Time Password) for MFA
def generate_otp():
    """Generate a 6-digit OTP."""
    otp = ''.join(random.choices(string.digits, k=6))
    return otp

# Function to handle communication with a connected client
def handle_client(conn, addr, password):
    """Handle communication with a connected client."""
    print(f"Connection established with {addr}. Awaiting password.")
    conn.send(b"Enter password: ")

    # Loop for password entry and validation
    while True:
        try:
            received_password = conn.recv(1024).decode().strip()
            if not received_password:
                continue

            if received_password == password:
                conn.send(b"Authentication successful! Please enter the OTP sent to your phone.\n")
                otp = generate_otp()
                print(f"OTP for {addr}: {otp}")  # For demonstration, print the OTP on the server side
                break  # Exit the loop if password is correct
            else:
                conn.send(b"Authentication failed! Try again.\n")
                log_failed_attempt(addr)  # Logs failed login attempts
                print(f"Authentication failed for {addr}. Awaiting retry.")
                conn.send(b"Enter password: ")  # Ask for the password again after failure
        except ConnectionResetError:
            print(f"Connection lost with {addr} during authentication.")
            return

    # Loop for OTP entry and verification
    while True:
        try:
            conn.send(b"Enter OTP: ")
            otp_received = conn.recv(1024).decode().strip()
            if otp_received == otp:
                conn.send(b"OTP verified successfully! You are now connected.\n")
                print(f"OTP verification successful for {addr}.")
                break  # Exit the OTP loop if OTP is correct
            else:
                conn.send(b"Invalid OTP! Try again.\n")
                print(f"Invalid OTP from {addr}. Awaiting retry.")
        except ConnectionResetError:
            print(f"Connection lost with {addr} during OTP verification.")
            return

    # Loop for receiving messages from the client
    while True:
        try:
            conn.send(b"Enter a message (type 'exit' to disconnect): ")
            message = conn.recv(1024).decode().strip()
            if message.lower() == "exit":
                print(f"Connection closed by {addr}.")
                conn.send(b"Goodbye!\n")
                break
            else:
                print(f"Message from {addr}: {message}")
                conn.send(f"Server received: {message}\n".encode())
        except ConnectionResetError:
            print(f"Connection lost with {addr} during communication.")
            break  # Exit the loop if connection is lost

# Main function to start the server and listen for connections
def main():
    # Define a secure password for the server
    server_password = "Secure123!"  # Predefined secure password

    # Checks password security
    security_feedback = is_password_secure(server_password)
    if security_feedback:
        print(f"Server password error: {security_feedback}")
        return

    # Sets up the server socket and start listening for connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(1)
    print("Server is listening on port 5000...")

    while True:
        conn, addr = server_socket.accept()
        try:
            handle_client(conn, addr, server_password)
        finally:
            conn.close()

if __name__ == "__main__":
    main()
