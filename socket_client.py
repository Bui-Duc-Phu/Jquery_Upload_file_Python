# Python client
import socket
import json

#sokket_client.py
def send_to_nodejs(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.0.109', 3002))

    # Chuyển dữ liệu thành JSON
    json_data = json.dumps(data)

    # Gửi độ dài dữ liệu trước
    client_socket.send(len(json_data.encode('utf-8')).to_bytes(4, byteorder='big'))

    # Gửi dữ liệu JSON
    client_socket.send(json_data.encode('utf-8'))

    client_socket.close()

