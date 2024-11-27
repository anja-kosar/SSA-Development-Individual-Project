import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 5000))

    while True:
        # Below will receive and print password prompt from server and send password input
        server_message = client_socket.recv(1024).decode().strip()
        print(server_message)

        # Below is a password input from the client side
        user_input = input("> ")
        client_socket.send(user_input.encode())

        # Below provides authentication feedback from the server
        auth_feedback = client_socket.recv(1024).decode().strip()
        print(auth_feedback)

        # If authentication is successful, user will receive OTP prompt from server and enter OTP
        if "Please enter the OTP" in auth_feedback:
            otp_input = input("Enter OTP: ")
            client_socket.send(otp_input.encode())

            # OTP verification feedback
            otp_feedback = client_socket.recv(1024).decode().strip()
            print(otp_feedback)

            if "OTP verified" in otp_feedback:
                break  # Proceed to communication after OTP verification

        # Allow 'exit' to disconnect
        if user_input.lower() == "exit":
            print("Disconnected from the server.")
            break

    client_socket.close()

if __name__ == "__main__":
    main()
