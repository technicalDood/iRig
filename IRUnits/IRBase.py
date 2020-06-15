import json
from ..base import *

class IRBase(object):
    def __init__(self):
        self.DATA = {'IRCLASS':'Base'}

    def checkData(self,dataDict):
        if 'IRCLASS' in dataDict.keys():
            if dataDict['IRCLASS'] == self.DATA['IRCLASS']:
                dataKeys = dataDict.keys()
                for k in dataKeys:
                    if k not in self.DATA.keys():
                        return False
                return True
            else:
                return False
        else:
            return False
    
    def setData(self,dataDict):
        if self.checkData(dataDict):
            for key in dataDict.keys():
                self.DATA[key] = dataDict[key]
        else:
            raise AttributeError(str(dataDict) + " is NOT compatible with this Unit!")

    def getData(self):
        return self.DATA

    def saveData(self,jsonPath):
        try:
            with open(jsonPath,'w') as outJson:
                json.dump(self.DATA, outJson, ensure_ascii=False, indent=4)
                print(jsonPath + ' exported!')
        except Exception as e:
            print(e)

    def loadData(self,jsonPath):
        try:
            with open(jsonPath,'r') as inJson:
                tempDict = json.load(inJson)
                self.setData(tempDict)
        except:
            print("ERROR loading Json:")
            print(jsonPath)
            return False
        

