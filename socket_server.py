import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('localhost', 3030))  # Привязываем серверный сокет к localhost и 3030 порту.
s.listen(1)  # Начинаем прослушивать входящие соединения.
conn, addr = s.accept()  # Метод который принимает входящее соединение.

while True:
    data = conn.recv(10000000000).decode()  # Получаем данные из сокета.
    if not data:
        break
    conn.send(data.encode())  # Отправляем данные в сокет.
    print(data)
conn.close()
