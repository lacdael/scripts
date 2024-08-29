#!/usr/bin/python

import socket
import h2.connection
import h2.events
import traceback

port = 8082

def send_request(connection):
    # Send a simple GET request
    headers = [
        (':method', 'GET'),
        (':path', '/'),
        (':scheme','http'),
        (':authority', 'localhost:'+str(port)),
        #('user-agent', 'h2-client/1.0'),
    ]

    stream_id = connection.get_next_available_stream_id()
    connection.send_headers(stream_id, headers, end_stream=True)

def receive_response(connection, response_data):
    while True:
        events = connection.receive_data( response_data )
        for event in events:
            if isinstance(event, h2.events.ResponseReceived):
                print("Received response headers:")
                for name, value in event.headers:
                    print(f"{name}: {value}")
            elif isinstance(event, h2.events.DataReceived):
                print("Received response data:", event.data.decode('utf-8'))
            elif isinstance(event, h2.events.StreamEnded):
                print("STREAM END");
                break
            else:
                print(event);

def main():
    client_socket = socket.create_connection(('127.0.0.1', port))
    
    config = h2.config.H2Configuration(client_side=True, header_encoding='utf-8')
    conn = h2.connection.H2Connection(config=config)
    conn.initiate_connection()

    # Simulate sending the client preface
    #?????
    #client_socket.sendall(conn.data_to_send())
    try:
        while True:
            send( client_socket, conn );
            input("press any key to continue...");
    except:
        traceback.print_exc();
    finally:
        client_socket.close()

def send( client_socket, conn ):
    # Send a GET request
    send_request(conn)
    data_to_send = conn.data_to_send()
    if data_to_send:
        print(f'TOSEND: { data_to_send.hex()  }');
    client_socket.sendall( data_to_send )

    # Receive and handle the response
    
    loop = True;
    try:
        while loop:
            response_data = client_socket.recv(65535)
            events = conn.receive_data( response_data )
            for event in events:
                if isinstance(event, h2.events.ResponseReceived):
                    print("Received response headers:")
                    for name, value in event.headers:
                        print(f"\t{name}: {value}")
                elif isinstance(event, h2.events.DataReceived):
                    print(f"DATA: {event.data.decode('utf-8')}\t0x{event.data.hex()}")
                elif isinstance(event, h2.events.StreamEnded):
                    print("\t\t--STREAM END--");
                    loop = False;
                    break
                elif isinstance(event, h2.events.StreamEnded):
                    break;
                else:
                    pass
                    #print(event);
            
            #simulate sending any outstanding data 
            data_to_send = conn.data_to_send()
            if data_to_send:
                print(f'TOSEND: { data_to_send.hex()  }');
            client_socket.sendall( data_to_send )
    except:
        traceback.print_exc();


if __name__ == '__main__':
    main()








