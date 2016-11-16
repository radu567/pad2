import socket
import struct
import sys
import json

class Group:
    def run(self, ip_multicast, port_multicast, ip_tcp, port_tcp, data, relation):
        # self.adr = (ip_multicast, port_multicast, relation)

        # Facem socketul
        sock_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_UDP.bind((ip_multicast, port_multicast))

        # Adaugam sistemul la grupul multicast in toate interfetele
        group = socket.inet_aton(ip_multicast)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock_UDP.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        relations = len(relation)

        # Receive/respond loop (bulca)

        while True:
            print("Astepare conexiuni")
            data, address = sock_UDP.recvfrom(1024)
            # sys.stderr - Fluxul standart de erori.
            print(sys.stderr, 'primiti %s bytes mesaj de la %s' % (len(data), address))
            print(sys.stderr, data)

            print(sys.stderr, 'Trimit raspuns cu datele mele la :', address)

            # se creaza obiectul json cu datele si se trimite
            data = {
                'relations': relations,
                'ip_tcp': ip_tcp,
                'port_tcp': port_tcp
            }
            jsonObj = json.dumps(data).encode('utf-8')
            sock_UDP.sendto(jsonObj)

        # creare socket TCP
        sock_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_TCP.connect(ip_tcp, port_tcp)

        while True:
            clientsocket, addr = sock_TCP.accept()
            info = sock_TCP.recv(1024)
            if info:
                print(info)
            else:
                clientsocket.close()

node1 = Group
node1.run('224.3.29.71', 10000, '127.0.0.1', '9991', 'node1', [('127.0.0.2', '9992'), ('127.0.0.3', '9993'), ('127.0.0.4', '9994')])
