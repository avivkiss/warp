warp
====

FTL-FTP  

## Introduction
**warp** is a file transfer utility that uses UDT as its data transfer protocol. **warp** is currently in *alpha* and as such is not yet feature complete. **warp** is intended to mimic the basic functionality of standard ftp clients. At the moment it is missing support for many command line options, one notable current omission is directory transfers. 

## Installation
These instructions are for installing on Ubuntu or Max OS X. There is no reason why this can't be installed on any Linux distro, but the distros differ in package managers and the instructions here are tailored to Ubuntu. 

At the current moment the installation procedure is a bit involved and requires root privileges. 

### UDT
The first step is installing UDT. To do this we will download and build UDT from source. 

1. **Install git:** Feel free to skip this step if you have git installed already. If you do not have git installed (it should be by default on Mac) you can install it Ubuntu using `apt-get install git`. If you do not have Ubuntu please refer to the [git installation page](http://git-scm.com/book/en/Getting-Started-Installing-Git).
2. **Clone the repo:** From here on out we will be assuming that you are in the current user's home directory. To clone the udt repository into a local folder use the following command: `git clone git://git.code.sf.net/p/udt/git udt-git`.
3. **Make UDT:** More, or less depending on how you look at it, detailed instructions are available at the [UDT documentation](http://udt.sourceforge.net/udt4/doc/make.htm). If you are following along here:
    - `cd udt-git/udt4/`
    - The make command for UDT takes the following format: ` make -e os=XXX arch=YYY` where os can be LINUX, BSD, and OSX, and arch IA32, IA64, POWERPC, and AMD64. For Ubuntu on an x86-64 CPU the command looks like this `make -e os=LINUX arch=AMD64`. (You may also have to install make and g++ is not installed on Ubuntu type `apt-get install make` and `apt-get install g++`).
4. **Installing UDT:** To install UDT we must but the `UDT.h` header file as well as the library file compiled by the make command into a directory that will be in your path. I copied my header file into `/usr/include` and my library files into `/usr/lib`, you may need root privileges to do this.
    - On Mac OS X:
        - `mkdir /usr/include/udt`
        - `cp ~/udt-git/udt4/src/udt.h /usr/include/udt/udt.h`
        - `cp src/libudt.a /usr/lib/libudt.a`
        - `cp src/libudt.dylib /usr/lib/libudt.dylib`
    - On Ubuntu:
        - `mkdir /usr/include/udt`
        - `cp ~/udt-git/udt4/src/udt.h /usr/include/udt/udt.h`
        - `cp src/libudt.a /usr/lib/libudt.a`
        - `cp src/libudt.so /usr/lib/libudt.so`
5. **Cleanup:** If you'd like you can delete the udt source directory that we used in the above steps. If you downloaded UDT into your home directory you can remove it by taking the following steps: 
    - `cd ~`
    - `rm -r udt-git/`

### Install warp
1. **Clone warp:** You can install warp anywhere on your system, but we recommend installing it in the `~/.warp` directory. You can do this with the following command: `git clone https://github.com/avivkiss/warp.git ~/.warp`.
2. **Python dependencies:** warp was built and tested with python 2.7. In order to install the required python packages you must have pip installed. If you do not see the pip [installation page](https://pip.pypa.io/en/latest/installing.html) for more details (on Ubuntu you can just type `apt-get install python-pip`. Once you have pip installed you can install the requirements with the following command: ` `.

### Python dependencies
warp was built and tested with python 2.7. In order to install the required python package requirements.

[Installing pip.](https://pip.pypa.io/en/latest/installing.html)


### Usage
