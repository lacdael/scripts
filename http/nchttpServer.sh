#!/bin/bash

CONTENT="hello World"
SIZE=$(wc -c <<< $CONTENT);
while : ; do
	( echo -ne "HTTP/1.1 200 OK\r\nContent-Length: $SIZE\r\n\r\n$CONTENT"; ) | nc -l -p 8080 ;
done
