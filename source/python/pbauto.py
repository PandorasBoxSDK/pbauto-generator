import socket
import struct

# Pandoras Box Automation
# {{ lang }} v{{ version }} @{{ time }} <support@coolux.de>

{% for et in enums %}
class {{et.name|camelize}}:
{% for e in et['values'] %}    {{ e.key|camelize }} = {{ e.val }}
{% endfor %}{% endfor %}

class PBAuto:
    @staticmethod
    def connect_tcp(ip="", domain=0):
        return PBAuto(Tcp(ip, domain))

    @staticmethod
    def offline_tcp(domain=0, callback=print, data_format='hex'):
        return PBAuto(OfflineTcp(domain, callback, data_format))

    def __init__(self, connector):
        if not issubclass(type(connector), Connector):
            raise TypeError('Expected Connector')
        self.__c = connector
{% for c in commands %}
    def {{ c.name|underscore }}(self{% for a in c.send %}, {{a.name|underscore}}{% endfor %}):
        b = ByteUtil()
        b.write_short({{ c.code }}){% for a in c.send %}
        b.write_{{ types[a.type_id].name|underscore }}({{ a.name|underscore }}){% endfor %}
        {% if c.recv|count > 0 %}r = self.__c.send(b, True)
        if not r: return {'ok': False, 'code': -1}
        c = r.read_short()
        if c < 0: return {'ok': False, 'code': c, 'error': r.read_int()}
        d = {'ok': True, 'code': c}{% for r in c.recv %}
        d['{{ r.name }}'] = r.read_{{ types[r.type_id].name|underscore }}(){% endfor %}
        return d{% else %}self.__c.send(b, False)
        return {'ok': True}{% endif %}
{% endfor %}


class Connector(object):
    pass


class OfflineTcp(Connector):
    def __init__(self, domain=0, callback=print, data_format='hex'):
        self.domain, self.callback, self.data_format = domain, callback, data_format

    def format(self, data):
        if self.data_format == 'hex':
            return ''.join('{:02x}'.format(x) for x in data)
        elif self.data_format == 'cpp':
            return "{" + ', '.join('0x{:02x}'.format(x) for x in data) + "}"
        elif self.data_format == 'wd':
            return ''.join('[h{:02x}]'.format(x) for x in data)
        elif self.data_format == 'pb':
            return ' '.join('{:02x}'.format(x) for x in data)
        else:
            raise Exception("Not a format: '%s'" % self.data_format)

    def send(self, data, wait_for_response):
        header = struct.pack("!BlhlB", 1, self.domain, len(data), 0, 0)
        checksum = struct.pack("!B", sum(bytearray(header)) % 255)
        data = b'PBAU' + header + checksum + bytes(data)
        self.callback(self.format(data))


class Tcp(Connector):
    PORT = 6211

    def __init__(self, ip, domain=0):
        self.__ip, self.domain = ip, domain
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # TODO # improve connection handling
        self.__sock.connect((self.__ip, self.PORT))

    def send(self, data, wait_for_response):
        # header consists of magic "PBAU" sequence
        # + protocol version (byte, currently 1)
        # + domain id (integer)
        # + message size (short)
        # + connection id (int, user definable, defaults to 0)
        # + protocol flag (byte, 0 for TCP)
        # + checksum (byte)

        header = struct.pack("!BlhlB", 1, self.domain, len(data), 0, 0)

        checksum = struct.pack("!B", sum(bytearray(header)) % 255)
        self.__sock.sendall(b'PBAU' + header + checksum + bytes(data))

        if wait_for_response:
            # receive only header (17 bytes)
            # TODO # WARNING: This does not take into account
            # TODO # cases where socket.recv returns less than 16
            # TODO # in practice this will never happen though.
            header = self.__sock.recv(17)

            # check for magic bytes...
            if header[0:4] == b'PBAU':
                # ...then parse the rest
                header_parsed = struct.unpack("!4sBlhlBB", header)
                response_length = header_parsed[3]

                return ByteUtil(self.__sock.recv(response_length))

        # if not wait_for_response OR invalid response:
        return ByteUtil()


class ByteUtil:
    def __init__(self, data=None):
        self.__data = data or bytearray()
        self.__pos = 0

    def write_bool(self, val):
        self.__data.extend(struct.pack('!B', val))

    def write_short(self, val):
        self.__data.extend(struct.pack('!h', val))

    def write_int(self, val):
        self.__data.extend(struct.pack('!l', val))

    def write_int64(self, val):
        self.__data.extend(struct.pack('!q', val))

    def write_double(self, val):
        self.__data.extend(struct.pack('d', val))

    def write_string_narrow(self, val):
        self.__data.extend(struct.pack('!h', len(val)))
        self.__data.extend(struct.pack("!%is" % len(val), val.encode("ASCII")))

    def write_string_wide(self, val):
        self.__data.extend(struct.pack('!h', len(val)))
        self.__data.extend(struct.pack("!%is" % len(val), val.encode("UTF-16-BE")))

    def write_byte_buffer(self, val):
        self.__data.extend(struct.pack('!l', len(val)))
        self.__data.extend(struct.pack("!%is" % len(val), val))

    def write_int_buffer(self, val):
        self.__data.extend(struct.pack('!l', len(val)))
        self.__data.extend(struct.pack("!%il" % len(val), val))

    def read_bool(self):
        return self._read_block(1)[0] == 1

    def read_byte(self):
        return self._read_block(1)[0]

    def read_short(self):
        return struct.unpack("!h", self._read_block(2))[0]

    def read_int(self):
        return struct.unpack("!l", self._read_block(4))[0]

    def read_int64(self):
        return struct.unpack("!q", self._read_block(8))[0]

    def read_double(self):
        return struct.unpack("d", self._read_block(8))[0]

    def read_string_narrow(self):
        length = self.readShort()
        return self._read_block(length).decode("ASCII")

    def read_string_wide(self):
        length = self.readShort()
        return self._read_block(length * 2).decode("UTF-16-BE")

    def read_byte_buffer(self):
        length = self.readInt()
        return self._read_block(length)

    def _read_block(self, count):
        self.__pos += count
        if self.__pos > len(self.__data):
            raise IndexError
        return self.__data[self.__pos - count: self.__pos]

    def __bool__(self):
        return not len(self.__data) == 0

    def __len__(self):
        return len(self.__data)

    # Python 2 hooray
    def __str__(self):
        return str(self.__data)

    def __bytes__(self):
        return bytes(self.__data)
