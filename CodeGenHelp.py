import re

class ExecutionEnviornment:

    def __init__(self):
        self.data = [None] * 256
        self.at = 0

    def makeEntry(self, entry):
        self.data[self.at] = entry
        self.at += 1

    def incrementAt(self):
        self.at += 1

    def printEnviornment(self):
        for i, data in enumerate(self.data):
            i = i + 1
            if (i % 8 == 0 and i != 0 and i != 255):
                print(i, data, end='\n')
            else:
                print('{0:<8}'.format(i), data, end='\t\t')
        print('\n')

    def printEnviornmentCompress(self):
        for i, data in enumerate(self.data):
            i = i + 1
            if (i % 8 == 0 and i != 0 and i != 255):
                print(data, end='\n')
            else:
                print(data, end='\t')
        print('\n')

class TableEntry:

    def __init__(self):
        self.temp = None
        self.var = None
        self.address = None

    def updateAll(self, temp, var, address):
        self.temp = temp
        self.var = var
        self.address = address

    def updateAddress(self, address):
        self.address = address


    def printTableEntry(self):
        print('\t', self.temp, '\t', self.var, '\t', self.address)

class StaticTable:

    def __init__(self):
        self.data = []

    def makeEntry(self, tableEntry):
        self.data.append(tableEntry)

    def getTempAtVal(self, var):
        for datum in self.data:
            if datum.var == var:
                return datum.temp

    def printStaticTable(self):
        print("INFO CG - Printing Static Table...")
        print('\t', "Temp", '\t', "Var", '\t', "Address", end='\n')
        for entry in self.data:
            entry.printTableEntry()

class JumpTableEntry:

    def __init__(self):
        self.temp = None
        self.distance = None
        self.at = None

    def updateAll(self, temp, distance, at):
        self.temp = temp
        self.distance = distance
        self.at = at

    def updateTemp(self, temp):
        self.temp = temp

    def updateAt(self, at):
        self.at = at

    def updateDistance(self, distance):
        self.distance = distance

    def printTableEntry(self):
        print('\t', self.temp, '\t', self.distance, '\t\t', self.at)

class JumpTable:

    def __init__(self):
        self.data = []

    def makeEntry(self, tableEntry):
        self.data.append(tableEntry)

    # def getTempAtVal(self, var):
    #     for datum in self.data:
    #         if datum.var == var:
    #             return datum.temp

    def printJumpTable(self):
        print("INFO CG - Printing Jump Table...")
        print('\t', "Temp", '\t', "Distance", '\t', "At", end='\n')
        for entry in self.data:
            entry.printTableEntry()

