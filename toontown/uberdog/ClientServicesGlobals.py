def generateLookupTable(key):
    return [hex(ord(str(key)[i % len(str(key))]) & ord(key[4]) & i) for i in range(255)]


def encodeHexString(lookupTable, hexString):
    return ''.join(lookupTable[int('0x%s' % i, 16)] for i in hexString.split('0x')[1:])
