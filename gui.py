import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import random
from socks import SOCKS
import socket
import threading
import time
import struct

CONNECT = 0x10
CONNACK = 0x20
PUBLISH = 0x30
PUBACK = 0x40
PUBREC = 0x50
PUBREL = 0x60
PUBCOMP = 0x70
SUBSCRIBE = 0x80
SUBACK = 0x90
UNSUBSCRIBE = 0xA0
UNSUBACK = 0xB0
PINGREQ = 0xC0
PINGRESP = 0xD0
DISCONNECT = 0xE0


class MQTT_GUI:

    def conn(self):
        add=self.message1_entry.get()
        if(len(add)>1):
            bucati = add.split(':')
            adresa=bucati[0].split('.')
            if(len(adresa)!=4):
                self.print_text('Connection failed, enter a valid address.\n')
                return
        
            for i in adresa:
                if(int(i)<0 or int(i)>255):
                    self.print_text('Connection failed, enter a valid address.\n')
                    return

            if(int(bucati[1])<1 or int(bucati[1])>9999):
                self.print_text('Connection failed, enter a valid address.\n')
                return

            if(len(bucati)!=2):
                self.print_text('Connection failed, enter a valid address.\n')
                return
        self.username = self.user_entry.get()
        self.password = self.pass_entry.get()
        print('\nUSER:' + self.username +'\tPASS: '+self.password)
        if(not(len(self.username)==len(self.password) or (len(self.username)>0 and len(self.password)>0))):
            self.print_text('Error: You must insert both a username and a password.\n')
            return
        threading.Thread(target=self.socket_conn).start()
       
    def start_send_data(self):
        type = CONNECT
        clientid = self.name_entry.get()
        if(not clientid):
            clientid = 'mqttx_'+str(random.randint(1111,9999))
        if(self.qos_pick.get()):
            self.qos = int(self.qos_pick.get())
        else:
            self.print_text('No Quality of Service picked. Defaulting to 0.\n')
            self.qos = 0
        kl = self.keepalive_entry.get()
        if not kl:
            kl = 60
        self.keep = int(kl)
        id_len = len(clientid)
        length = 18 + len(clientid)
        protocol_name = 'MQTT'
        ver = 5
        conflag_reserved = 2
        prop_len = 5
        prop_id = 17
        prop_number = 300
        if(self.willtopic_entry.get() and self.will_entry.get()):
            conflag_reserved+=36
            conflag_reserved+=(self.qos<<3)
            will_topic = self.willtopic_entry.get()
            will_msg = self.will_entry.get()
            length+=5+len(will_topic)+len(will_msg)
            if(not(len(self.username) or len(self.password))):
                packet = struct.pack('!BBH4sBBHBBiH' + str(id_len) +'sBH'+str(len(will_topic))+'sH'+str(len(will_msg))+'s', type, length, 4, protocol_name.encode('utf-8'), ver, conflag_reserved, int(kl), prop_len, prop_id, prop_number, id_len, clientid.encode('utf-8'),0,len(will_topic), will_topic.encode('utf-8'), len(will_msg), will_msg.encode('utf-8'))
            else:
                len_user = len(self.username)
                len_pass = len(self.password)
                length+=(4+len_user+len_pass)
                conflag_reserved +=(12<<4) 
                packet = struct.pack('!BBH4sBBHBBiH' + str(id_len) +'sHB'+str(len(will_topic))+'sH'+str(len(will_msg))+'sH' + str(len_user) +'sH'+str(len_pass)+'s', type, length, 4, protocol_name.encode('utf-8'), ver, conflag_reserved, int(kl), prop_len, prop_id, prop_number, id_len, clientid.encode('utf-8'),0, len(will_topic), will_topic.encode('utf-8'), len(will_msg), will_msg.encode('utf-8'), len_user, self.username.encode('utf-8'), len_pass, self.password.encode('utf-8'))
            try:
                self.s.s.sendall(packet)
            except:
                pass
        else:
            if(not(len(self.username) or len(self.password))):
                packet = struct.pack('!BBH4sBBHBBiH' + str(id_len) +'s', type, length, 4, protocol_name.encode('utf-8'), ver, conflag_reserved, int(kl), prop_len, prop_id, prop_number, id_len, clientid.encode('utf-8'))
            else:
                len_user = len(self.username)
                len_pass = len(self.password)
                length+=(4+len_user+len_pass)
                conflag_reserved +=(12<<4) 
                packet = struct.pack('!BBH4sBBHBBiH' + str(id_len) +'sH' + str(len_user) +'sH'+str(len_pass)+'s', type, length, 4, protocol_name.encode('utf-8'), ver, conflag_reserved, int(kl), prop_len, prop_id, prop_number, id_len, clientid.encode('utf-8'), len_user, self.username.encode('utf-8'), len_pass, self.password.encode('utf-8'))
            try:
                self.s.s.sendall(packet)
            except:
                pass
       
    def socket_conn(self):
        add=self.message1_entry.get()
        bucati = add.split(':')
        adresa=bucati[0].split('.')
        self.print_text('Connecting...\n')
        self.s = SOCKS()
        if(len(add)>1):
            self.address = bucati[0]
            self.port = bucati[1]
        else:
            self.print_text('Connecting to default address and port...\n')
        self.s.load(self.address, int(self.port))
        try: 
            self.s.bind()
        except Exception as e:
            self.print_text('Connection error:' + str(e) + '\n')
            return
        self.start_send_data()
        self.status = 1
        start_time = time.time()
        packet = struct.pack('!H', PINGREQ<<8)
        while(self.status):
            if(not self.status):
                break
            curr_time = time.time()
            if(curr_time-start_time >= self.keep):
                self.s.s.sendall(packet)
                start_time = curr_time
            if(len(self.s.data)>2):
                data = self.s.data
                self.s.data = b''
                fixed_header = struct.unpack_from('2B', data, 0)
                type = fixed_header[0]
                length = fixed_header[1]
                self.MQTT_unpack(type, length, data)

    def disconn(self):
        self.dissconnect_button.pack_forget()
        self.connect_button = tk.Button(self.root,text="Connect", font=('Arial', 12), command=self.conn)
        self.connect_button.place(x=50,y=100,height=30,width=100)
        self.status = 0
        self.s.status = 0
        if(self.publishing):
            self.stop_publishing()
        self.packet_ids = list()
        self.topic_list = list()
        self.confirmed_packets = list()
        self.unconfirmed_packets = list()
        self.unconfirmed_pubrec = list()
        packet = [0xe0, 0x02, 0x8e, 0x00]
        self.s.s.sendall(bytes(packet))
        self.s.s.close()
        self.print_text('Disconnected.\n')

    def MQTT_unpack(self,type, length, data):
        print('\n~~RECEIVED NEW DATA~~\n')
        print("\tPACKET TYPE AND FLAGS:\t"+ str(hex(type)))
        print("\tREMAINING LENGTH:\t"+ str(length))
        if type == CONNACK:
            sess = struct.unpack_from('B', data,2)[0]
            reason_code = struct.unpack_from('B',data,3)[0]
            print('\tSESSION:\t'+str(sess))
            print('\tREASON CODE:\t'+str(reason_code))
            if(reason_code):
                self.print_text('Connection error.\n')
                self.status = 0
            else:
                self.print_text('Connected successfully!\n')
                self.status = 1
                remaining_things = struct.unpack_from(str(length-2)+'b',data,4)
                print('\tREMAINING:\t'+str(remaining_things))
                self.connect_button.pack_forget()
                self.dissconnect_button = tk.Button(self.root, text="Disconnect", font=('Arial', 12), command = self.disconn)
                self.dissconnect_button.place(x=50, y=100, height=30, width=100)
        elif type == SUBACK:
            self.print_text('Subscribed successfully!\n')
            pass
        elif ((type>>4)<<4) == PUBLISH:
            mesg_qos = ((type%8)>>1)
            print('\nMESG QOS: '+str(mesg_qos)+'\n')
            if(mesg_qos == 0):
                topic_len = struct.unpack_from('!H', data, 2)[0]
                prop_len = struct.unpack_from('B', data, 4+topic_len)[0]
                topic_name = struct.unpack_from('!' + str(topic_len)+'s', data, 4)[0].decode('utf-8')
                msg = struct.unpack_from(str(length - 1 - topic_len- prop_len) + 's', data, 3+prop_len + topic_len)[0].decode('utf-8')[2:]
                self.print_text(str(topic_name) + ': ' + str(msg)+ '\n')
            elif (mesg_qos == 1):
                topic_len = struct.unpack_from('!H', data, 2)[0]
                prop_len = struct.unpack_from('B', data, 4+topic_len)[0]
                topic_name = struct.unpack_from('!' + str(topic_len)+'s', data, 4)[0].decode('utf-8')
                msg = struct.unpack_from(str(length - 1 -prop_len  - topic_len) + 's', data, 3+prop_len + topic_len)[0].decode('utf-8')[2:]
                self.print_text(str(topic_name) + ': ' + str(msg)+ '\n')
            elif (mesg_qos == 2):
                topic_len = struct.unpack_from('!H', data, 2)[0]
                prop_len = struct.unpack_from('B', data, 4+topic_len)[0]
                topic_name = struct.unpack_from('!' + str(topic_len)+'s', data, 4)[0].decode('utf-8')
                msg = struct.unpack_from(str(length - 1 -prop_len  - topic_len) + 's', data, 3+prop_len + topic_len)[0].decode('utf-8')[2:]
                self.print_text(str(topic_name) + ': ' + str(msg)+ '\n')
        elif type == PUBACK:
            self.packet_confirmed = 1
            pass
        elif type == PUBREC:
            self.pubrec_id = int(self.get_packetid(data)[0])
            self.pubrec_confirmed = 1
        elif type == PUBCOMP:
            self.pubcomp_confirmed = 1
        elif type == UNSUBACK:
            self.print_text('Unsubscribed successfully!\n')
            pass

    def sub(self):
        topic = self.message2_entry.get()
        if(not self.status):
            self.print_text('Not connected to any broker.\n')
            return
        if topic in self.topic_list:
            self.print_text('Topic already subscribed to!\n')
            return
        self.topic_list.append(topic)
        type = (8 << 4) + 2
        packet_id = random.randint(1,9999)
        self.packet_ids.append(packet_id)
        prop_length = 0
        topic_length = len(topic)  
        flags = self.qos
        print(topic + ' '+ str(type) + ' ' + str(packet_id) + ' ' + str(topic_length) + ' bytes: ') 
        #byte_topic = bytearray(topic.encode('utf-8'))
        #print(byte_topic)
        self.print_text('Attempting to subscribe...\n')
        packet = struct.pack('!BBhBh' + str(topic_length)+'sB', type, (topic_length + 6), packet_id, prop_length, topic_length, topic.encode('utf-8'), flags)
        self.s.s.sendall(packet)

    def unsub(self):
        topic = self.message2_entry.get()
        if(not self.status):
            self.print_text('Not connected to any broker.\n')
            return
        if topic not in self.topic_list:
            self.print_text('Topic not subscribed to!\n')
            return
        packet_id = 0
        for i in range(len(self.topic_list)):
            if(topic == self.topic_list[i]):
                packet_id = self.packet_ids[i]
        type = (10 << 4) + 2
        prop_length = 0
        topic_length = len(topic)  
        print(topic + ' '+ str(type) + ' ' + str(packet_id) + ' ' + str(topic_length) + ' bytes: ') 
        self.print_text('Attempting to unsubscribe...\n')
        packet = struct.pack('!BBhBh' + str(topic_length)+'s', type, (topic_length + 5), packet_id, prop_length, topic_length, topic.encode('utf-8'))
        self.s.s.sendall(packet)

    def keepalive_start(self): 
        threading.Thread(target=self.keepalive()).start()

    def pub(self, topic, data, qos):
        type = (3 << 4) + qos*2
        topic_length = len(topic)
        mesg_expr = 2
        val = 300
        mesg_id = 0
        ident = 8
        ident_val = 'response'
        payload = data.encode('utf-8')
        remain_length = 8+ topic_length + len(data)
        if(self.qos):
            mesg_id = random.randint(1,9999) 
            remain_length+=2
            packet = struct.pack('!BBH' + str(topic_length) + 'sHBBi' + str(len(payload)) +'s', type, remain_length, topic_length, topic.encode('utf-8'),mesg_id, 5, mesg_expr, val, payload)  
        else:
            packet = struct.pack('!BBH' + str(topic_length) + 'sBBi' + str(len(payload)) +'s', type, remain_length, topic_length, topic.encode('utf-8'), 5, mesg_expr, val, payload)  
        self.s.s.sendall(packet)
        if(self.qos == 1):
            self.packet_confirmed = 0
            while(not self.packet_confirmed):
                time.sleep(1)
                if(not self.packet_confirmed):
                    self.s.s.sendall(packet)
        if(self.qos == 2):
            self.pubcomp_confirmed = 0
            self.pubrec_confirmed = 0
            while(not self.pubrec_confirmed):
                time.sleep(1)
                if(not self.pubrec_confirmed):
                    self.s.s.sendall(packet)
            pubrel = struct.pack('!BBHB',0x62,3,mesg_id,0)
            self.s.s.sendall(packet)
            while(not self.pubcomp_confirmed):
                time.sleep(1)
                if(not self.pubcomp_confirmed):
                    self.s.s.sendall(pubrel)


    def stop_publishing(self):
        self.publishing = 0
        self.publish_button.pack_forget()
        self.publish_button=tk.Button(self.root,text="Start Publish",font=('Arial',12), command = self.start_publishing)
        self.publish_button.place(x=50,y=400,height=30,width=100)
        self.print_text('Stopped publishing.\n')
    
    def start_publishing(self):
        if(not self.status):
            self.print_text('Not connected to any broker.\n')
            return
        self.print_text('Publishing system parameters...\n')
        self.publishing = 1
        self.publish_button.pack_forget()
        self.publish_button=tk.Button(self.root,text="Stop Publish",font=('Arial',12), command = self.stop_publishing)
        self.publish_button.place(x=50,y=400,height=30,width=100)
        threading.Thread(target=self.publish_data).start()
    
    def publish_data(self):
        while 1:
            if(not self.publishing):
                break
            self.pub('cpu/temp', str(random.randint(50,55))+'C', self.qos)
            self.pub('cpu/usage', str(random.randint(40,65))+'%', self.qos)
            self.pub('mem/usage', str(random.randint(60,65))+'%', self.qos)
            time.sleep(1)

    def print_text(self, text):
        self.textbook.configure(state = 'normal')
        self.textbook.insert(tk.INSERT, text)
        self.textbook.configure(state = 'disabled')
        self.textbook.see("end")

    def keepalive(self):
        while(not self.status):
            pass
        packet = struct.pack('!H', PINGREQ<<8)
        while(self.status):
            self.print_text(str(packet)+'\n')
            for i in range(0,self.keep-1):
                if(not self.status):
                    break
                time.sleep(1)
            if(self.status):
                self.s.s.sendall(packet)

    def exit_app(self):
        if(self.status):
            self.disconn()
        self.root.destroy()

    def get_packetid(self, packet):
        return struct.unpack_from('!H', packet, 2)

    def __init__(self):
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = '127.0.0.1'
        self.port = 1883
        self.packet_ids = list()
        self.topic_list = list()
        self.confirmed_packets = list()
        self.unconfirmed_packets = list()
        self.unconfirmed_pubrec = list()
        self.packet_confirmed = 1
        self.pubrec_id = 0000
        self.root=tk.Tk()
        self.root.geometry("810x850")
        self.root.title("MQTT CLIENT")
        self.qos = 0
        self.status = 0
        self.publishing = 0 
        self.label_messagebox=tk.Label(self.root,text="Message Box",font=('Arial',12))
        self.label_messagebox.place(x=290,y=400)

        self.textbook=scrolledtext.ScrolledText(self.root,height=13,width=60,font=('Arial',16))
        self.textbook.place(x=50,y=450)
        self.textbook.configure(state ='disabled')

        self.connect_button = tk.Button(self.root,text="Connect", font=('Arial', 12), command=self.conn)
        self.connect_button.place(x=50,y=100,height=30,width=100)

        self.message1_entry=tk.Entry(self.root,width=60)
        self.message1_entry.place(x=200,y=100)

        self.name_entry=tk.Entry(self.root,width=15)
        self.name_entry.place(x=200,y=150)
        self.label_name=tk.Label(self.root,text="Client name:",font=('Arial',12))
        self.label_name.place(x=100,y=150)

        self.user_entry=tk.Entry(self.root,width=15)
        self.user_entry.place(x=200,y=180)
        self.label_user=tk.Label(self.root,text="User:",font=('Arial',12))
        self.label_user.place(x=100,y=180)
        self.pass_entry=tk.Entry(self.root,width=15)
        self.pass_entry.place(x=420,y=180)
        self.keepalive_entry=tk.Entry(self.root,width=5)
        self.label_pass=tk.Label(self.root,text="Pass:",font=('Arial',12))
        self.label_pass.place(x=330,y=180)
        self.keepalive_entry.place(x=420,y=150)
        self.label_keepalive=tk.Label(self.root,text="KeepAlive:",font=('Arial',12))
        self.label_keepalive.place(x=330,y=150)

        self.will_entry=tk.Entry(self.root,width=15)
        self.will_entry.place(x=200,y=210)
        self.label_will=tk.Label(self.root,text="Last Will:",font=('Arial',12))
        self.label_will.place(x=100,y=210)
        self.willtopic_entry=tk.Entry(self.root,width=15)
        self.willtopic_entry.place(x=420,y=210)
        self.label_willtopic=tk.Label(self.root,text="Topic:",font=('Arial',12))
        self.label_willtopic.place(x=330,y=210)

        self.label_ConnectButton=tk.Label(self.root,text="Insert an address to connect to",font=('Arial',12))
        self.label_ConnectButton.place(x=310,y=70)

        self.message2_entry = tk.Entry(self.root, width=60)
        self.message2_entry.place(x=200, y=300)

        self.subscribe_button=tk.Button(self.root,text="Subscribe",font=('Arial',12), command = self.sub)
        self.subscribe_button.place(x=50,y=300,height=30,width=100)

        
        self.unsubscribe_button=tk.Button(self.root,text="Unsubscribe",font=('Arial',12), command = self.unsub)
        self.unsubscribe_button.place(x=50,y=350,height=30,width=100)

        self.publish_button=tk.Button(self.root,text="Start Publish",font=('Arial',12), command = self.start_publishing)
        self.publish_button.place(x=50,y=400,height=30,width=100)

        self.label_SubscribeButton = tk.Label(self.root, text="Choose the topic to subscribe to", font=('Arial', 12))
        self.label_SubscribeButton.place(x=330, y=270)

        self.root.protocol('WM_DELETE_WINDOW', self.exit_app)
        
        self.qos_pick = ttk.Combobox(self.root)
        self.qos_pick['values']=(0, 1, 2)
        self.qos_pick['state']='readonly'
        self.qos_pick.pack()
        self.qos_pick.place(x = 510, y = 150, width = 35, height = 25)
        self.label_qos=tk.Label(self.root,text="QoS:",font=('Arial',12))
        self.label_qos.place(x=470,y=150)

    