class CodeGenerator:

    def __init__(self, ast):
        self.ast = ast
        self.executionEnviornment = None
        self.tempCount = 0
        self.jumpCount = 0
        self.staticTable = StaticTable()
        self.jumpTable = JumpTable()

    def processAndPrintAST(self):
        print("Processed AST")
        print(self.ast)

    def createExecutionEnviornmnet(self):
        print("INFO CG - Creating Execution Enviornmnet...")
        self.executionEnviornment = ExecutionEnviornment()

    def printExecutionEnviornmnet(self):
        print("INFO CG - Printing Execution Enviornmnet...")
        self.executionEnviornment.printEnviornment()
        self.staticTable.printStaticTable()
        self.jumpTable.printJumpTable()

    def printEnv(self):
        print("INFO CG - Printing Execution Enviornmnet...")
        for i, datum in enumerate(self.executionEnviornment.data):
            if datum is None:
                self.executionEnviornment.data[i] = '00'
        self.executionEnviornment.printEnviornmentCompress()

    def generateCode(self):

        def varDeclSubRoutine(id):

            #initalize data to append to execution envionrment
            LDA = 'A9'
            ZERO = '00'
            STA = '8D'
            temp = 'T' + str(self.tempCount)

            #increment the execution envionrmnet's tempCounter
            self.tempCount += 1

            #load these data into the execution enviornment
            self.executionEnviornment.makeEntry(LDA)
            self.executionEnviornment.makeEntry(ZERO)
            self.executionEnviornment.makeEntry(STA)
            self.executionEnviornment.makeEntry(temp)
            self.executionEnviornment.makeEntry('XX')

            #make entry into static table
            entry = TableEntry()
            hexyTemp = temp + 'XX'
            entry.updateAll(hexyTemp, id, '+0')
            self.staticTable.makeEntry(entry)

        def assignmnetSubRoutine(id, val):

            #quick check to see if val is also an id
            match = re.match('[a-z]', val)

            if match:

                #initalize data to append to execution envionrment
                LDAmem = 'AD'
                tempVal = self.staticTable.getTempAtVal(val)
                tempPrefixVal = tempVal[0:2]
                STA = '8D'
                tempID = self.staticTable.getTempAtVal(id)
                tempPrefixID = tempID[0:2]

                #load these data into the execution enviornment
                self.executionEnviornment.makeEntry(LDAmem)
                self.executionEnviornment.makeEntry(tempPrefixVal)
                self.executionEnviornment.makeEntry('XX')
                self.executionEnviornment.makeEntry(STA)
                self.executionEnviornment.makeEntry(tempPrefixID)
                self.executionEnviornment.makeEntry('XX')

            else:
                #initalize data to append to execution envionrment
                LDA = 'A9'
                hexyVal = '0' + val
                STA = '8D'

                temp = self.staticTable.getTempAtVal(id)

                tempPrefix = temp[0:2]

                #load these data into the execution enviornment
                self.executionEnviornment.makeEntry(LDA)
                self.executionEnviornment.makeEntry(hexyVal)
                self.executionEnviornment.makeEntry(STA)
                self.executionEnviornment.makeEntry(tempPrefix)
                self.executionEnviornment.makeEntry('XX')

        def printSubRoutine(id):

            #initalize data to append to execution envionrment
            LDAy = 'AC'
            temp = self.staticTable.getTempAtVal(id)
            tempPrefix = temp[0:2]
            LDAx = 'A2'
            SYS_CALL_PRINT = '01' #print in in Y register
            SYS_CALL = 'FF'

            #load these data into the execution enviornment
            self.executionEnviornment.makeEntry(LDAy)
            self.executionEnviornment.makeEntry(tempPrefix)
            self.executionEnviornment.makeEntry('XX')
            self.executionEnviornment.makeEntry(LDAx)
            self.executionEnviornment.makeEntry(SYS_CALL_PRINT)
            self.executionEnviornment.makeEntry(SYS_CALL)

        def ifSubRoutine(boolOp, boolVal1, boolVal2):

            LDAxMem = 'AE'
            tempVal1 = self.staticTable.getTempAtVal(boolVal1)
            tempPrefixVal1 = tempVal1[0:2]
            COMPARE = 'EC'
            tempVal2 = self.staticTable.getTempAtVal(boolVal2)
            tempPrefixVal2 = tempVal2[0:2]
            BNE = 'D0'

            #make entry into jump table
            entry = JumpTableEntry()
            hexyJump = 'J' + str(self.jumpCount)
            entry.updateTemp(hexyJump)


            self.executionEnviornment.makeEntry(LDAxMem)
            self.executionEnviornment.makeEntry(tempPrefixVal1)
            self.executionEnviornment.makeEntry('XX')
            self.executionEnviornment.makeEntry(COMPARE)
            self.executionEnviornment.makeEntry(tempPrefixVal2)
            self.executionEnviornment.makeEntry('XX')
            self.executionEnviornment.makeEntry(BNE)
            self.executionEnviornment.makeEntry(hexyJump)
            # make sure the <at> for this entry is in the correct sequence
            entry.updateAt(self.executionEnviornment.at)
            self.jumpTable.makeEntry(entry)

        def EOPsubRoutine():

            BRK = '00'

            self.executionEnviornment.makeEntry(BRK)


        AST = self.ast.copy()
        AST = AST # test AST[0:n]

        while len(AST) != 0:

            print(AST[0])
            currentToken = AST[0][0]

            if currentToken == "VarDecl":
                print("INFO CG - Variable Decleration...")
                id = AST[2][0]
                varDeclSubRoutine(id)
                del AST[0] #varDecl

            if currentToken == "AssignmentStatement":
                print("INFO CG - Assignment Statement...")
                id = AST[1][0]
                val = AST[2][0]
                assignmnetSubRoutine(id, val)
                del AST[0] #AssignmentStatement

            if currentToken == "PrintStatement":
                print("INFO CG - PrintStatement...")
                id = AST[1][0]
                printSubRoutine(id)
                del AST[0] #PrintStatement

            if currentToken == "IfStatement":
                print("INFO CG - IfStatement...")
                boolOp = AST[1][0]
                boolVal1 = AST[2][0]
                boolVal2 = AST[3][0]
                ifSubRoutine(boolOp, boolVal1, boolVal2)
                del AST[0] #IfStmt

            # No $ in AST. Use this instead to find EOP and run EOPsubRoutine()
            if len(AST) == 1:
                print("INFO CG - END OF PROGRAM...")
                # delete token before else so we arent caught capturing
                #   the same node (infinte loop)
                EOPsubRoutine()
                del AST[0]

            else:
                del AST[0]

        #update jumps
        def updateJumps():
            print("INFO CG - Updating Jump Table...")
            for jump in self.jumpTable.data:
                print("\t INFO CG - Updating " + jump.temp + "...")
                currentLocation = self.executionEnviornment.at
                jumpLocation = jump.at
                distance = currentLocation - jumpLocation
                #update the newly calc'd distance
                if distance <= 10:
                    distance = '0' + str(distance - 1)
                    jump.updateDistance(distance)
                else:
                    jump.updateDistance(distance - 1)

        def backpatchJumps():
            print("INFO CG - Backpatching Jump Temp With Distance...")
            for jump in self.jumpTable.data:
                print("\t INFO CG - Updating " + jump.temp + "...")
                self.executionEnviornment.data[jump.at - 1] = jump.distance

        def updateStaticTable():
            print("INFO CG - Updating Static Trial...")
            for entry in self.staticTable.data:
                print("\t INFO CG - Updating " + entry.temp + "...")
                current = self.executionEnviornment.at
                hexyCurrent = hex(current).split('x')
                hexyCurrent = hexyCurrent[1].upper()
                entry.updateAddress(hexyCurrent)
                self.executionEnviornment.makeEntry('%' + entry.var)

        def backpatchEnvironmentFromStaticTable():
            print("INFO CG - Backpatching Enviornment Froom Static Table...")
            for entry in self.staticTable.data:
                for i, datum in enumerate(self.executionEnviornment.data):
                    if entry.temp[0:2] == datum:
                        self.executionEnviornment.data[i] = entry.address
                        print(entry.temp[0:2])
                    if datum == 'XX':
                        self.executionEnviornment.data[i] = '00'

        updateJumps()
        backpatchJumps()
        updateStaticTable()
        backpatchEnvironmentFromStaticTable()
