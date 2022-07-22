import base64, json
from Crypto.Cipher    import PKCS1_OAEP
from Crypto.Hash      import SHA256
from Crypto.PublicKey import RSA


import aiohttp


class DiscordUser:
    def __init__(self, **values):
        self.id = values.get('id')
        self.username = values.get('username')
        self.discrim = values.get('discrim')
        self.avatar_hash = values.get('avatar_hash')
        self.token = values.get('token')

    @classmethod
    def from_payload(cls, payload):
        values = payload.split(':')

        return cls(id=values[0],
                   discrim=values[1],
                   avatar_hash=values[2],
                   username=values[3])



class DRAClient:
    def __init__(self, on_connected=None, on_finish=None, on_scan=None, on_close=None):
        self.ws = None
        self.key = RSA.generate(2048)
        self.cipher = PKCS1_OAEP.new((self.key), hashAlgo=SHA256)
        
        self.token = None
        self.fingerprint = None
        
        self.on_connected = on_connected
        self.on_scan = on_scan
        self.on_finish = on_finish
        self.on_close = on_close     

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            self.ws = await session.ws_connect('wss://remote-auth-gateway.discord.gg/?v=1', headers={'Origin': 'https://discord.com'}, heartbeat=0.5)
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.handle_message(msg.data)
                else:
                    print(msg)
        
    def decrypt_payload(self, encrypted_payload):
        payload = base64.b64decode(encrypted_payload)
        decrypted = self.cipher.decrypt(payload)
        return decrypted

    @property
    def public_key(self):
        pub_key = self.key.publickey().export_key().decode('utf-8')
        pub_key = ''.join(pub_key.split('\n')[1:-1])
        return pub_key

    async def send(self, op, data=None):
        payload = {'op': op}
        if data is not None:
            (payload.update)(**data)
        
        data2 = json.dumps(payload)
        await self.ws.send_str(data2)


    async def handle_message(self, msg):
        data = json.loads(msg)
        op = data.get('op')

        #INITIALISING CONNECTION 
        if op == 'hello':
            self.ws._heartbeat = data.get('heartbeat_interval') / 1000
            await self.send('init', {'encoded_public_key': self.public_key})
            
        #VALIDATING REQUEST
        elif op == 'nonce_proof':
            nonce = data.get('encrypted_nonce')
            decrypted_nonce = self.decrypt_payload(nonce)
            proof = SHA256.new(data=decrypted_nonce).digest()
            proof = base64.urlsafe_b64encode(proof)
            proof = proof.decode().rstrip('=')
            await self.send('nonce_proof', {'proof': proof})
            
        #CONNECTED TO DISCORD
        elif op == 'pending_remote_init':
            self.fingerprint = data.get('fingerprint')
            await self.on_connected()
            
        #USER SCANNED QR CODE
        elif op == 'pending_finish':
            encrypted_payload = data.get('encrypted_user_payload')
            payload = self.decrypt_payload(encrypted_payload)
            self.user = DiscordUser.from_payload(payload.decode())
            await self.on_scan()
            
        #USER SUBMITTED
        elif op == 'finish':
            encrypted_token = data.get('encrypted_token')
            token = self.decrypt_payload(encrypted_token)
            self.token = token.decode()
            await self.on_finish()
        
        elif op == 'cancel':
            await self.on_close()
     
            

