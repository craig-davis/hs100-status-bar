import base64
import json
import rumps
import socket
import struct
import sys
import time

class AcControlStatusBarApp(rumps.App):
    def __init__(self):
        super(AcControlStatusBarApp, self).__init__("AC Control", title=None, icon="icon.png")
        ac = rumps.MenuItem('Air Conditioner')
        self.menu = [ac]
        self.api = Hs100Api()
        response = self.api.request('query')
        ac.state = -1 if not response else response['system']['get_sysinfo']['relay_state']

    @rumps.clicked("Air Conditioner")
    def onoff(self, sender):
        sender.state = not sender.state
        command = 'on' if sender.state else 'off'
        self.api.request(command)

class Hs100Api():

    ip = '192.168.1.15'

    port = 9999

    # base64 encoded data to send to the plug to switch it on
    payload_on="AAAAKtDygfiL/5r31e+UtsWg1Iv5nPCR6LfEsNGlwOLYo4HyhueT9tTu36Lfog=="

    # base64 encoded data to send to the plug to switch it off
    payload_off="AAAAKtDygfiL/5r31e+UtsWg1Iv5nPCR6LfEsNGlwOLYo4HyhueT9tTu3qPeow=="

    # base64 encoded data to send to the plug to query it
    payload_query="AAAAI9Dw0qHYq9+61/XPtJS20bTAn+yV5o/hh+jK8J7rh+vLtpbr"

    # base64 encoded data to query emeter - hs100 doesn't seem to support this in hardware, but the API seems to be there...
    payload_emeter="AAAAJNDw0rfav8uu3P7Ev5+92r/LlOaD4o76k/6buYPtmPSYuMXlmA=="

    def recv_size(self, the_socket):
        #data length is packed into 4 bytes
        total_len=0;
        total_data=[];
        size=sys.maxint
        size_data=sock_data='';
        recv_size=8192
        while total_len<size:
            sock_data=the_socket.recv(recv_size)
            if not total_data:
                if len(sock_data)>4:
                    size_data+=sock_data
                    size=struct.unpack('>i', size_data[:4])[0]
                    recv_size=size
                    if recv_size>524288:recv_size=524288
                    total_data.append(size_data[4:])
                else:
                    size_data+=sock_data
            else:
                total_data.append(sock_data)
            total_len=sum([len(i) for i in total_data ])
        return ''.join(total_data)

    def send(self, payload):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))

        #input_num=`sendtoplug $ip $port "$payload"
        s.send(base64.b64decode(payload))
        data = self.recv_size(s)
        s.close()

        mapped = map(ord, data)

        code = 171
        response = ''
        for byte in mapped:
            output = byte ^ code
            response += chr(output)
            code=byte

        return json.loads(response)

    def request(self, command):
        functions = {
                'on':    lambda: self.send(self.payload_on),
                'off':   lambda: self.send(self.payload_off),
                'query': lambda: self.send(self.payload_query),
                'meter': lambda: self.send(self.payload_emeter)
        }

        function = functions.get(command)

        return function()

if __name__ == "__main__":
    AcControlStatusBarApp().run()
