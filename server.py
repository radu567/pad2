import socket
import struct
import sys
import json


class Group:
    def __init__(self, ip_multicast, port_multicast, ip_tcp, port_tcp, data, relation):
        self.ip_multicast = ip_multicast
        self.port_multicast = port_multicast
        self.ip_tcp = ip_tcp
        self.port_tcp = port_tcp
        self.data = data
        self.relation = relation

    def run(self):

        # Facem socketul
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.bind((self.ip_multicast, self.port_multicast))

        # Adaugam sistemul la grupul multicast in toate interfetele
        group = socket.inet_aton(self.ip_multicast)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock_udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        relations = len(self.relation)

        # Receive/respond loop (bulca)

        while True:
            print("Astepare conexiuni")
            data, address = sock_udp.recvfrom(1024)
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
            sock_udp.sendto(json_obj)

        # creare socket TCP
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.connect(self.ip_tcp, self.port_tcp)

        while True:
            clientsocket, addr = sock_tcp.accept()
            info = sock_tcp.recv(1024)
            if info:
                print(info)
            else:
                clientsocket.close()

node1 = Group('224.3.0.64', 10000, '127.0.0.1', '9991', 'node1', [('127.0.0.1', '9992'), ('127.0.0.3', '9993')])
node1.run()
