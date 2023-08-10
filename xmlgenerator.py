# from dicttoxml import dicttoxml
import xmltodict


class XMLGenerator:

    def sendText(self, title, prompt, text):
        xmldata = {
            'CiscoIPPhoneText': {
                'Title': title,
                'Prompt': prompt,
                'Text': text
            }
        }
        return xmltodict.unparse(xmldata, pretty=True)

    def ring(self, tone='Ring1.raw'):
        xmldata = {
            'CiscoIPPhoneExecute': {
                'ExecuteItem': {
                    '@Priority': '0',
                    '@URL': 'Play:' + tone
                }
            }
        }
        return xmltodict.unparse(xmldata, pretty=True)

    def preparecall(self, name, dn):
        xmldata = {
            'CiscoIPPhoneDirectory': {
                '@appId': 'TUC/click2dial',
                '@onAppFocusLost': 'App:Close:1:10:TUC/click2dial',
                'Prompt': 'Wahlvorbereitung',
                'DirectoryEntry': {
                    'Name': name,
                    'Telephone': dn
                }
            }
        }
        return xmltodict.unparse(xmldata, pretty=True)
