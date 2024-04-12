from hashlib import sha256, new, sha3_512
from base58 import b58encode
from binascii import hexlify, unhexlify
from ecdsa import SigningKey, SECP256k1
from random import randint
from json import loads
from os import system, name
from time import time

class Puzzle():
    def __init__(self):
        self.count = 0
        self.found = False
        self.GREEN = '\033[32m'
        self.DEFAULT = '\033[39m'
        self.RED = '\033[31m'
        system('cls' if name == 'nt' else 'clear')
        self.print_art()
        puzzle_length = self.get_puzzle_length()
        try:
            cmd = int(input(f'Enter Puzzle Number (0 - {puzzle_length-1}): '))
            if cmd >= puzzle_length:exit()
        except:exit()
        self.puzzle = self.get_puzzle(cmd)
        self.start = int(self.puzzle['start'], 16)
        self.end = int(self.puzzle['end'], 16)
        self.address = self.puzzle['address']
        self.reward = float(self.puzzle['reward'])
        try:self.seek()
        except:pass

    def print_art(self):
        print(f'''{self.RED} ▄▄▄▄    ██▓▄▄▄█████▓    ██▓███   █    ██ ▒███████▒▒███████▒
▓█████▄ ▓██▒▓  ██▒ ▓▒   ▓██░  ██▒ ██  ▓██▒▒ ▒ ▒ ▄▀░▒ ▒ ▒ ▄▀░
▒██▒ ▄██▒██▒▒ ▓██░ ▒░   ▓██░ ██▓▒▓██  ▒██░░ ▒ ▄▀▒░ ░ ▒ ▄▀▒░ 
▒██░█▀  ░██░░ ▓██▓ ░    ▒██▄█▓▒ ▒▓▓█  ░██░  ▄▀▒   ░  ▄▀▒   ░
░▓█  ▀█▓░██░  ▒██▒ ░    ▒██▒ ░  ░▒▒█████▓ ▒███████▒▒███████▒
░▒▓███▀▒░▓    ▒ ░░      ▒▓▒░ ░  ░░▒▓▒ ▒ ▒ ░▒▒ ▓░▒░▒░▒▒ ▓░▒░▒
▒░▒   ░  ▒ ░    ░       ░▒ ░     ░░▒░ ░ ░ ░░▒ ▒ ░ ▒░░▒ ▒ ░ ▒
 ░    ░  ▒ ░  ░         ░░        ░░░ ░ ░ ░ ░ ░ ░ ░░ ░ ░ ░ ░
 ░       ░                          ░       ░ ░      ░ ░    
      ░                                   ░        ░        {self.DEFAULT}v0.1.2\n\n''')



    def get_puzzle_length(self):
        return len(loads(open('data.json').read()))

    def get_puzzle(self, n):
        data = loads(open('data.json').read())[str(n)]
        return data

    def ripemd160(self, x):
        d = new('ripemd160')
        d.update(x)
        return d

    def seek(self):
        while True:
            t = time()
            for i in range(5000):
                key = f'{randint(self.start, self.end):x}'
                key = '0'*(64-len(key)) + key
                priv_key = bytes.fromhex(key)
                fullkey1 = hexlify(priv_key).decode()
                fullkey = '80' + hexlify(priv_key).decode() +'01'
                sha256a = sha256(unhexlify(fullkey)).hexdigest()
                sha256b = sha256(unhexlify(sha256a)).hexdigest()
                WIF = b58encode(unhexlify(fullkey+sha256b[:8]))
                sk = SigningKey.from_string(priv_key, curve=SECP256k1)
                vk = sk.get_verifying_key()
                key_bytes = hexlify(vk.to_string()).decode()
                key = ('0x' + hexlify(sk.verifying_key.to_string()).decode('utf-8'))
                half_len = len(key_bytes) // 2
                key_half = key_bytes[:half_len]
                last_byte = int(key[-1], 16)
                bitcoin_byte = '02' if last_byte % 2 == 0 else '03'
                publ_key = bitcoin_byte + key_half
                hash160 = self.ripemd160(sha256(unhexlify(publ_key)).digest()).digest()
                publ_addr_a = b"\x00" + hash160
                checksum = sha256(sha256(publ_addr_a).digest()).digest()[:4]
                publ_addr_b = b58encode(publ_addr_a + checksum)
                priv = WIF.decode()
                pub = publ_addr_b.decode()
                if pub == self.address:
                    open('found.txt', 'a').write(f'{priv} {pub}\n')
                    self.found = True
            self.count += 5000
            print(f'{self.RED if not self.found else self.GREEN}[+] Checked : {self.count}{self.DEFAULT}\tReward : {self.reward:.02f} BTC\tSpeed : {5000 * (1/(time()-t)):.02f}/Second')

if __name__ == '__main__':
    Puzzle()