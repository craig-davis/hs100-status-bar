import base64
import json
import rumps
import socket
import struct
import sys
import threading
import Queue
from netaddr import *

# Rumps status bar app
class AcControlStatusBarApp(rumps.App):
    def __init__(self):
        super(AcControlStatusBarApp, self).__init__("HS100 Control", title=None, icon="icon.png")

        self.apis = {}

        menuitems = []
        for ip in Helpers.discover():
            print "Discovered ", ip
            api = Hs100Api(ip)
            response = api.query()

            if response:
                info = response['system']['get_sysinfo']
                alias = info['alias']
                state = info['relay_state']
            else:
                alias = ip
                state = -1

            self.apis[alias] = api

            menuitem = rumps.MenuItem(alias, callback=self.onoff)
            menuitem.state = state
            menuitems.append(menuitem)

        self.menu = menuitems

    def onoff(self, sender):
        sender.state = not sender.state
        command = 'on' if sender.state else 'off'
        api = self.apis[sender.title]
        getattr(api, command)()

# Simple HS100 Api
# Based on https://github.com/j05h/hs100
class Hs100Api():
    # base64 encoded data to send to the plug to switch it on
    payload_on = "AAAAKtDygfiL/5r31e+UtsWg1Iv5nPCR6LfEsNGlwOLYo4HyhueT9tTu36Lfog=="

    # base64 encoded data to send to the plug to switch it off
    payload_off = "AAAAKtDygfiL/5r31e+UtsWg1Iv5nPCR6LfEsNGlwOLYo4HyhueT9tTu3qPeow=="

    # base64 encoded data to send to the plug to query it
    payload_query = "AAAAI9Dw0qHYq9+61/XPtJS20bTAn+yV5o/hh+jK8J7rh+vLtpbr"

    # base64 encoded data to query emeter - hs100 doesn't seem to support this in hardware, but the API seems to be there...
    payload_emeter = "AAAAJNDw0rfav8uu3P7Ev5+92r/LlOaD4o76k/6buYPtmPSYuMXlmA=="

    def __init__(self, ip, port = 9999):
        print "Setting ip and port ", ip , port
        self.ip   = ip
        self.port = port

    def __getattr__(self, command):
        methods = {
            'on':    lambda: self.send(self.payload_on),
            'off':   lambda: self.send(self.payload_off),
            'query': lambda: self.send(self.payload_query),
            'meter': lambda: self.send(self.payload_emeter)
        }

        return methods.get(command)

    def recv_size(self, the_socket):
        # data length is packed into 4 bytes
        total_len  = 0;
        total_data = [];
        size       = sys.maxint
        size_data  = '';
        sock_data  = '';
        recv_size  = 8192
        while total_len < size:
            sock_data = the_socket.recv(recv_size)
            if not total_data:
                if len(sock_data) > 4:
                    size_data += sock_data
                    size = struct.unpack('>i', size_data[:4])[0]
                    recv_size = size
                    if recv_size > 524288 : recv_size = 524288
                    total_data.append(size_data[4:])
                else:
                    size_data += sock_data
            else:
                total_data.append(sock_data)
            total_len = sum([len(i) for i in total_data ])

        return ''.join(total_data)

    def send(self, payload):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
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

class Helpers():
    @staticmethod
    def find(q, ip, port):
        result = Helpers.check_port(ip, port)

        if result:
            q.put(result)

    @staticmethod
    def discover():
        ipset = IPSet([Helpers.my_ip() + '/24'])

        print("Discovering devices on {0}".format(ipset))

        q = Queue.Queue()

        threads = []
        for ip in list(ipset):
            t = threading.Thread(target=Helpers.find, args=(q, str(ip), 9999))
            t.daemon = True
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        ips = []
        while not q.empty():
            ips.append(q.get())

        return ips

    @staticmethod
    def check_port(host, port):
        captive_dns_addr = ""
        host_addr = ""
        try:
            captive_dns_addr = socket.gethostbyname("BlahThisDomaynDontExist22.com")
        except:
            pass
        try:
            host_addr = socket.gethostbyname(host)
            if (captive_dns_addr == host_addr):
                return False
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((host, port))
            s.close()
        except:
            return False
        return host

    @staticmethod
    def my_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        myip = (s.getsockname()[0])
        s.close()

        return myip

if __name__ == "__main__":
    AcControlStatusBarApp().run()
