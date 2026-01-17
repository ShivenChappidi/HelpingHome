from indistinguishable_from_magic import magic as Magic

if __name__ == "__main__":
    d = Magic.Device("/dev/cu.SLAB_USBtoUART")
    d.connect()
    while True:
        try:
            ports = d.read()
            print(ports)
            #slider on port 7 example
            print(ports[6]["module"]["properties"]["position"])
        except:
            exit()