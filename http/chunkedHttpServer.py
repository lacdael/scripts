#!/usr/bin/python

import socket
import time
import traceback

content = "Hello World";

def createChuncked( rspBody , chunkSize =5 ):
	chunks = [ rspBody [ i: i + chunkSize ] for i in range(0,len(rspBody) , chunkSize) ]  
	return chunks;

def sendRsp( clientSock ):
    chunkedRsp = createChuncked( content ); 
    rsp = f"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n"
    clientSock.send(rsp.encode("utf-8"));
    for i in range(0,len(chunkedRsp)):
        chunk = chunkedRsp[i];
        chunkLength = f"{len(chunk):x}";
        aChunk = f"{chunkLength}\r\n{chunk}\r\n";
        print(f"\ta chunk: {aChunk}");
        clientSock.send(aChunk.encode("utf-8"));
        time.sleep(1);
    clientSock.send("0\r\n\r\n".encode("utf-8"));
    clientSock.close();

def run():
    host="localhost"
    port=8084
    server_socket = None;
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host,port));
        server_socket.listen(1);
        while True:
            clientSock, clientAddr = server_socket.accept();
            reqData = clientSock.recv(1024).decode("utf-8");
            sendRsp( clientSock );
    except:
        traceback.print_exc();
    finally:
        if server_socket:
            server_socket.close();

if __name__ == "__main__":
	run();
