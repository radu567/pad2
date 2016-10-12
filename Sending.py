import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = 'Hallio'
MESSAGE = str.encode(MESSAGE)

print("UDP target IP:", UDP_IP)

print("UDP target port:", UDP_PORT)
print("message:", MESSAGE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

while True:
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
