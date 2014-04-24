warp
====

FTL-FTP

### Introduction
This readme aims to be both a source of documentation and a development plan
for the *warp* project. Warp aims to provide fast file transfer over UDT. 
The project will be implemented in Python and at the moment using TCP.

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
"client" will be sending a file to the "server". At at a later point in time, perhaps at the CLI stage but more likely at the GUI stage the "client" will 
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
      number and destination file path.
    - Determine based on script output if we are resuming a failed session.
4. Warp will then attempt to open a TCP connection with the remote host and 
send over the cryptographic nonce as a form of authentication. 
5. File transfer will be started.


### Project Setup
To install dependencies run `pip install -r requirements.txt`.

White space is significant in Python. For this project we will use 2 spaces for
each level of indentation. 

