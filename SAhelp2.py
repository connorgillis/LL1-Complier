import re

class Scope:

    def __init__(self, name):
        self.name = name
        self.symbols = []

class Symbol:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.val = None
        self.init = False
        self.used = False
        self.usedCount = 0

class Semantic:

    def __init__(self, ast):
        self.ast = ast
        self.scopes = []

    def printScopeAreas(self):
        unusedSymbolsIsInit = []
        unusedSymbolsIsNotInit = []
        for scope in self.scopes:
            print("Scope Name: " + str(scope.name))
            print("- Scope Symbols")
            #print(scope.symbols)
            for symbol in scope.symbols:
                if symbol.used == False and symbol.init == True:
                    unusedSymbolsIsInit.append(symbol)
                if symbol.used == False and symbol.init == False:
                    unusedSymbolsIsNotInit.append(symbol)
                if symbol != scope.symbols[0]:
                    print("*")
                print("*** ID: " + symbol.id)
                print("*** TYPE: " + symbol.type)
                print("*** VAL: " + str(symbol.val))
                print("*** INIT: " + str(symbol.init))
                print("*** USED: " + str(symbol.used))
                print("*** USEDCOUNT: " + str(symbol.usedCount))

            print('\n')
        print("Unused Symbols (Decl + Initialized ): ")
        for symbol in unusedSymbolsIsInit:
            print("*ID: " + symbol.id + " *TYPE: " + symbol.type + " *VAL: " + str(symbol.val))
        print("Unused Symbols (Decl + Not Initialized): ")
        for symbol in unusedSymbolsIsNotInit:
            print("*ID: " + symbol.id + " *TYPE: " + symbol.type + " *VAL: " + str(symbol.val))

    def toString(self):
        self.traversalResult = ""

        #recursive function to handle the expansion of nodes

        def expand(node, depth):
            for i in range(depth):
                self.traversalResult +=  " # "
            if node.children is None or len(node.children) == 0:
                self.traversalResult += " [" + node.name + "] "
                self.traversalResult += '\n'

            else:
                # if we are the root
                self.traversalResult += (" <" + node.name + "> " + '\n')
                for i in range(len(node.children)):
                    expand(node.children[i], depth + 1)


        expand(self.ast.root, 0)

        return self.traversalResult

    def cleanAST(self, traversal):
        cleanAST = []
        for line in traversal.split("\n"):
            depth = 0
            thisLine = line
            for char in thisLine.split(" "):
                if char is "#":
                    depth += 1
            
            print(line)
            cleaned = re.sub('[^A-Za-z0-9]+', '', line)
            cleanAST.append([cleaned, depth])

        del cleanAST[len(cleanAST)-1]

        return cleanAST

    def createScopeAreas(self, cleanAST):
        currentScope = 1
        for node in cleanAST:
            if node[0] == "Block":
                self.scopes.append(Scope(currentScope))
                currentScope += 1

    def parseSymbols(self, cleanAST):
        AST = cleanAST.copy()

        current = 0
        while len(AST) != 0:
            match = re.match('(TYPEINT)|(TYPESTR)|(TYPEBOOL)', AST[current][0])
            if match:
                currentScope = AST[current][1] - 1
                type = AST[current][0]
                del AST[current]
                symbolToInsert = Symbol(AST[current][0], type)
                symbolAlreadyDeclared = False
                for symbol in self.scopes[currentScope - 1].symbols:
                    if symbol.id == symbolToInsert.id:
                        symbolAlreadyDeclared = True

                if symbolAlreadyDeclared:
                    print("ERROR SA - " + symbolToInsert.type + " [" + symbolToInsert.id + "] redeclared in same scope. ")
                    print("ERROR SA - Will not add to symbol table ")
                else:
                    self.scopes[currentScope - 1].symbols.append(symbolToInsert)
            else: del AST[current]

    def parseAssign(self, cleanAST):

        def assignTypeCheck(symbol, val):
            if type == "TYPEINT":
                match = re.match('(\d)+?', AST[current][0])
                if match:
                    print("INFO SA - Type Checking... " + type + " with " + val)
                    print("INFO SA - Successful Assignment: ID " + id + " found in scope" + str(currentScope + 1) + " assigned val " + val)
                    symbol.init = True
                    symbol.val = val
                    return True
                else:
                    print("ERROR SA - Type Mismatch: " + type + " [" + id + "] cannot be assigned string or bool value: " + val)
                    symbol.val = "typemismatch"
            elif type == "TYPEBOOL":
                print("Bool")
                match = re.match('(True)|(False)', AST[current][0])
                if match:
                    print("INFO SA - Type Checking... " + type + " with " + val)
                    print("INFO SA - Successful Assignment: ID " + id + " found in scope" + str(currentScope + 1) + " assigned val " + val)
                    symbol.init = True
                    symbol.val = val
                else:
                    print("ERROR SA - Type Mismatch: " + type + " [" + id + "] cannot be assigned int or string value: " + val)
                    symbol.val = "typemismatch"
            elif type == "TYPESTR":
                match = re.match('([a-z])+', AST[current][0])
                if match:
                    print("INFO SA - Type Checking... " + type + " with " + val)
                    print("INFO SA - Successful Assignment: ID " + id + " found in scope" + str(currentScope + 1) + " assigned val " + val)
                    symbol.init = True
                    symbol.val = val
                else:
                    print("ERROR SA - Type Mismatch: " + type + " [" + id + "] cannot be assigned int boolean: " + val)
                    symbol.val = "typemismatch"

        AST = cleanAST.copy()
        current = 0
        while len(AST) != 0:

            match = re.match('AssignmentStatement', AST[current][0])
            if match:
                currentScope = AST[current][1] - 1
                # for scopes listt (index 0)
                # print + 1

                # delete assign stmt
                del AST[current]

                # the id we want to assign
                id = AST[current][0]

                del AST[current]
                val = AST[current][0]

                print("INFO SA - Attempt Assignment: [" + id + "] <=  [" + val + "]")

                found = False

                for scope in self.scopes:

                    for symbol in scope.symbols:

                        idToTest = symbol.id

                        lenScopes = len(self.scopes)
                        lenSymbols = len(scope.symbols)

                        thisScopeCheck = self.scopes.index(scope) + 1
                        thisSymbolCheck = scope.symbols.index(symbol) + 1

                        # check this scope
                        if id == idToTest and scope.name == currentScope + 1:
                            type = symbol.type
                            assignTypeCheck(symbol, val)
                            found = True
                        # check prev scopes
                        elif id == idToTest and scope.name < currentScope + 1:
                            type = symbol.type
                            assignTypeCheck(symbol, val)
                            found = True
                        # we are at the end of both the scopes and symbols and it's still not it, then it was never declared..
                        elif id != idToTest and thisScopeCheck == lenScopes and thisSymbolCheck == lenSymbols and found == False:
                            print("ERROR SA - Unsuccessful Assignment: ID " + id + " not declared in this, or any previous scope found in scopes..."  + " won't assign " + val)

            else: del AST[current]

    def parsePrintStatement(self, cleanAST):
        AST = cleanAST.copy()
        current = 0
        while len(AST) != 0:

            match = re.match('PrintStatement', AST[current][0])
            if match:
                currentScope = AST[current][1] - 2
                # for scopes listt (index 0)
                # print + 1

                # delete print stmt
                del AST[current]

                # this is the id they wish to print
                id = AST[current][0]

                found = False
                # run thru everything
                for scope in self.scopes:

                    for symbol in scope.symbols:

                        lenScopes = len(self.scopes)
                        lenSymbols = len(scope.symbols)

                        thisScopeCheck = self.scopes.index(scope) + 1
                        thisSymbolCheck = scope.symbols.index(symbol) + 1

                        idToTest = symbol.id

                        # this scope
                        if id == idToTest and scope.name > currentScope:
                            if symbol.init == True:
                                symbol.used = True
                                symbol.usedCount += 1

                                print("INFO SA - Var Declared and Initialized. Able to PRINT( "+ id + " )")

                            else:
                                print("WARNING SA - Uninitialized Variable. Unable to PRINT( "+ id + " )")
                            found = True
                        # previous scopes
                        elif id == idToTest and scope.name <= currentScope:
                            if symbol.init == True:
                                symbol.used = True
                                symbol.usedCount += 1
                                found = True
                                print("INFO SA - Var Declared and Initialized (Prev Scope). Able to PRINT( "+ id + " )")

                            else:
                                print("WARNING SA - Uninitialized Variable. (Prev Scope) Unable to PRINT( "+ id + " )")
                            found = True
                        # not found
                        elif id != idToTest and thisScopeCheck == lenScopes and thisSymbolCheck == lenSymbols and found == False:
                            print("ERROR SA - Undeclared Variable. Unable to PRINT( "+ id + " )")


            else: del AST[current]

    def parseChildrenComparability(self, cleanAST):
        AST = cleanAST.copy()
        current = 0
        while len(AST) != 0:

            match = re.match('(isEq)|(isNotEq)', AST[current][0])
            if match:
                currentScope = AST[current][1] - 1
                print(currentScope)
                # for scopes listt (index 0)
                # print + 1

                # delete isEq/isNotEq stmt
                del AST[current]

                print("Here")

                # this is the id they wish to print

                def getType(child):

                    for scope in self.scopes:

                        for symbol in scope.symbols:

                            lenScopes = len(self.scopes)
                            lenSymbols = len(scope.symbols)

                            thisScopeCheck = self.scopes.index(scope) + 1
                            thisSymbolCheck = scope.symbols.index(symbol) + 1

                            idToTest = symbol.id

                            # this scope
                            if child == idToTest and scope.name == currentScope:
                                print("INFO SA - Compare Check .. Var Declared and Initialized: " + child)
                                if symbol.init == True:
                                    symbol.used += 1
                                    symbol.isUsed = True
                                    return symbol.type
                                else:
                                    print("WARNING SA - Uninitialized Variable. Can't Compare: ( "+ child + " )")
                            elif child == idToTest and scope.name <= currentScope - 1:
                                print("INFO SA - Compare Check .. Var Declared and Initialized (Prev. Scope): " + child)
                                if symbol.init == True:
                                    symbol.used += 1
                                    symbol.isUsed = True
                                    return symbol.type
                                else:
                                    print("WARNING SA - Uninitialized Variable. Can't Compare: ( "+ child + " )")
                            # not found
                            elif child != idToTest and thisScopeCheck == lenScopes and thisSymbolCheck == lenSymbols:
                                print("ERROR SA - Undeclared Variable. Can't Compare:( "+ child + " )")


                child1 = AST[current][0]
                type1 = getType(child1)
                print(type1)

                del AST[current]

                child2 = AST[current][0]
                type2 = getType(child2)
                print(type2)

                if type1 == type2:
                     print("INFO SA - Compare Check PASS  " + str(type1) + " and " + str(type2))
                else:
                     print("ERROR SA - Compare Check FAIL  " + str(type1) + " and " + str(type2))

            else: del AST[current]
