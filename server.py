import socket
import struct
import sys
import json
import collections
import queue
import threading
from threading import Thread

MESSAGE_TYPE = collections.namedtuple('MessageType', ('client', 'node'))(*('client', 'node'))
lista_date = queue.Queue()

class Nod:
    def __init__(self, ip_multicast, server_multicast, ip_tcp, port_tcp, data, relation):
        self.ip_multicast = ip_multicast
        self.server_multicast = server_multicast
        self.ip_tcp = ip_tcp
        self.port_tcp = port_tcp
        self.data = data
        self.relation = relation

    def listen_udp(self):
        # Facem socketul
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Se leaga cu adresa serverului
        sock_udp.bind(self.server_multicast)

        # Adaugam sistemul la grupul multicast in toate interfetele

        group = socket.inet_aton(self.ip_multicast)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock_udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        relations = len(self.relation)

        while True:
            print("Astepare conexiuni")
            data, address = sock_udp.recvfrom(1024)
            data = data.decode('utf-8')
            # sys.stderr - Fluxul standart de erori.
            print(sys.stderr, 'primiti %s bytes mesaj de la %s' % (len(data), address))
            print(sys.stderr, data)

            print(sys.stderr, 'Trimit raspuns cu datele mele la :', address)

            # se creaza obiectul json cu datele si se trimite
            data = {
                'relations': relations,
                'ip_tcp': self.ip_tcp,
                'port_tcp': self.port_tcp
            }
            json_obj = json.dumps(data).encode('utf-8')
            print('datele mele sunt:', data)

            sock_udp.sendto(json_obj, address)
        # sfirsit conexiune udp

    def listen_tcp(self):

        # creare socket TCP ....... date utilizate pentru TCP
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.bind((self.ip_tcp, self.port_tcp))
        print('socket tcp in functiune')

        while True:
            clientsocket, addr = sock_tcp.accept()
            data = sock_tcp.recv(1024)
            data = json.loads(data.decode('utf-8'))
            type = data.get('type')

            if type == MESSAGE_TYPE.node:
                info = self.data.encode('utf-8')
                sock_tcp.send(info)

            if type == MESSAGE_TYPE.client:
                # facem citirea de pe fiecare nod
                i = 0
                relatii = len(self.relation)
                lista_date.put(self.data)

                while i < relatii:
                    # preluam prima relatie pentru a ne conecta la acest nod
                    ip, port = self.relation[i]
                    sock_node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_node.connect(ip, port)
                    # facem cererea la nod
                    cerere = {
                        'type': 'node',
                        'message': ''
                    }
                    jsonobj = json.dumps(cerere).encode('utf-8')
                    sock_node.send(jsonobj)

                    # asteptam raspuns de la nod
                    raspuns = sock_node.recv(1024)
                    raspuns = raspuns.decode('utf-8')
                    # adaugam raspunsul in lista de date
                    lista_date.put(raspuns)
                    sock_node.close()
                    i += 1

                # atit timp cit avem date in lista le trimitem clientului
                if lista_date:
                    m = lista_date.get()
                    # print(m)   # comentat de radu
                    sock_tcp.send(m.encode("utf-8"))

                else:
                    sock_tcp.send('Queue is empty')

            else:
                clientsocket.close()

# initiem nodurile
node1 = Nod('224.3.29.71', ('', 10000), '127.0.0.1', 9991, 'node1', [('127.0.0.2', '9992'), ('127.0.0.6', '9996')])
node2 = Nod('224.3.29.71', ('', 10000), '127.0.0.2', 9992, 'node2', [('127.0.0.1', '9991'), ('127.0.0.3', '9993'), ('127.0.0.6', '9996'), ('127.0.0.5', '9995')])
node3 = Nod('224.3.29.71', ('', 10000), '127.0.0.3', 9993, 'node3', [('127.0.0.2', '9992')])
node4 = Nod('224.3.29.71', ('', 10000), '127.0.0.4', 9994, 'node4', [])
node5 = Nod('224.3.29.71', ('', 10000), '127.0.0.5', 9995, 'node5', [('127.0.0.2', '9992')])
node6 = Nod('224.3.29.71', ('', 10000), '127.0.0.6', 9996, 'node6', [('127.0.0.1', '9991'), ('127.0.0.2', '9992')])

if __name__ == '__main__':
    Thread(target=node1.listen_tcp()).start()
    Thread(target=node1.listen_udp()).start()
