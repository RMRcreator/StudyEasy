import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9999)) # specify the public IP address of the service, host on private connect on the public

message = client.recv(1024).decode()
client.send(input(message).encode())
message = client.recv(1024).decode()
client.send(input(message).encode())
print(client.recv(1024).decode())