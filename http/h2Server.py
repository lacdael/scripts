#!/usr/bin/python

import socket
import h2.config
import h2.connection
import h2.events
import traceback
import threading

port = 8082

def handle_request( event, connection ):
    #print( "handle_request");
    #print( event );
    if isinstance( event, h2.events.RemoteSettingsChanged):
        return
    
    stream_id = event.stream_id;
    headers = [ (name,value) for (name,value) in event.headers];
    response_headers= [
        (':status','200'),
        ('Content-type','text/plain')]
    

    b = bytearray();
    for i in range(1000):
        for j in range(10):
            b.append( 30 + j );
    
    response_data = bytes( b );
    #response_data = b'Hello World';
    connection.send_headers(stream_id, response_headers);
    if len( response_data ) > 16:
        #split into chunks
        chunkSize = 5;
        for i in range(0, len(response_data), chunkSize):
            connection.send_data( stream_id, response_data[i:i+chunkSize]);

        connection.end_stream( stream_id );
    else:
        connection.send_data(stream_id,response_data,end_stream=True);


def handle_client( client_socket ):
    try:
        config = h2.config.H2Configuration(
                client_side=False,
                header_encoding='utf-8',);
        conn = h2.connection.H2Connection(config=config);

        while True:
            data = client_socket.recv( 65535 );
            events = conn.receive_data( data );
            for event in events:
                if isinstance(event, h2.events.RequestReceived):
                    handle_request( event, conn );
                elif isinstance(event, h2.events.DataReceived):
                    handle_request( event, conn );
                elif isinstance(event, h2.events.StreamEnded):
                    print("\t\t--STREAM END--");
                    break;

            outgoing_data = conn.data_to_send();
            if outgoing_data:    
                print(f'TOSEND: { outgoing_data.hex() }');

            client_socket.sendall(outgoing_data);
    except:
        traceback.print_exc()

def main():
    try:
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
        server_socket.bind(('127.0.0.1',port))
        server_socket.listen(5)
        
        while True:
            client_socket, _ = server_socket.accept();
            client_thread = threading.Thread(target=handle_client,args=(client_socket,));
            client_thread.start();
    except:
        traceback.print_exc()
    finally:
        server_socket.close();
        
if __name__ == '__main__':
    main()

