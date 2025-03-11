import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 9999))  # specify the public IP address of the service, host on private connect on the public

    while True:
        # try to read server message
        server_message = client.recv(1024)
        if not server_message:
            # connection closed by server
            print("Server closed the connection.")
            break

        # decodes and displays the prompt/message
        prompt = server_message.decode()
        user_input = input(prompt)

        # sends the user’s response
        client.send(user_input.encode())

    client.close()

if __name__ == "__main__":
    main()