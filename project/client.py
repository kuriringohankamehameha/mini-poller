import socket

UDP_IP = '127.0.0.1'
UDP_PORT = 8081

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(bytes("Hello World!", "utf-8"), (UDP_IP, UDP_PORT))