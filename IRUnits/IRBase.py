import json
from ..base import *

def cleanManager(oldManager):
    oldManager = pm.PyNode(oldManager)
    for oa in oldManager.outputs(plugs=True):
        pm.deleteAttr(oa)
    pm.delete(oldManager)

class IRBase(object):
    def __init__(self,name='Default'):
        self.DATA = {'IRCLASS':'Base',
                     'NAME':None,
                     'MANAGER':None}
        self.setName(name)

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
        
    def setName(self,name):
        managerName = 'IRMNG_'+name
        self.DATA['NAME'] = name
        self.DATA['MANAGER'] = managerName

#--------------------------------------
    
class IRDAG(IRBase):
    def __init__(self,rootNode=None,name=None):
        #check if manager exists
        rootNode = pm.PyNode(rootNode)
        if rootNode.hasAttr('ROOT'):
            oldManager = rootNode.ROOT.inputs()
            if len(oldManager) > 0:
                if name is None:
                    name = oldManager[0].name().replace('IRMNG_','')
                else:
                    managerName = 'IRMNG_'+name
                    if pm.objExists(managerName):
                        raise AttributeError("This name is already exists! Please pick a different name!")
                    else:
                        oldManager = pm.PyNode(oldManager[0].name())
                        cleanManager(oldManager)
            else:
                if name is None:
                    raise AttributeError("This root has no manager yet! Please input new name!")
                else:
                    managerName = 'IRMNG_'+name
                    if pm.objExists(managerName):
                        raise AttributeError("This name is already exists! Please pick a different name!")
        else:
            if name is None:
                raise AttributeError("This root has no manager yet! Please input new name!")
            else:
                managerName = 'IRMNG_'+name
                if pm.objExists(managerName):
                    raise AttributeError("This name is already exists! Please pick a different name!")
            

        super(IRDAG,self).__init__(name)
        extension = {'PARENT':None,
                     'MEMBERS':{}}
        self.DATA.update(extension)
        self.ROOT = pm.PyNode(rootNode)
        self.updateNode()

    def _updateParent(self):
        p = self.ROOT.getParent()
        if p is not None:
            self.DATA['PARENT'] = p.name()
        else:
            self.DATA['PARENT'] = None

    def _updateMember(self):
        rootNode = self.ROOT
        if rootNode is not None:
            rootNode = pm.PyNode(rootNode)
            allDes = pm.listRelatives(rootNode,ad=True)
            self.DATA['MEMBERS']['ROOT'] = rootNode.fullPath()
            for d in allDes:
                type = d.type()
                self.DATA['MEMBERS'][type] = []
            for d in allDes:
                type = d.type()
                dagPath = d.fullPath()
                if dagPath not in self.DATA['MEMBERS'][type]:
                    self.DATA['MEMBERS'][type].append(dagPath)
        else:
            raise AttributeError("Please input root node")

    def _updateManager(self):
        if self.DATA['MANAGER'] is not None:
            manager = self.DATA['MANAGER']
            if not pm.objExists(manager):
                manager = pm.createNode('script',n=manager)
            else:
                manager = pm.PyNode(manager)
            #
            outputAttrName = manager.name()+'_output'
            if not manager.hasAttr(outputAttrName):
                manager.addAttr(outputAttrName,keyable=False)
            outputAttr = pm.PyNode(manager.name()+'.'+outputAttrName)
            #
            root = pm.PyNode(self.DATA['MEMBERS']['ROOT'])
            if not root.hasAttr('ROOT'):
                root.addAttr('ROOT',keyable=False)
            outputAttr >> root.ROOT
            #
            for k in self.DATA['MEMBERS'].keys():
                if k != 'ROOT':
                    attrName = manager.name()+'_'+k+'_input'
                    for m in self.DATA['MEMBERS'][k]:
                        mem = pm.PyNode(m)
                        if not mem.hasAttr(attrName):
                            mem.addAttr(attrName,keyable=False)
                        inputAttr = pm.PyNode(mem.name()+'.'+attrName)
                        outputAttr >> inputAttr
        
    def updateNode(self):
        self._updateParent()
        self._updateMember()
        self._updateManager()

    def setParent(self,parentName):
        parentName = str(parentName)
        self.DATA['PARENT'] = parentName
        pm.parent(self.DATA['MEMBERS']['ROOT'],parentName)

    
    def rebuildData(self,jsonPath):
        pass
