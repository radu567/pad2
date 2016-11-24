import socket
import struct
import sys
import json
import collections
import queue
from threading import Thread


MESSAGE_TYPE = collections.namedtuple('MessageType', ('client', 'node'))(*('client', 'node'))
lista_date = queue.Queue()


class Nod(object):
    def __init__(self, ip_multicast, server_multicast, ip_tcp, port_tcp, data, relation):
        self.ip_multicast = ip_multicast
        self.server_multicast = server_multicast
        self.ip_tcp = ip_tcp
        self.port_tcp = port_tcp
        self.data = data
        self.relation = relation

        self.thread1 = Thread(target=self.listen_udp)
        self.thread2 = Thread(target=self.listen_tcp)

    def listen_udp(self):
        # Facem socketul
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
        sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_tcp.bind((self.ip_tcp, self.port_tcp))

        while True:
            sock_tcp.listen(6)

            clientsocket, addr = sock_tcp.accept()
            print('socket tcp in functiune')

            data = clientsocket.recv(1024)
            data = json.loads(data.decode('utf-8'))
            types = data.get('type')

            if types == MESSAGE_TYPE.node:
                info = self.data.encode('utf-8')
                clientsocket.send(info)
                print('am trimis nodului principal mesajul meu')

            if types == MESSAGE_TYPE.client:
                # facem citirea de pe fiecare nod
                i = 0
                relatii = len(self.relation)
                lista_date.put(self.data)

                # pentru testare adaugam scoaterea imediata din lista si trimiterea la client
                m1 = lista_date.get()
                # print(m)   # comentat de radu
                clientsocket.send(m1.encode("utf-8"))

                while i < relatii:
                    # preluam prima relatie pentru a ne conecta la acest nod
                    ip, port = self.relation[i]
                    sock_node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_node.connect((ip, port))
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
                    print('raspunsul primit de la vecin este : ', raspuns)
                    lista_date.put(raspuns)
                    sock_node.close()
                    i += 1

                    # atit timp cit avem date in lista le trimitem clientului
                    # pentru testare trimitem mesajul primit de la nod imediat clientului
                    # if lista_date:

                    m = lista_date.get()
                    # print(m)   # comentat de radu
                    clientsocket.send(m.encode("utf-8"))

                else:
                    final = 'Queue is empty'
                    final = final.encode('utf-8')
                    clientsocket.send(final)

            else:
                clientsocket.close()

    def run(self):
        self.thread1.start()
        self.thread2.start()

    def stop(self):
        self.thread1.join()
        self.thread2.join()


# initiem nodurile
node1 = Nod('224.3.29.71', ('', 10000), '127.0.0.1', 9991, 'node1', [('127.0.0.2', 9992), ('127.0.0.6', 9996)])
node2 = Nod('224.3.29.71', ('', 10000), '127.0.0.2', 9992, 'node2', [('127.0.0.1', 9991), ('127.0.0.3', 9993),
                                                                     ('127.0.0.6', 9996), ('127.0.0.5', 9995)])
node3 = Nod('224.3.29.71', ('', 10000), '127.0.0.3', 9993, 'node3', [('127.0.0.2', 9992)])
node4 = Nod('224.3.29.71', ('', 10000), '127.0.0.4', 9994, 'node4', [])
node5 = Nod('224.3.29.71', ('', 10000), '127.0.0.5', 9995, 'node5', [('127.0.0.2', 9992)])
node6 = Nod('224.3.29.71', ('', 10000), '127.0.0.6', 9996, 'node6', [('127.0.0.1', 9991), ('127.0.0.2', 9992)])

nodes = [node1, node2, node3, node4, node5, node6]


for node in nodes:
    node.run()

for node in nodes:
    node.stop()
