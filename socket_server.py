import socket
import jsonpickle

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('localhost', 3030))  # Привязываем серверный сокет к localhost и 3030 порту.
s.listen(1)  # Начинаем прослушивать входящие соединения.
conn, addr = s.accept()  # Метод который принимает входящее соединение.

from BFV_demo import *

while True:
    data = conn.recv(10000000000).decode()  # Получаем данные из сокета.
    if not data:
        break
    # cct1 = jsonpickle.decode(data[0])


    conn.send(data.encode())  # Отправляем данные в сокет.
    print(data)
conn.close()
