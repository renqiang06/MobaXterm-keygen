#/usr/bin/env python3
'''
Author: renqiang06
'''
import os, sys, zipfile, random, socket, time

UserNameLength = 5
VariantBase64Table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
VariantBase64Dict = { i : VariantBase64Table[i] for i in range(len(VariantBase64Table)) }
RandomUserName = ''.join(random.sample(VariantBase64Table[:-3], UserNameLength))
hostname = socket.gethostname()

def write_logfile(text):
    logfile = open('log_{0}.txt'.format(hostname[-6:]), 'a')
    logfile.write(time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime()) + ':' + hostname + str(text) + '\n')
    logfile.close()

def VariantBase64Encode(bs : bytes):
    result = b''
    blocks_count, left_bytes = divmod(len(bs), 3)

    for i in range(blocks_count):
        coding_int = int.from_bytes(bs[3 * i:3 * i + 3], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 18) & 0x3f]
        result += block.encode()

    if left_bytes == 0:
        return result
    elif left_bytes == 1:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        result += block.encode()
        return result
    else:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        result += block.encode()
        return result

def EncryptBytes(key : int, bs : bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xff))
        key = result[-1] & key | 0x482D
    return bytes(result)

class LicenseType:
    Professional = 1
    Educational = 3
    Persional = 4

def GenerateLicense(Type : LicenseType, Count : int, UserName : str = RandomUserName, MajorVersion : int = 21, MinorVersion : int = 2):
    assert(Count >= 0)
    LicenseString = '%d#%s|%d%d#%d#%d3%d6%d#%d#%d#%d#' % (Type, 
                                                          UserName, MajorVersion, MinorVersion, 
                                                          Count, 
                                                          MajorVersion, MinorVersion, MinorVersion,
                                                          0,    # Unknown
                                                          0,    # No Games flag. 0 means "NoGames = false". But it does not work.
                                                          0)    # No Plugins flag. 0 means "NoPlugins = false". But it does not work.
    print(LicenseString) # 打印License字符串
    EncodedLicenseString = VariantBase64Encode(EncryptBytes(0x787, LicenseString.encode())).decode()
    print(EncodedLicenseString)
    with zipfile.ZipFile('Custom.mxtpro', 'w') as f:
        f.writestr('Pro.key', data = EncodedLicenseString)

def help():
    print(f'Usage:\n    MobaXterm-Keygen.py <UserName默认:随机5位字符> <Version默认:21.2>\n')
    print('    <UserName>:      eg:Mrren')
    print('    <Version>:       eg:21.2')

if __name__ == '__main__':
    help()
    UserName = ''
    MajorVersion, MinorVersion = 0, 0
    try:
        UserName = sys.argv[1]
        MajorVersion, MinorVersion = sys.argv[2].split('.')[0:2]
        MajorVersion = int(MajorVersion)
        MinorVersion = int(MinorVersion)
    except:
        pass
    try:
        GenerateLicense(LicenseType.Professional, 
                        1,
                        UserName,
                        MajorVersion, 
                        MinorVersion)
        print(f'[*] Success!\n[*] File generated: %s' % os.path.join(os.getcwd(), 'Custom.mxtpro'))
        print('[*] Please move or copy the newly-generated file to MobaXterm\'s installation path.')
    except Exception as e:
        print(e)
        write_logfile(e+', License获取失败!')
else:
    print('[*] ERROR: Please run this script directly')
