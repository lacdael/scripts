# Wireshark

`tshark -Y "! icmp" -x`
- -x : hex display
- -Y "! icmp" : filter out network management messages

`ping -c 1 localhost`

! note: wireshark does not show the preamble of an ethernet packet, here, 0x0000 replaces the preamble.

       0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000  00 00 03 04 00 06 00 00 00 00 00 00 00 00 86 dd   ................
0010  60 0b 2c 61 00 40 3a 40 00 00 00 00 00 00 00 00   `.,a.@:@........
0020  00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00   ................
0030  00 00 00 00 00 00 00 01 80 00 fd 90 75 52 00 01   ............uR..
0040  ea 1a 69 65 00 00 00 00 ed 4b 0d 00 00 00 00 00   ..ie.....K......
0050  10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f   ................
0060  20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f    !"#$%&'()*+,-./
0070  30 31 32 33 34 35 36 37                           01234567

    Ethernet Frame Header (Bytes 0-13):
        Bytes 0-5: Destination MAC Address
        Bytes 6-11: Source MAC Address
        Bytes 12-13: Ethernet Type (0x86DD indicates IPv6)

    IPv6 Header (Bytes 14-39):
        Bytes 14-15: Version and Traffic Class
        Bytes 16-17: Flow Label
        Bytes 18-21: Payload Length
        Bytes 22: Next Header (0x3A indicates ICMPv6)
        Bytes 23: Hop Limit
        Bytes 24-39: Source and Destination IPv6 Addresses

# HTTP2

HTTP/2 is considered a binary protocol due to its binary framing layer. In HTTP/2, communication is structured in frames, and these frames are binary-encoded.

Here are some aspects of HTTP/2 that contribute to its classification as a binary protocol:

- HTTP/2 frames have a binary format instead of the plain text format used in HTTP/1.1. This binary encoding reduces the overhead of textual representation, making the protocol more efficient in terms of both parsing and transmission.
- HTTP/2 employs header compression using the HPACK algorithm, which compresses headers before they are transmitted. This compression is performed on the binary-encoded headers, resulting in more compact representations compared to the text-based headers in HTTP/1.1.
- HTTP/2 allows for multiple concurrent streams within a single connection. Each stream is divided into frames, and these frames are binary-encoded. This multiplexing of streams allows for more efficient use of the connection and reduces latency.
- HTTP/2 introduces stream dependencies, prioritization and flow Control.

# HTTP/1.1

```
while : ; do ( echo -ne "HTTP/1.1 200 OK\r\nContent-Length: $(wc -c <<< "Hello World")\r\n\r\n" ; cat <<< "Hello World"; ) | nc -l -p 8080 ; done
```

`curl localhost:8080`

       0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000  00 00 03 04 00 06 00 00 00 00 00 00 00 00 08 00   ................
0010  45 00 00 82 36 de 40 00 40 06 05 96 7f 00 00 01   E...6.@.@.......
0020  7f 00 00 01 c0 ca 1f 90 a2 07 ed 95 8c 2a 9f 2c   .............*.,
0030  80 18 02 00 fe 76 00 00 01 01 08 0a d4 90 77 b5   .....v........w.
0040  d4 90 77 b5 47 45 54 20 2f 20 48 54 54 50 2f 31   ..w.GET / HTTP/1
0050  2e 31 0d 0a 48 6f 73 74 3a 20 6c 6f 63 61 6c 68   .1..Host: localh
0060  6f 73 74 3a 38 30 38 30 0d 0a 55 73 65 72 2d 41   ost:8080..User-A
0070  67 65 6e 74 3a 20 63 75 72 6c 2f 37 2e 38 38 2e   gent: curl/7.88.
0080  31 0d 0a 41 63 63 65 70 74 3a 20 2a 2f 2a 0d 0a   1..Accept: */*..
0090  0d 0a                                             ..

       0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000  00 00 03 04 00 06 00 00 00 00 00 00 00 00 08 00   ................
0010  45 00 00 66 45 29 40 00 40 06 f7 66 7f 00 00 01   E..fE)@.@..f....
0020  7f 00 00 01 1f 90 c0 ca 8c 2a 9f 2c a2 07 ed e3   .........*.,....
0030  80 18 02 00 fe 5a 00 00 01 01 08 0a d4 90 77 b5   .....Z........w.
0040  d4 90 77 b5 48 54 54 50 2f 31 2e 31 20 32 30 30   ..w.HTTP/1.1 200
0050  20 4f 4b 0d 0a 43 6f 6e 74 65 6e 74 2d 4c 65 6e    OK..Content-Len
0060  67 74 68 3a 20 31 32 0d 0a 0d 0a 68 65 6c 6c 6f   gth: 12....hello
0070  20 57 6f 72 6c 64 

# HTTP/2

Using the hyper library for python to serve and request data.

```
       0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000  00 00 03 04 00 06 00 00 00 00 00 00 00 00 08 00   ................
0010  45 00 00 97 c3 fe 40 00 40 06 78 60 7f 00 00 01   E.....@.@.x`....
0020  7f 00 00 01 eb 3c 1f 92 a6 56 ec ce be 75 a3 24   .....<...V...u.$
0030  80 18 02 00 fe 8b 00 00 01 01 08 0a d4 88 53 a1   ..............S.
0040  d4 88 53 a1 50 52 49 20 2a 20 48 54 54 50 2f 32   ..S.PRI * HTTP/2
0050  2e 30 0d 0a 0d 0a 53 4d 0d 0a 0d 0a 00 00 2a 04   .0....SM......*.
0060  00 00 00 00 00 00 01 00 00 10 00 00 02 00 00 00   ................
0070  01 00 04 00 00 ff ff 00 05 00 00 40 00 00 08 00   ...........@....
0080  00 00 00 00 03 00 00 00 64 00 06 00 01 00 00 00   ........d.......
0090  00 0f 01 05 00 00 00 01 82 84 86 41 8a a0 e4 1d   ...........A....
00a0  13 9d 09 b8 f0 1e 17                              .......

       0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000  00 00 03 04 00 06 00 00 00 00 00 00 00 00 08 00   ................
0010  45 00 00 64 02 85 40 00 40 06 3a 0d 7f 00 00 01   E..d..@.@.:.....
0020  7f 00 00 01 1f 92 eb 3c be 75 a3 24 a6 56 ed 31   .......<.u.$.V.1
0030  80 18 02 00 fe 58 00 00 01 01 08 0a d4 88 53 a2   .....X........S.
0040  d4 88 53 a1 00 00 00 04 01 00 00 00 00 00 00 0a   ..S.............
0050  01 04 00 00 00 01 88 5f 87 49 7c a5 8a e8 19 aa   ......._.I|.....
0060  00 00 0b 00 01 00 00 00 01 48 65 6c 6c 6f 20 57   .........Hello W
0070  6f 72 6c 64
```

# HTTP1.1 Chunked

```
def sendRsp( clientSock, content ):
    chunks = createChuncked( content ); 
    rsp = f"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n"
    clientSock.send(rsp.encode("utf-8"));
    for i in range(0,len(chunks)):
        chunk = chunks[i];
        chunkLength = f"{len(chunk):x}";
        aChunk = f"{chunkLength}\r\n{chunk}\r\n";
        clientSock.send(aChunk.encode("utf-8"));
        time.sleep(1);
    clientSock.send("0\r\n\r\n".encode("utf-8"));
    clientSock.close();
```






