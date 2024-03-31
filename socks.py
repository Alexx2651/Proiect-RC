import tkinter as tkinter
import tkinter.ttk as ttk
import socket
import time
import threading
import struct

class SOCKS:
    def __init__(self):
        self.status=1
        self.data=''
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[+] Socket creat")

    def load(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        print("[=] Incarcat atribute")
        return

    def bind(self):
        print("[=] Incercat conexiune")
        i = 10
        while i>0:
            try:
                self.s.connect((self.ip_address, int(self.port)))
                print("[+] Connectat cu succes")
                threading.Thread(target=self.recv).start()
                break
            except:
                print("[-] Eroare conexiune")
                time.sleep(1)
                pass
        if(i==0):
            return 10

    def recv(self):
        data = b'' 
        while(self.status == 1):
            try:
                data = self.s.recv(4096)
                if data:
                    self.data = data
                    #.decode('utf-8')
                    #self.history.insert("end", data)
            except Exception as e:
                print(e, 'recv')
                time.sleep(1)
            pass

    def send(self, text:str):
        try:
            self.s.sendall(text.encode('utf-8'))
        except:
            print("[=] Not Connected")
            pass
