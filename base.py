'''
DRE.base module is the foundation, the base to build The rigging tool
This module contain all the functions, classes that works at the lowest level to all rigging such as node manipulations.
Everything in here should NOT do more than 1 task per function

Note:
This tool was design to work best with pymel. It might work with cmds but pymel is highly recommended
'''

import pymel.core as pm

#-----------------------------------------------------------
# --- Arithmetic library -----------------------------------
# This library is used for node manipulation ---------------
# ----------------------------------------------------------

def nodeFromAttr(attr):
    if type(attr).__name__ == 'str':
        return pm.PyNode(attr.split('.')[0])
    else:
        if type(attr).__name__ != 'Attribute':
            raise AttributeError('Wrong arguments, attr only take pymel Attribute type')
        return attr.node()

def connect2Attrs(attr1,attr2):
    '''
    attr1 either pymel attribute type or number
    attr2 must be pymel attribute
    '''
    try:
        #pm.connectAttr(attr1,attr2)
        attr1 >> attr2
    except:
        #pm.setAttr(attr2,attr1)
        attr2.set(attr1)

class LinearNodesF(object):
    '''
    This class take in a list of pymel attributes type (Float) then provide various method to connect them into a arithmetic network
    '''
    def __init__(self,name='Default',*args):
        
        self._argCheck(args)
        self.name = name
        self.args = list(args)

    def _argCheck(self,args):
        for arg in args: #tuple
            try:
                float(arg) #see if its number
            except TypeError:
                if (type(arg).__name__ != 'Attribute') or (arg.type() != 'doubleLinear'):
                    raise AttributeError('Wrong arguments, *arg only take pymel Attribute Float type')

    #---------------------------------------------------------------------

    def setName(self,name):
        '''
        Set name for the nodes network
        '''
        self.name = name

    def setArgs(self,*args):
        '''
        Set new args list

        '''
        self._argCheck(args)
        self.args = list(args)

    def addArgs(self,*args):
        '''
        Add more args to current args list
        '''
        self._argCheck(args)
        for arg in args:
            self.args.append(arg)
        self.args = list(set(self.args))
        self.args.sort()

    def removeArgs(self,*args):
        '''
        Remove args from current args list
        '''
        temp = []
        for arg in self.args:
            if arg not in args:
                temp.append(arg)
        self.args = temp
    
    def _pma1DBase(self,operation):
        '''
        This method is the base for plusMinusAverage 1D node management
        parameter:
            operation: 1-sum,2-minus,3-average
        '''
        #---------------------------
        nodeName = 'PMA_'+self.name
        if (pm.objExists(nodeName)) and (pm.nodeType(nodeName)=='plusMinusAverage'):
            pma = pm.PyNode(nodeName)
        else:
            pma = pm.shadingNode('plusMinusAverage',n=nodeName,asUtility=True)
        
        for x in range(0,len(self.args)):
            connect2Attrs(self.args[x],pma.input1D[x])
            #self.args[x] >> pma.input1D[x]
        pma.operation.set(operation)
        return pma.output1D

    def _pma2DBase(self,slot,operation):
        '''
        This method is the base for plusMinusAverage 2D node management
        parameter:
            slot: x,y
            operation: 1-sum,2-minus,3-average
            
        '''
        #-- checking ------------ consider decorator later
        if slot not in ['x','y']:
            raise AttributeError('slot only accepts x,y')
            return None
        #---------------------------
        nodeName = 'PMA_'+self.name
        if (pm.objExists(nodeName)) and (pm.nodeType(nodeName)=='plusMinusAverage'):
            pma = pm.PyNode(nodeName)
        else:
            pma = pm.shadingNode('plusMinusAverage',n=nodeName,asUtility=True)
        
        for x in range(0,len(self.args)):
            if slot == 'x':
                connect2Attrs(self.args[x],pma.input2D[x].input2Dx)
                #self.args[x] >> pma.input2D[x].input2Dx
            else:
                connect2Attrs(self.args[x],pma.input2D[x].input2Dy)
                #self.args[x] >> pma.input2D[x].input2Dy

        pma.operation.set(operation)
        if slot == 'x':
            return pma.output2Dx
        else:
            return pma.output2Dy

    def _pma3DBase(self,slot,operation):
        '''
        This method is the base for plusMinusAverage 3D node management
        parameter:
            slot: x,y,z
            operation: 1-sum,2-minus,3-average
        '''
        #-- checking ------------ consider decorator later
        if slot not in ['x','y','z']:
            raise AttributeError('slot only accepts x,y,z')
            return None
        #---------------------------
        nodeName = 'PMA_'+self.name
        if (pm.objExists(nodeName)) and (pm.nodeType(nodeName)=='plusMinusAverage'):
            pma = pm.PyNode(nodeName)
        else:
            pma = pm.shadingNode('plusMinusAverage',n=nodeName,asUtility=True)
        
        for x in range(0,len(self.args)):
            if slot == 'x':
                connect2Attrs(self.args[x],pma.input3D[x].input3Dx)
                #self.args[x] >> pma.input3D[x].input3Dx
            elif slot == 'y':
                connect2Attrs(self.args[x],pma.input3D[x].input3Dy)
                #self.args[x] >> pma.input3D[x].input3Dy
            else:
                connect2Attrs(self.args[x],pma.input3D[x].input3Dz)
                #self.args[x] >> pma.input3D[x].input3Dz

        pma.operation.set(operation)
        if slot == 'x':
            return pma.output3Dx
        elif slot == 'y':
            return pma.output3Dy
        else:
            return pma.output3Dz
    
    def _multiplyDivideBase(self,slot,operation):
        '''
        This method is the base for multiplyDivide node management
        parameter:
            slot: x,y,z
            operation: 1-multiply,2-divide,3-power
        '''
        if slot not in ['x','y','z']:
            raise AttributeError('slot only accepts x,y,z')
            return None
        #--------------------------------
        nodeName = 'MD_'+self.name
        argsCount = len(self.args)
        out = self.args[0]
        if slot == 'x':
            for x in range(1,argsCount):
                md = pm.shadingNode('multiplyDivide',n=(nodeName+str(x).zfill(2)),asUtility=True)
                md.operation.set(operation)
                connect2Attrs(out,md.input1X)
                connect2Attrs(self.args[x],md.input2X)
                out = md.outputX 
        elif slot == 'y':
            for x in range(1,argsCount):
                md = pm.shadingNode('multiplyDivide',n=(nodeName+str(x).zfill(2)),asUtility=True)
                md.operation.set(operation)
                connect2Attrs(out,md.input1Y)
                connect2Attrs(self.args[x],md.input2Y)
                out = md.outputY
        else:
            for x in range(1,argsCount):
                md = pm.shadingNode('multiplyDivide',n=(nodeName+str(x).zfill(2)),asUtility=True)
                md.operation.set(operation)
                connect2Attrs(out,md.input1Z)
                connect2Attrs(self.args[x],md.input2Z)
                out = md.outputZ 

        return out


    #------------------------------------------------------------------------------------
    
    def plus1D(self):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Add them all together
        '''
        #---------------------------
        return self._pma1DBase(1)

    def plus2D(self,slot):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Using 2D inputs.
        Add them all together
        Parameter:
            slot: x,y
        '''
        return self._pma2DBase(slot,1)

    def plus3D(self,slot):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Using 3D inputs.
        Add them all together
        Parameter:
            slot: x,y,z
        '''
        return self._pma3DBase(slot,1)

    def minus1D(self):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Subtract the first arg to all subsequent args
        '''
        #---------------------------
        return self._pma1DBase(2)

    def minus2D(self,slot):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Using 2D inputs.
        Subtract the first arg to all subsequent args
        Parameter:
            slot: x,y
        '''
        return self._pma2DBase(slot,2)

    def minus3D(self,slot):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Using 3D inputs.
        Subtract the first arg to all subsequent args
        Parameter:
            slot: x,y,z
        '''
        return self._pma3DBase(slot,2)

    def average1D(self):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Return the average of all args
        '''
        #---------------------------
        return self._pma1DBase(3)

    def average2D(self,slot):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Using 2D inputs.
        Return the average of all args
        Parameter:
            slot: x,y
        '''
        return self._pma2DBase(slot,3)

    def average3D(self,slot):
        '''
        This method create a plusMinusAverageNode, then plug all attributes parse in
        then return a single attribute output. Using 3D inputs.
        Return the average of all args
        Parameter:
            slot: x,y,z
        '''
        return self._pma3DBase(slot,3)

    def mult(self):
        '''
        This method create a multDoubleLinear for each pairs of arg
        Return the products of all args
        '''
        nodeName = 'MULT_'+self.name
        argsCount = len(self.args)
        out = self.args[0]
        for x in range(1,argsCount):
            mult = pm.shadingNode('multDoubleLinear',n=(nodeName+str(x).zfill(2)),asUtility=True)
            connect2Attrs(out,mult.input1)
            connect2Attrs(self.args[x],mult.input2)
            out = mult.output 

        return out

    def div(self,slot):
        '''
        This method create a multiplyDivide for each pairs of arg
        Return the result of the division of the first arg and remaining args
        Parameter:
            slot: x,y,z
        '''
        return self._multiplyDivideBase(slot,2)

    def power(self,slot):
        '''
        This method create a multiplyDivide for each pairs of arg
        Return the result of the power of the first arg and remaining args
        Parameter:
            slot: x,y,z
        '''
        return self._multiplyDivideBase(slot,3)

    def arithExpr(self,expStr,argList = self.args):
        '''
        This method take in a string represent a linear arithmetic
        return the result
        to signify variable, use @ infront of the index number of the arg in arg list
        example:
        ((@0 + @1 + @4) * @2/@3)+@5
        argList = [5,6,7,8,9,10]
        '''
        #step1 - remove space
        expStr = expStr.replace(' ','')
        expStrList = list(expStr)
        expStrLen = len(expStr)
        #step2 - reorganize
        def _reorganize(expStr,argList):
            orderedArgs = []
            orderedStr = ''
            orderedCount = 0
            for x in range(0,expStrLen):
                char = expStrList[x]
            
                if char == '@':
                    orderedStr += '#'
                    realNum = ''
                    for tmp in range(x+1,expStrLen):                   
                        try:
                            num = int(expStrList[tmp])
                            realNum += expStrList[tmp]
                            expStrList[tmp] = '$'
                        except ValueError:
                            break
                    realNumValue = int(realNum)
                    orderedArgs.append(argList[realNumValue])
                    orderedStr += str(orderedCount)
                    orderedCount += 1
                else:
                    orderedStr += expStrList[x]
                    
            orderedStr = orderedStr.replace('$','')
            return orderedStr
        orderedStr = _reorganize(expStr,argList)
        orderedStrLen = len(orderedStr)
    
        #getStr in brackets
        '''
        openCount = len([x for x in orderedStr if x == '('])
        closeCount = len([x for x in orderedStr if x == ')'])
        if openCount != closeCount:
            raise ValueError('open brackets does not match close brackets')
    
        subStrList = []
        for x in range(0,openCount):
            tmpStr = ''
            for ri in range(-1,(orderedStrLen*-1-1),-1):
                char = orderedStr[ri]
                if char == '(':#start counting forward
                    for fi in range((orderedStrLen+ri),orderedStrLen):
                        tmpStr += orderedStr[fi]
                        if orderedStr[fi] == ')':
                            break
                    break 
            subStrList.append(tmpStr)
        '''

        
        

