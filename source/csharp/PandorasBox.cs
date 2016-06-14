/* Pandoras Box Automation - {{ lang }} v{{ version }} @{{ time }} <support@coolux.de> */

using System;
using System.Collections.Generic;
using System.Text;
using System.Net.Sockets;


namespace PandorasBox
{
    /// <summary>
    /// The main class used to communicate with Pandoras Box
    /// </summary>
    public class PBAuto
    {
        private Connector c;

        public PBAuto(Connector connector)
        {
            c = connector;
        }

        public static PBAuto ConnectTcp(string ip, int domain = 0)
        {
            return new PBAuto(new TCP(ip, domain));
        }

        public struct PBAutoResult {
            public bool ok { get { return error == 0; } }
            public short code; public int error;
        }
{% for c in commands %}

        {% if c.recv|count > 0 %}public struct {{ c.name|camelize }}Result
        {
            public bool ok { get { return error == 0; } }
            public short code; public int error;{% for r in c.recv %}
            public {{types[r.type_id].name|no_suffix }}{% if types[r.type_id].name|is_buffer %}[]{%endif%} {{ r.name|camelize_small }};{% endfor %}
        }
        {% endif %}public {% if c.recv|count > 0 %}{{ c.name|camelize }}Result{%else%}PBAutoResult{%endif%} {{ c.name|camelize }}({% for a in c.send %}{% if not loop.first %}, {% endif %}{{ types[a.type_id].name|no_suffix }}{% if types[a.type_id].name|is_buffer %}[]{%endif%} {{ a.name|camelize_small }}{% endfor %})
        {
            var b = new ByteUtil();
            b.writeShort({{ c.code }});{% for a in c.send %}
            b.write{{ types[a.type_id].name|camelize }}({{ a.name|camelize_small }});{% endfor %}
            {% if c.recv|count > 0 %}b = c.Send(b, true);
            var r = new {{ c.name|camelize }}Result();
            r.code = b.readShort();
            if(r.code != {{ c.code }})
            {
            	r.code = -1;
            	r.error = 7; // WrongMessageReturned
            	return r;
            }
            if(r.code < 0) r.error = b.readInt(); else
            {
                r.error = 0;{% for r in c.recv %}
                r.{{ r.name|camelize_small }} = b.read{{ types[r.type_id].name|camelize }}();{% endfor %}
            }
            return r;{% else %}b = c.Send(b, false);return new PBAutoResult(){ code = {{c.code}},error = 0 };{% endif %}
        }{% endfor %}
    }

    /// <summary>
    /// Contains extension methods for conversion between native format and byte arrays
    /// </summary>
    public static class PBUtil
    {
        public static byte PBAutoChecksum(this byte[] message)
        {
            if (message.Length < 17) throw new ArgumentException("Byte array is not a PBAuto header! Length != 17");
            var checksum = 0;
            for(int i=4;i<16;i++)
            {
                checksum += message[i];
            }
            return (byte)(checksum % 255);
        }
        public static long GetInt64(this byte[] bytes, int offset = 0)
        {
            byte[] value_bytes = new byte[8];
            Array.Copy(bytes, offset, value_bytes, 0, 8);
            if (BitConverter.IsLittleEndian) { Array.Reverse(value_bytes); }
            return BitConverter.ToInt64(value_bytes, 0);
        }

        public static int GetInt32(this byte[] bytes, int offset = 0)
        {
            byte[] value_bytes = new byte[4];
            Array.Copy(bytes, offset, value_bytes, 0, 4);
            if (BitConverter.IsLittleEndian) { Array.Reverse(value_bytes); }
            return BitConverter.ToInt32(value_bytes, 0);
        }

        public static short GetInt16(this byte[] bytes, int offset = 0)
        {
            byte[] value_bytes = new byte[2];
            Array.Copy(bytes, offset, value_bytes, 0, 2);
            if (BitConverter.IsLittleEndian) { Array.Reverse(value_bytes); }
            return BitConverter.ToInt16(value_bytes, 0);
        }

        public static byte[] GetBytesNetworkOrder(this Int64 value)
        {
            var bytes = BitConverter.GetBytes(value);
            if (BitConverter.IsLittleEndian) { Array.Reverse(bytes); }
            return bytes;
        }
        public static byte[] GetBytesNetworkOrder(this int value)
        {
            var bytes = BitConverter.GetBytes(value);
            if (BitConverter.IsLittleEndian) { Array.Reverse(bytes); }
            return bytes;
        }

        public static byte[] GetBytesNetworkOrder(this short value)
        {
            var bytes = BitConverter.GetBytes(value);
            if (BitConverter.IsLittleEndian) { Array.Reverse(bytes); }
            return bytes;
        }
    }

    /// <summary>
    /// Utility class for byte conversion
    /// </summary>
    public class ByteUtil
    {
        // Holds the bytes
        private List<byte> list_bytes;
        private byte[] read_bytes;
        
        // Position for reading
        private int position = 0;

