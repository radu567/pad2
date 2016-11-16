import socket
import struct
import sys
import json

message = 'Clientul cere informatie'
message = str.encode(message)
multicast_group = ('224.3.29.71', 10000)

# Se creaza datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Setare timp pentru mesaje
sock.settimeout(2)

# Setare timp pentru viata mesajelor 1 astfel încât acestea să nu mearg dincolo de segmentul de rețea locală.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# datele pentru tratarea celui mai important nod cu tcp
i = 0
rel = []
ip = []
port = []

while i < 6:

    # Trimite date la grupul multicast
    print(sys.stderr, 'sending "%s"' % message)
    sent = sock.sendto(message, multicast_group)

    # Cautare raspunsuri de la destinatari
    while i < 6:
        print(sys.stderr, 'waiting to receive')
        try:
            # se primeste segmentul de date si se citeste din json
            data = sock.recvfrom(2048)
            data = json.loads(data.decode('utf-8'))
            relations = data.get('relations')
            ip_tcp = data.get('ip_tcp')
            port_tcp = data.get('port_tcp')

        except socket.timeout:
            print(sys.stderr, 'timed out, no more responses')
            break
        else:
            print(sys.stderr, '1 nod are %s legaturi, ip-ul: %s si portul: %s' % (relations, ip_tcp, port_tcp))
            rel.append(relations)
            ip.append(ip_tcp)
            port.append(port_tcp)

print(sys.stderr, 'closing socket')
sock.close()

# cautam nodul cu cele mai multe relatii
pozitia = rel.index(max(rel))
sock_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_TCP.bind(ip[pozitia], port[pozitia])
sock_TCP.listen(5)

while True:

    datas = sock_TCP.recv(1024)
    datas = datas.decode('utf-8')
    print(datas)
