# coding=utf-8
import msgpack
import httplib


class Msfrpc:
    class MsfError(Exception):
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return repr(self.msg)

    class MsfAuthError(MsfError):
        def __init__(self, msg):
            self.msg = msg

    def __init__(self, opts=None):
        if opts is None:
            opts = []
        self.host = opts.get('host') or "127.0.0.1"
        self.port = opts.get('port') or 55552
        self.uri = opts.get('uri') or "/api/"
        self.ssl = opts.get('ssl') or False
        self.authenticated = False
        self.token = False
        self.headers = {"Content-type": "binary/message-pack"}
        if self.ssl:
            self.client = httplib.HTTPSConnection(self.host, self.port)
        else:
            self.client = httplib.HTTPConnection(self.host, self.port)

    def encode(self, data):
        return msgpack.packb(data)

    def decode(self, data):
        return msgpack.unpackb(data)

    def call(self, meth, opts=None):
        if opts is None:
            opts = []
        if meth != "auth.login":
            if not self.authenticated:
                raise self.MsfAuthError("MsfRPC: Not Authenticated")

        if meth != "auth.login":
            opts.insert(0, self.token)

        opts.insert(0, meth)
        params = self.encode(opts)
        self.client.request("POST", self.uri, params, self.headers)
        resp = self.client.getresponse()
        return self.decode(resp.read())

    def login(self, user, password):
        # {'token': 'TEMPYN2aoiaAwX2IMOLZAia0pGan1HJ2', 'result': 'success'}
        ret = self.call('auth.login', [user, password])
        if ret.get('result') == 'success':
            self.authenticated = True
            self.token = ret.get('token')
            return True
        else:
            raise self.MsfAuthError("MsfRPC: Authentication failed")


if __name__ == '__main__':
    # Create a new instance of the Msfrpc client with the default options
    client = Msfrpc({})

    # Login to the msfmsg server using the password "abc123"
    client.login('msf', '123456')

    # Get a list of the exploits from the server
    mod = client.call('module.exploits')
    print
    mod.keys()
    # Grab the first item from the modules value of the returned dict
    # print "Compatible payloads for : %s\n" % mod['modules'][0]

    # mod1 = client.call('console.create')
    # print mod1  # , mod1.keys()

    ret = client.call('console.write', ["11", "use exploit/windows/smb/ms08_067_netapi\n"])
    print
    ret

    ret = client.call('console.write', ["11", "set payload windows/meterpreter/reverse_tcp\n"])
    print
    ret

    ret = client.call('console.read', ["11"])
    result = ret["data"].split("\n")
    for i in result:
        print
        i

    ret = client.call('console.write', ["11", "show options\n"])
    print
    ret

    ret = client.call('console.read', ["11"])
    result = ret["data"].split("\n")
    for i in result:
        print
        i

    ret = client.call('plugin.loaded')
    print
    ret
    # for ids in client.call('console.list')["consoles"]:
    #     client.call('console.destroy', [ids["id"]])

    # # Get the list of compatible payloads for the first option
    # ret = client.call('module.compatible_payloads', [mod['modules'][0]])
    # for i in (ret.get('payloads')):
    #     print "\t%s" % i
