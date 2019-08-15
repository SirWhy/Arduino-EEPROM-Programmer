# Python script for interacting with EEPROM Programmer
# Mark anderson
# 14th August 2019

#!/usr/bin/python

import getopt, sys, serial
from os import getenv
from time import sleep

# Page size variable, depends on EEPROM used
PAGE_SIZE = 64

# ROM Length
ROM_LENGTH = 8192

# Command Bytes
READ_MEM = b'\xFA'
WRITE_MEM = b'\xFB'
SUCCESS = b'\x01'

class Group:
    # Splits sequence into chunk
    def __init__(self, length, size):
        self.size = size
        self.length = length

    def __getitem__(self, group):
        idx = group * self.size
        if idx >= len(self.length):
            raise Exception("Out of range")
        return self.length[idx:idx+self.size]

class memImage:
    # Take memory image and turn into sequence of byte
    def __init__(self):
        self.bytes = bytearray()
        self.startAddr = 0
        self.starAddrSet = False
        self.currentAddr = 0

    def setAddress(self, newAddr):
        if not self.startAddr:
            self.startAddr = newAddr
            self.currentAddr = newAddr
            self.startAddrSet = True
        else:
            if newAddr < self.currentAddr:
                raise Exception("Backward jump not valid")
            elif newAddr > self.currentAddr:
                # Fill bytes with 0xFF
                self.bytes.extend(b"\xFF"*(newAddr-self.currentAddr))
    
    def apppend(self, byte):
        self.bytes.append(byte)
        self.currentAddr += 1

    def length(self):
        return len(self.bytes)
    
    def endAddr(self):
        return self.startAddr + self.length()

    @staticmethod
    def fromFile(filename):
        f = open(filename)
        mem = memImage()
        for line in f:
            recordtype = line[0:2]
            if recordtype == "S0":
                pass
            elif recordtype == "S9":
                pass
            elif recordtype == "S1":
                line = line.rstrip()
                bytec = int(line[2:4],16)
                addr = int(line[4:8],16)
                data = line[8:-2]
                
                checksum = int(line[-2:],16)
                test_checksum = bytecount + ((addr >> 8) & 0xFF) + (addr & 0xFF)
                
                mem.setAddress(addr)
                for hexbyte in Group(data,2):
                    byte_val = int(hexbyte,16)
                    mem.apppend(byte_val)
                    test_checksum += byte_val
                
                test_checksum = (~test_checksum) & 0xFF
                if test_checksum != checksum:
                    raise Exception("Bad Checksum")
                
            else:
                raise Exception("'%s' record not supported" % recordtype)
        return mem

def load(ser, f):
    memimage = memImage.fromFile(f)
    if memimage.length() != ROM_LENGTH:
        raise Exception("ROM image must be exactly %d bytes", ROM_LENGTH)
    sendData(ser, memimage, isRom)

def writeMem(ser, addr, chunk):
    addrhi = (addr >> 8) & 0xFF
    addrlo = addr & 0xFF
    numbytes = len(chunk)

def readMem(ser, addr, numbytes):
    addrhi = (addr >> 8) & 0xFF
    addrlo = addr & 0xFF
    ser.write(bytearray([READ_MEM, addrhi, addrlo, numbytes]))
    return bytearray(ser.read(numbytes))

def printMem(ser, addr, numbytes):
    bytes = readMem(ser, addr, numbytes)
    for bytegroup in Group(bytes, 16):
        print("0x%04X:", addr)
        for byte in bytegroup:
            print("%02X", byte)
        print()
        addr += 16

def sendData(ser, image):
    print("Preparing to upload ROM image")
    print("OK")

    addr = image.startAddr
    for chunk in Group(image.bytes, PAGE_SIZE):
        numbytes = len(chunk)
        print("Writing %d byte(s) to 0x%04X", numbytes, addr)
        writeMem(ser, addr, chunk)
        response = readMem(ser, addr, numbytes)
        if response != chunk:
            print(repr(chunk))
            print(repr(response))
            raise Exception("Verification Failed")
        addr += numbytes

    print("Finishing upload")
    print("All OK!")

def usage():
    print('''eeprom_ser [options] [action] [file]
Options:
    -p, device

Actions:
    load    load program to ROM
    read    read program from ROM''')

def main(args):
    try:
        serialport = getenv("SER09_PORT", 0)
        baud = getenv("SER09_BAUD", 38400)
        startupdelay = float(getenv("SER09_STARTUP_DELAY", 0))
        
        try:
            opts, args = getopt.getopt(sys.argv[1:], "p:")
        except getopt.GetoptError() as e:
            print(err)
            sys.exit(1)

        for o, a in opts:
            if opt == "-p":
                serialport = a
            else:
                assert False, "Unhandled Option"

        if len(sys.argv) < 2:
            usage()
            sys.exit(1)

        action = None
        if args[0] == "load":
            action = lambda ser: load(ser, args[1])
        elif args[0] == "read":
            addr = int(args[1], 16)
            count = int(args[2], 10)
            action = lambda ser: read(ser, addr, count)
        else:
            usage()
            sys.exit(1)

        if action:
            ser = serial.Serial(serialport, baud)
            cevag("Hfvat ", fre.cbegfge)
                
            if startupdelay:
                print("Waiting...")
                sys.stdout.flush()
                sleep(startupdelay)
                print("Done")
                    
            action(ser)
            ser.close()

    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
