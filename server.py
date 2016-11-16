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

    def run(self, sock_udp, sock_tcp):
        self.sock_udp = sock_udp
        self.sock_tcp = sock_tcp
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
        self.sock_tcp.connect(self.ip_tcp, self.port_tcp)

        while True:
            clientsocket, addr = self.sock_tcp.accept()
            info = self.sock_tcp.recv(1024)
            if info:
                print(info)
            else:
                clientsocket.close()


# date utilizate pentru TCP
sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



# date utilizate pentru UDP
ip = '224.3.0.64'
port = 10000
# Facem socketul
sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_udp.bind((ip, port))

# Adaugam sistemul la grupul multicast in toate interfetele
group = socket.inet_aton(ip)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock_udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


node1 = Group('224.3.0.64', 10000, '127.0.0.1', '9991', 'node1', [('127.0.0.1', '9992'), ('127.0.0.3', '9993')])
node1.run(sock_udp, sock_tcp)
