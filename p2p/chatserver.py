"""
To run this code, you need to run the following command in your terminal:
	twistd -y chatserver.py
And to send messages on the server you need to connect to the 1025 port with telnet

/!\ Attention, the port should be closed after usage by killing the process
"""
from __future__ import print_function

from twisted.protocols import basic



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
			self.sendLine("Welcome {} join us!".format(peerIP))
			self.state = "CHAT" 
			print("Got new client: {}".format(peerIP))
			self.factory.clients.append(self)
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

application = service.Application("chatserver")
internet.TCPServer(1026, factory).setServiceParent(application)


