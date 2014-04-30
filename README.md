warp
====

FTL-FTP

### Todo
make .todo file
tests

### Introduction
This readme aims to be both a source of documentation and a development plan
for the *warp* project. Warp aims to provide fast file transfer over UDT. 
The project will be implemented in Python 2.7 and at the moment using TCP.

Eventually TCP will be swapped out and replaced with something like 
[pyUDT](https://github.com/cjhanks/PyUDT). The original pyUDT has not been 
updated in a while and there appear to be several forks that may be better than
the original repository but this will be discussed at a later date. 

The end goal is to build a GUI file transfer client, but for now we will 
implement a basic CLI version to get things started. The CLI version will 
support most of the essential basic features that we have identified, namely 
the capability to resume failed transfers.

### Protocol - a high level overview
Before going into the details of the handshake and initiation protocol some
terminology needs to be clarified. In the following description the 
"client" will be sending a file to the "server". At at a later point in time,
perhaps at the CLI stage but more likely at the GUI stage the "client" will 
also be able to pull a file off the server.

In order to initiate a file transfer the following steps will be taken:

1. The required software will be installed on both the client and the server.
2. The client, or file sender, will run `warp` passing in the remote host 
IP, the source file name, and the destination on the remote host.
3. Warp will start an SSH session with the host. For now we will assume
that authentication is done with an ssh-agent. The script will then do the 
following:
    - Negotiate a port number with the remote host.
    - Run the `server.py` script passing in a cryptographic 
      [nonce](http://en.wikipedia.org/wiki/Cryptographic_nonce), port 
      number, file hash and destination file path.
    - Determine based on script output if we are resuming a failed session.
4. Warp will then attempt to open a TCP connection with the remote host and 
send over the cryptographic nonce as a form of authentication. 
5. File transfer will be started.

### Ravioli Code
There are [many different types](http://en.wikipedia.org/wiki/Spaghetti_code#Related_terms) 
of code. We all know and love spaghetti code (not really), cringe at the 
over-engineered Java programmer's lasagna code, and strive for the encapsulated
functionality of ravioli code. 

Unfortunately, ravioli code is hard to write, so as development progresses the
overall program structure may change to further fit our dream of encapsulated
functionality. Until then here is the base structure for this program:

#### handshake.py
hanshake.py is responsible for creating a secure connection with the remote 
host. This means starting the SSH session, doing the port negotiation, 
starting the remote server and ultimately returning a "live" TCP connection.

#### server.py
server.py is the remote server that is started by the handshake, this is responsible
for listening for the connection from the client and saving the file 
accordingly. Further, if a connection fails during a file transfer the server
should save the file transfer state to disk. Upon reconnecting with the host
the server should check if it has any of the file that will be transferred
and if so inform the host of how much data it has successfully saved. The
server uses a hash of the file sent by the client to determine if it has
"seen" that file before. 

#### transfer.py
transfer.py is responsible for chunking and sending the file to the remote host
in addition it should be able to resume file transfers from a chunk location
and handle errors correctly.

#### config.py
This is a file that will store our global vars, in the future we can expand 
this to read in config from a configuration file.

### Project Setup
To install dependencies run `pip install -r requirements.txt`.

White space is significant in Python. For this project we will use 2 spaces for
each level of indentation. 

