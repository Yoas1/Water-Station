from sqlite3 import *
from socket import *
from _thread import *
from time import *
from datetime import *

thread_count = 0


def create_sql_table(table):
    table.execute('''CREATE TABLE IF NOT EXISTS data(
    Station_ID INT,
    Last_date TEXT,
    Alarm_1 INT,
    Alarm_2 INT,
    PRIMARY KEY(Station_ID))''')


def update_sql_table(table, values):
    table.executemany("INSERT OR REPLACE INTO data VALUES(?, ?, ?, ?)", values)
    table.commit()


def check_data(data):  # check the data received from client
    if len(data) != 3:
        return False
    elif not (data[0]).isdigit():
        return False
    elif not (data[1]).isdigit() or not (data[2]).isdigit():
        return False
    elif 0 > int(data[1]) or int(data[1]) > 1 or 0 > int(data[2]) or int(data[2]) > 1:
        return False


def threaded_client(client_connection):
    global thread_count
    count_client = thread_count
    try:
        while True:
            client_connection.send(bytes('keep alive'.encode()))
            data = client_connection.recv(1024)
            list_data = (data.decode().split(', '))
            if check_data(list_data) == 0:
                client_connection.send(bytes('error'.encode()))
                print("Data from client #{} is incorrect!".format(count_client))
                print("Client #{} Disconnect!".format(count_client))
                client_connection.close()
                thread_count -= 1
                break
            else:
                station_table = connect('data.sqlite')
                last_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                list_data.insert(1, last_date)
                print('\nClient #{} write to DataBase:\n'.format(count_client), list_data)
                values = [list_data]
                update_sql_table(station_table, values)
                client_connection.send(bytes('write_db'.encode()))
            station_table.close()
            sleep(5)  # change to 60 sec for receive data every minute.
    except ConnectionResetError:
        thread_count -= 1
        print("client #{} Disconnect! the Connection was forcibly closed by the client..".format(count_client))


def main():
    global thread_count
    server = socket(AF_INET, SOCK_STREAM)
    host = '0.0.0.0'
    port = 8080
    thread_count = 0
    try:
        server.bind((host, port))
        station_table = connect('data.sqlite')
        create_sql_table(station_table)
    except ConnectionRefusedError:
        print("No connection append")
    finally:
        print('Waiting for a Connection..')
        server.listen(5)
        while True:
            client, address = server.accept()
            thread_count += 1
            print('Client #{} Connected to server by: '.format(thread_count) + address[0] + ':' + str(address[1]))
            start_new_thread(threaded_client, (client,))  # start new thread for new client.


if __name__ == '__main__':
    main()
