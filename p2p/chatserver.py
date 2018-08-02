"""
To run this code, you need to run the following command in your terminal:
	twistd -y chatserver.py
And to send messages on the server you need to connect to the 1025 port with telnet

/!\ Attention, the port should be closed after usage by killing the process
"""
from __future__ import print_function

from twisted.protocols import basic
import os
import uuid
import socket
import time


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
 
    return ip

nodes_list = []
ip_addr = get_host_ip()
print("Chat server {}".format(ip_addr))
n = dict(index=0,ip=ip_addr,time= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
nodes_list.append(n)

path = os.getcwd()
l = path.split('/')
fileloc = str('/' + l[1] + '/'+ l[2] + '/')
os.chdir(fileloc)
filename = fileloc + 'map.txt'
fp = open (filename, "wb")
fp.write("{} {} {}\n".format(nodes_list[0]["index"],nodes_list[0]["ip"],nodes_list[0]["time"]))
fp.close()

class MyChat(basic.LineReceiver):
	def __init__(self):
		self._peer = None
		self.answer = "c"
		self.state = "VERIFY"

	def connectionMade(self):
		self.sendLine("An apple a day keeps the doctor away\r\n")

	def connectionLost(self, answer):
		peerIP = str(self._peer).split("'")[1]
		print("Lost a client: {} ".format(peerIP))
		self.factory.clients.remove(self)

	def lineReceived(self, line):
		if self.state == "VERIFY":
			self.handle_VERIFY(line)
		else: 
		 	self.handle_CHAT(line)

	def handle_VERIFY(self, answer):
		if answer == "GOOD": 
			self._peer = self.transport.getPeer()
			peerIP = str(self._peer).split("'")[1]

			flag = 1
			for node in nodes_list:
				if node["ip"] == peerIP:
					self.sendLine("This IP alreay in use. \n")
					flag = 0
					break
				else:
					flag = 1

			if flag == 1:
				self.sendLine("Welcome {} join us!".format(peerIP))
				self.state = "CHAT" 
				print("Got new client: {}".format(peerIP))
				self.factory.clients.append(self)
				n = dict(index=len(nodes_list),ip=peerIP,time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
				nodes_list.append(n)
				fp = open ("map.txt","wb")
				ii = 0
				for node in nodes_list:
					fp.write("{} {} {}\r\n".format(node["index"],node["ip"],node["time"]))
					ii += 1
				fp.close()
		else:
			self.sendLine("Command password error!")

	def handle_CHAT(self,line):
		peerIP = str(self._peer).split("'")[1] 
		print("received from {}:".format(peerIP), repr(line))
		for c in self.factory.clients:
			c.message(line)
	def message(self, message):
		peerIP = str(self._peer).split("'")[1]
                self.transport.write(b"From {} : {}\n".format(peerIP,message))


from twisted.internet import protocol
from twisted.application import service, internet

factory = protocol.ServerFactory()
factory.protocol = MyChat
factory.clients = []

if __name__ == '__main__':
    from twisted.internet import reactor
    reactor.listenTCP(1026, factory)
    reactor.run()
else:
    application = service.Application("chatserver")
    internet.TCPServer(1026, factory).setServiceParent(application)

#application = service.Application("chatserver")
#internet.TCPServer(1026, factory).setServiceParent(application)


