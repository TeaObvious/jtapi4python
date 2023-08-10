from config import SOAP_HOST, SOAP_USER, SOAP_PASSWD

providerString = f'{SOAP_HOST};login={SOAP_USER};passwd={SOAP_PASSWD}'

import jpype.imports
import time

from lru import LRU


def evicted(key, value):
    pytapihandle = value[0]
    phoneTerminal = value[1]

    if pytapihandle.isSuperUser:
        print("deleting Terminal for %s" % phoneTerminal.getName())
        pytapihandle.provider.deleteTerminal(phoneTerminal)
        print("deleted Terminal for %s" % key)


class PyTAPI:
    jpypeInstance = jpype
    provider = None
    isSuperUser = False

    terminalCache = None

    def __init__(self):
        self.jpypeInstance.startJVM('-ea', classpath=['lib/*', 'lib', 'classes'], convertStrings=False)

        import com.cisco.jtapi.Handler as Handler

        import javax.telephony.JtapiPeerFactory

        self.handler = Handler()

        peer = javax.telephony.JtapiPeerFactory.getJtapiPeer(None)
        self.provider = peer.getProvider(providerString)

        provCap = self.provider.getCapabilities()
        if provCap is not None and provCap.canObserveAnyTerminal() is True:
            self.isSuperUser = True

        self.provider.addObserver(self.handler)
        print('Awaiting ProvInServiceEv...')
        self.handler.providerInService.waitTrue()

        self.terminalCache = LRU(250, callback=evicted)

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean()

    def clean(self):
        print("shutting down all Terminals")
        for key, value in self.terminalCache.items():
            evicted(key, value)
            self.terminalCache[key] = None

        print('performing shutdown')
        self.provider.shutdown()
        print('provider shutdown called')
        time.sleep(1)

    def getTerminal(self, deviceName):
        if deviceName in self.terminalCache.keys():
            return self.terminalCache[deviceName][1]

        if self.isSuperUser:
            phoneTerminal = self.provider.createTerminal(deviceName)
        else:
            phoneTerminal = self.provider.getTerminal(deviceName)

        print('Awaiting CiscoTermInServiceEv for: ' + str(phoneTerminal.getName()) + '...')
        phoneTerminal.addObserver(self.handler)

        self.handler.fromTerminalInService.waitTrue()

        self.terminalCache[deviceName] = (self, phoneTerminal)

        return phoneTerminal

    def sendDataBySEP(self, phoneTerminal, data):
        if isinstance(phoneTerminal, str):
            phoneTerminal = self.getTerminal(phoneTerminal)

        # retry send data in case or error
        try:
            phoneTerminal.sendData(data)
        except:
            phoneTerminal.sendData(data)

        print('success')

    def sendDataByDN(self, dn, data):
        dn = str(dn)
        phoneAddress = self.provider.getAddress(dn)
        print('Awaiting CiscoAddrInServiceEv for: ' + str(phoneAddress.getName()) + '...')
        phoneAddress.addObserver(self.handler)
        self.handler.phoneAddressInService.waitTrue()
        phoneAddress.addCallObserver(self.handler)

        phoneTerminals = phoneAddress.getTerminals()
        for phoneTerminal in phoneTerminals:
            if 'SEP' in phoneTerminal.getName():
                self.sendDataBySEP(phoneTerminal, data)

    def __del__(self):
        # dunno how to properly shutdown, so lets kill everything
        System = jpype.JClass("java.lang.System")
        System.exit(0)
        self.jpypeInstance.shutdownJVM()
