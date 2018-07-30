'''
title           : blockchain_client.py
description     : A blockchain client implemenation, with the following features
                  - Wallets generation using Public/Private key encryption (based on RSA algorithm)
                  - Generation of transactions with RSA encryption      
usage           : python blockchain_client.py
                  python blockchain_client.py -p 8080
                  python blockchain_client.py --port 8080
python_version  : 3.6.1
Comments        : Wallet generation and transaction signature is based on [1]
References      : [1] https://github.com/julienr/ipynb_playground/blob/master/bitcoin/dumbcoin/dumbcoin.ipynb
'''

from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template

from telnetlib import Telnet


class Task:

    def __init__(self, sender_address, sender_private_key, task_description, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.task_description = task_description
        self.value = value

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'task_description': self.task_description,
                            'value': self.value})

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


def telnet_connect(msg):
        HOST = '100.98.10.148'
        PORT = 1025

        tn = Telnet(HOST, PORT)
        line = tn.read_until("An apple a day keeps the doctor away\r\n")
        print(line)

        tn.write(b'GOOD\r\n')
        line = tn.read_until("\n")
        print(line)
        tx = ''

        for key, value in msg.items():
                tx += key + ': ' + str(value) + '\r\n'
        print("Sending data: {}".format(tx))
        tn.write(b'{}'.format(tx))
        line = tn.read_until("\n")

        print("Closing the connection ...")
        tn.close()



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/announcer')
def announcer():
    return render_template('./announcer.html')

@app.route('/submit', methods=['POST'])
def generate_transaction():



@app.route('/confirm', methods=['POST'])
def confirm_task():

    sender_address = request.form['sender_address']
    sender_private_key = request.form['sender_private_key']
    task_description = request.form['task_description']
    value = request.form['amount']

    transaction = Task(sender_address, sender_private_key, task_description, value)

    response = {'transaction': transaction.to_dict(), 'signature': transaction.sign_transaction()}
    # telnet_connect(response)
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