        // Constructors
        public ByteUtil()
        {
            list_bytes = new List<byte>();
        }
        public ByteUtil(byte[] data)
        {
            read_bytes = data;
        }

        public void CopyTo(byte[] bytes, int offset) { list_bytes.CopyTo(bytes, offset); }
        public int Length { get { return list_bytes.Count; } }

        // Writing
        public void writeBool(bool value) { list_bytes.Add((byte)(value ? 1 : 0)); }
        public void writeByte(byte value) { list_bytes.Add(value); }
        public void writeShort(short value) { list_bytes.AddRange(value.GetBytesNetworkOrder() ); }
        public void writeInt(int value) { list_bytes.AddRange(value.GetBytesNetworkOrder()); }
        public void writeInt64(long value) { list_bytes.AddRange(value.GetBytesNetworkOrder()); }
        public void writeDouble(double value) { list_bytes.AddRange(BitConverter.GetBytes(value)); }
        public void writeStringNarrow(string value) { writeShort((short)value.Length); list_bytes.AddRange(Encoding.UTF8.GetBytes(value)); }
        public void writeStringWide(string value) { writeShort((short)value.Length); list_bytes.AddRange(Encoding.BigEndianUnicode.GetBytes(value)); }
        public void writeByteBuffer(byte[] value) { writeInt(value.Length); list_bytes.AddRange(value); }
        public void writeIntBuffer(int[] value) { writeInt(value.Length); foreach (var i in value) { list_bytes.AddRange(i.GetBytesNetworkOrder()); } }

        // Reading
        private byte[] _readBlock(int length) { var ret = new byte[length]; Array.Copy(read_bytes, position, ret, 0, length);position += length;return ret; }
        public bool readBool() { var result = read_bytes[position];position++;return result == 1; }
        public byte readByte() { var result = read_bytes[position];position++;return result; }
        public short readShort() { return _readBlock(2).GetInt16(); }
        public int readInt() { return _readBlock(4).GetInt32(); }
        public long readInt64() { return _readBlock(8).GetInt64(); }
        public double readDouble() { return BitConverter.ToDouble(_readBlock(8), 0); }
        public string readStringNarrow() { int length = readShort(); return Encoding.UTF8.GetString(_readBlock(length)); }
        public string readStringWide() { int length = readShort(); return Encoding.BigEndianUnicode.GetString(_readBlock(length)); }
        public byte[] readByteBuffer() { int length = readInt(); return _readBlock(length); }
        public int[] readIntBuffer() { int length = readInt(); int[] result = new int[length]; for (int i = 0;i < length; i++) { result[i] = _readBlock(4).GetInt32(); }; return result; }
    }

    /// <summary>
    /// Interface that allows PBAuto to transmit messages
    /// </summary>
    public interface Connector
    {
        ByteUtil Send(ByteUtil data, bool has_reponse);
    }

    /// <summary>
    /// Implements the Connector interface using TCP as the underlying protocol
    /// </summary>
    public class TCP : Connector
    {
        private string ip;
        private int domain;
        private TcpClient client;
        private const int PORT = 6211;

        public TCP(string ip, int domain = 0)
        {
            this.ip = ip;
            this.domain = domain;
            client = new TcpClient();
            client.NoDelay = true;
            client.Connect(System.Net.IPAddress.Parse(ip), PORT);
        }

        public ByteUtil Send(ByteUtil data, bool has_response)
        {
            byte[] header = new byte[17] {
                (byte)'P', (byte)'B', (byte)'A', (byte)'U', //# header consists of magic "PBAU" sequence
                1,                                          //# + protocol version (byte, currently 1)
                0, 0, 0, 0,                                 //# + domain id (integer)
                0, 0,                                       //# + message size (short)
                0, 0, 0, 0,                                 //# + connection id (int, user definable, defaults to 0)
                0,                                          //# + protocol flag (byte, 0 for TCP)
                0,                                          //# + checksum
            };

            // write domain id to header
            domain.GetBytesNetworkOrder().CopyTo(header, 5);
            // write message length
            ((short)data.Length).GetBytesNetworkOrder().CopyTo(header, 9);
            // calculate checksum and write
            header[16] = header.PBAutoChecksum();

            var message = new byte[17 + data.Length];
            header.CopyTo(message, 0);
            data.CopyTo(message, 17);

            var stream = client.GetStream();
            stream.Write(message, 0, message.Length);
            stream.Flush();

            if( !has_response )
            {
                return null;
            }

            int bytesread = 0;
            while(bytesread < 17)
            {
                bytesread += stream.Read(header, bytesread, 17 - bytesread);
            }

            if(header[0] != 0x50 || header[1] != 0x42 || header[2] != 0x41 || header[3] != 0x55 || header.PBAutoChecksum() != header[16])
            {
                // Not a PB Header or checksum fail
                return null;
            }

            int message_length = header.GetInt16(9);
            message = new byte[message_length];

            bytesread = 0;
            while (bytesread < message_length)
            {
                bytesread += stream.Read(message, bytesread, message_length - bytesread);
            }

            return new ByteUtil(message);
        }
    }
}
