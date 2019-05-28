import xmltodict

class CmsStatus:
    name = None

    def __init__(self, name, payload):
        self.name = name
        self.__data = xmltodict.parse(payload)
        for entry in self.__data['data']['statusTable']['entries']['entry']:
            id = entry['@id']
            if id == 'version':
                self.version = entry['value']
            elif id == 'uptime':
                self.uptime = entry['value']
            elif id == 'mediaStatus':
                self.mediaStatus = entry['value']
            elif id == 'numClientCalls':
                self.numClientCalls = entry['value']
            elif id == 'numLyncCalls':
                self.numLyncCalls = entry['value']
            elif id == 'numSipCalls':
                self.numSipCalls = entry['value']
            elif id == 'numConfs':
                self.numConfs = entry['value']
            elif id == 'mediaBitRateOutgoing':
                self.mediaBitRateOutgoing = entry['value']
            elif id == 'mediaBitRateIncoming':
                self.mediaBitRateIncoming = entry['value']
