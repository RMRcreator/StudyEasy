import sqlite3
import hashlib
import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))  # change to the local host/IP
server.listen()

def handle_connection(c):
    # Step 1: Ask the user if they want to sign up or log in
    c.send("Do you want to log in (1) or create an account (2)? ".encode())
    choice = c.recv(1024).decode().strip()

    if choice == "2":
        # -------- SIGN-UP LOGIC --------
        c.send("Choose a username: ".encode())
        username = c.recv(1024).decode().strip()

        c.send("Choose a password: ".encode())
        raw_password = c.recv(1024).strip()
        hashed_password = hashlib.sha256(raw_password).hexdigest()

        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()

        # checks if this username already exists
        cur.execute("SELECT * FROM userdata WHERE username = ?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            c.send("Username already taken. Please try again.\n".encode())
        else:
            cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)",
                        (username, hashed_password))
            conn.commit()
            c.send("Account created successfully!\n".encode())

        conn.close()
        c.close()

    else:
        # -------- LOGIN LOGIC --------
        c.send("Username: ".encode())
        username = c.recv(1024).decode().strip()

        c.send("Password: ".encode())
        raw_password = c.recv(1024).strip()
        hashed_password = hashlib.sha256(raw_password).hexdigest()

        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()

        # checks credentials
        cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?",
                    (username, hashed_password))
        result = cur.fetchall()

        if result:
            c.send("Login successful!\n".encode())
        else:
            c.send("Login failed!\n".encode())

        conn.close()
        c.close()

def start_server():
    print("Server listening on port 9999...")
    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_connection, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
