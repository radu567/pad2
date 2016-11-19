import socket
import struct
import sys
import json
import collections
import queue

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
        sock_tcp.connect(self.ip_tcp, self.port_tcp)

        while True:
            clientsocket, addr = sock_tcp.accept()
            data = sock_tcp.recv(1024)
            data = json.loads(data.decode('utf-8'))
            type = data.get('type')

            if type == MESSAGE_TYPE.node:
                info = self.data.encode('utf-8')
                sock_tcp.send(info)
            if type == MESSAGE_TYPE.client:
                cerere = {
                    'type': 'node',
                    'message': ''
                }
                jsonobj = json.dumps(cerere).encode('utf-8')
                sock_tcp.send(jsonobj)

                raspuns = sock_tcp.recv(1024)
                raspuns = raspuns.decode('utf-8')

                lista_date.put(raspuns)


            else:
                clientsocket.close()


node1 = Nod('224.3.29.71', ('', 10000), '127.0.0.1', '9991', 'node1', [('127.0.0.1', '9992'), ('127.0.0.3', '9993')])
node1.listen_udp()
