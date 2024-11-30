import socket

def send_command(target_ip, target_port, command):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((target_ip, target_port))
        client_socket.send(command.encode('ascii'))
        print(f"Command sent to {target_ip}:{target_port}")
    except Exception as e:
        print(f"Error sending command to {target_ip}:{target_port}: {e}")
    finally:
        client_socket.close()

def main():
    targets = [
        ('192.168.0.1', 12345)
        # Добавьте другие IP-адреса и порты, если необходимо
    ]

    packet_size = 1500
    target_ip = '192.168.0.1'
    command = f"{packet_size};{target_ip}"

    for target in targets:
        send_command(target[0], target[1], command)

if __name__ == "__main__":
    main()
