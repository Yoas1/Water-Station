from socket import *


def read_data_station():
    file = open('status2.txt', 'r')
    data = ', '.join(file.read().splitlines())
    file.close()
    return data


def data_send(client):
    try:
        while True:
            if read_data_station() == "":
                client.close()
                print("Station data broken or empty!")
                break
            data_from_server = client.recv(1024)
            if data_from_server.decode() == 'keep alive':
                print("\nKeep alive request received")
                client_status = read_data_station()
                client.send(bytes(client_status.encode()))
                print('Station status send!')
            if data_from_server.decode() == 'write_db':
                print("\nWrite to DataBase success!")
            elif data_from_server.decode() == 'error':
                print("""\nServer closed connection.
    Data format is incorrect. Please fix it and reconnect.""")
                break
    except OSError:
        print("Disconnect! the Connection was forcibly closed by the remote host.")


def main():
    client = socket(AF_INET, SOCK_STREAM)
    host = '127.0.0.1'
    port = 8080
    try:
        client.connect((host, port))
        print('Connecting to server\n')
    except ConnectionRefusedError as e:
        print("No connection append")
    data_send(client)


if __name__ == '__main__':
    main()

