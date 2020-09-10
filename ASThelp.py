import time

class Node:

    def __init__(self, name, kind):
        self.name = name
        self.parent = None
        self.kind = kind
        self.children = []

class Scope:

    def __init__(self, name):
        self.name = name
        self.symbolList = {}
        self.type = None

    def __str__(self):
        return str(self.name)

    def addType(self, type):
        self.type = type
        self.symbolList["type"] = [type]
        print(self.symbolList)

    def printInfo(self):
        print(self.symbolList)



class AST:

    def __init__(self, tokenStream):

        self.root = None
        self.current = None
        self.currentScope = -1
        self.symbolTable = []
        self.thisScope = None

        # create empty token steam to hold our tokens
        # self.tokenStream[0] is current token
        self.tokenStream = tokenStream

        # in case things go bad
        self.fail = False

    def setScopeFromPointer(self):

        self.thisScope = Scope(self.currentScope)
        print(self.thisScope)

    def addNode(self, name, kind):

        node = Node(name, kind)

        if self.root is None:
            self.root = node

        else:
            node.parent = self.current
            self.current.children.append(node)

        if (node.kind == "branch"):
            self.current = node

    def endChildren(self):
        if self.current.parent is not None:
            self.current = self.current.parent

    def toString(self):
        self.traversalResult = ""

        #recursive function to handle the expansion of nodes

        def expand(node, depth):
            for i in range(depth):
                self.traversalResult +=  " || "
            if node.children is None or len(node.children) == 0:
                self.traversalResult += " [" + node.name + "] "
                self.traversalResult += '\n'

            else:
                # if we are the root
                self.traversalResult += (" <" + node.name + "> " + '\n')
                for i in range(len(node.children)):
                    expand(node.children[i], depth + 1)

        expand(self.root, 0)

        return self.traversalResult

    def parseProgram(self):

        def reportFailure():
            print("Failed Parse")
            self.fail = True

        def parseStatementList():

            def parseType():

                if self.tokenStream[0].type is "TYPE_INT":
                    self.addNode(self.tokenStream[0].type, "leaf")
                    del self.tokenStream[0]
                elif self.tokenStream[0].type is "TYPE_STR":
                    self.addNode(self.tokenStream[0].type, "leaf")
                    del self.tokenStream[0]
                elif self.tokenStream[0].type is "TYPE_BOOL":
                    self.addNode(self.tokenStream[0].type, "leaf")
                    del self.tokenStream[0]


            def parseChar():


                self.addNode(self.tokenStream[0].value, "leaf")

                del self.tokenStream[0]

            def parseId():

                parseChar()

            def parseVarDecl():


                self.addNode("Var Decl", "branch")

                parseType()

                if self.tokenStream[0].type is not "CHAR":
                    print('ERROR Parse: Expecting char, got - ' + self.tokenStream[0].type + ' [ ' + self.tokenStream[0].value + ' ] found at [' + str(self.tokenStream[0].position) + ']')
                    del self.tokenStream[0]
                    reportFailure()
                else:
                    parseId()
                    self.endChildren()

            def parseExpr():

                def parseIntExpr():

                    def parseIntOp():

                        self.addNode(self.tokenStream[0].type, "branch")

                        self.addNode("+", "leaf")

                        del self.tokenStream[0]

                        self.endChildren()


                    def parseDigit():

                        self.addNode(self.tokenStream[0].value, "leaf")

                        del self.tokenStream[0]

                        while(self.tokenStream[0].type is "DIGIT"):
                            print('ERROR Parse: Double Digit Int - ' + self.tokenStream[0].type + ' [ ' + self.tokenStream[0].value + ' ] found at [' + str(self.tokenStream[0].position) + ']')
                            del self.tokenStream[0]

                    if self.tokenStream[0].type is "DIGIT" and self.tokenStream[1].type is not "PLUS_OP":
                        parseDigit()
                    elif self.tokenStream[0].type is "DIGIT" and self.tokenStream[1].type is "PLUS_OP":
                        parseDigit()
                        parseIntOp()
                        parseExpr()
                    else:
                        print("Something strange")

                    print(self.tokenStream[0])

                def parseBooleanExpr():

                    print("parseBooleanExpr()")

                    def parseBoolVal():
                        print("parseBoolVal()")

                        if self.tokenStream[0].type is "BOOL_EXP_FALSE":
                            self.addNode("False", "leaf")

                        elif self.tokenStream[0].type is "BOOL_EXP_TRUE":
                            self.addNode("True", "leaf")

                        del self.tokenStream[0]

                    def parseBoolOp():

                        if self.tokenStream[0].type is "BOOL_OP_EQUALS":
                            print("==")
                            self.addNode("==", "leaf")
                        elif self.tokenStream[0].type is "BOOL_OP_NOT_EQUALS":
                            print("!=")
                            self.addNode("!=", "leaf")
                        del self.tokenStream[0]

                    if self.tokenStream[0].type is "L_PAREN":

                        del self.tokenStream[0]
                        parseExpr()
                        parseBoolOp()
                        parseExpr()

                        if self.tokenStream[0].type is "R_PAREN":
                            del self.tokenStream[0]

                    elif self.tokenStream[0].type is "BOOL_OP_EQUALS" or "BOOL_OP_NOT_EQUALS":
                        parseBoolVal()

                def parseStringExpr():

                    def parseCharList():
                        self.addNode(self.tokenStream[0].value, "leaf")
                        del self.tokenStream[0]

                    parseCharList()

                if self.tokenStream[0].type is "DIGIT":
                    parseIntExpr()
                elif self.tokenStream[0].type is "CHAR" or self.tokenStream[0].type is "IDENTIFIER":
                    parseId()
                elif self.tokenStream[0].type is "BOOL_EXP_FALSE":
                    parseBooleanExpr()
                elif self.tokenStream[0].type is "BOOL_EXP_TRUE" or self.tokenStream[0].type is "BOOL_EXP_FALSE":
                    parseBooleanExpr()
                elif self.tokenStream[0].type is "L_PAREN":
                    parseBooleanExpr()
                elif self.tokenStream[0].type is "STRING_EXPR":
                    parseStringExpr()

                self.endChildren()

            def parseAssignmentStatement():

                print("parseAssignmentStatement")

                self.addNode("Assignment Statement", "branch")

                parseId()

                if self.tokenStream[0].type is "BOOL_OP_EQUALS":
                    print('ERROR Parse: Bool Statement Operator, You Need (parens) - ' + self.tokenStream[0].type + ' [ ' + self.tokenStream[0].value + ' ] found at [' + str(self.tokenStream[0].position) + ']')
                    del self.tokenStream[0]
                    reportFailure()

                del self.tokenStream[0]

                parseExpr()

            def parseWhileStatement():

                print("parseWhileStatement()")

                self.addNode("While Statement", "branch")

                del self.tokenStream[0]

                def parseBooleanExpr():

                    print("parseBooleanExpr()")

                    def parseBoolVal():
                        print("parseBoolVal()")

                        if self.tokenStream[0].type is "BOOL_EXP_FALSE":
                            self.addNode("False", "leaf")

                        elif self.tokenStream[0].type is "BOOL_EXP_TRUE":
                            self.addNode("True", "leaf")

                        del self.tokenStream[0]

                        if self.tokenStream[0].type is "R_PAREN":
                            del self.tokenStream[0]

                    def parseBoolOp():
                        del self.tokenStream[0]

                    firstExp = self.tokenStream[1]

                    del self.tokenStream[0]

                    if self.tokenStream[0].type is not "BOOL_EXP_TRUE" and self.tokenStream[0].type is not "BOOL_EXP_FALSE":

                        del self.tokenStream[0]

                        print("This", self.tokenStream[0])

                        if self.tokenStream[0].type is "BOOL_OP_EQUALS":
                            print("==")
                            self.addNode("isEq", "branch")
                            self.addNode(firstExp.value, "leaf")
                            del self.tokenStream[0]
                            self.addNode(self.tokenStream[0].value, "leaf")

                            self.endChildren()

                        elif self.tokenStream[0].type is "BOOL_OP_NOT_EQUALS":
                            print("!=")
                            self.addNode("isNotEq", "branch")
                            self.addNode(firstExp.value, "leaf")
                            self.addNode(self.tokenStream[1].value, "leaf")
                            self.endChildren()

                        self.tokenStream.insert(0, firstExp)

                        del self.tokenStream[0]
                        del self.tokenStream[0]
                        del self.tokenStream[0]

                        if self.tokenStream[0].type is "R_PAREN":
                            del self.tokenStream[0]
                    else:
                        parseBoolVal()


                parseBooleanExpr()

                parseBlock()

                self.endChildren()


            def parseIfStatement():

                self.addNode("If Statement", "branch")

                del self.tokenStream[0]

                def parseBooleanExpr():

                    def parseBoolVal():

                        if self.tokenStream[0].type is "BOOL_EXP_FALSE":
                            self.addNode("False", "leaf")

                        elif self.tokenStream[0].type is "BOOL_EXP_TRUE":
                            self.addNode("True", "leaf")

                        del self.tokenStream[0]

                        if self.tokenStream[0].type is "R_PAREN":
                            del self.tokenStream[0]

                    def parseBoolOp():
                        del self.tokenStream[0]

                    firstExp = self.tokenStream[1]

                    del self.tokenStream[0]

                    print("first", firstExp)


                    if self.tokenStream[0].type is not "BOOL_EXP_TRUE" and self.tokenStream[0].type is not "BOOL_EXP_FALSE":

                        del self.tokenStream[0]

                        print("This", self.tokenStream[0])

                        if self.tokenStream[0].type is "BOOL_OP_EQUALS":
                            print("==")
                            self.addNode("isEq", "branch")
                            self.addNode(firstExp.value, "leaf")
                            del self.tokenStream[0]
                            self.addNode(self.tokenStream[0].value, "leaf")

                            self.endChildren()

                        elif self.tokenStream[0].type is "BOOL_OP_NOT_EQUALS":
                            print("!=")
                            self.addNode("isNotEq", "branch")
                            self.addNode(firstExp.value, "leaf")
                            self.addNode(self.tokenStream[1].value, "leaf")
                            self.endChildren()

                        self.tokenStream.insert(0, firstExp)

                        del self.tokenStream[0]
                        del self.tokenStream[0]
                        del self.tokenStream[0]

                        if self.tokenStream[0].type is "R_PAREN":
                            del self.tokenStream[0]
                    else:
                        parseBoolVal()

                parseBooleanExpr()

                parseBlock()

                self.endChildren()

            def parsePrintStatement():


                self.addNode("Print Statement", "branch")

                del self.tokenStream[0]

                parseExpr()

            def parseStatement():

                if (self.tokenStream[0].type is "TYPE_INT"
                or self.tokenStream[0].type is "TYPE_STR"
                or self.tokenStream[0].type is "TYPE_BOOL"):
                    if len(self.tokenStream) > 1:
                        parseVarDecl()
                elif (self.tokenStream[0].type is "CHAR" and self.tokenStream[1].type is "ASSIGN_OP"):
                    if len(self.tokenStream) > 1:
                        parseAssignmentStatement()
                elif self.tokenStream[0].type is "BOOL_EXP_WHILE":
                    if len(self.tokenStream) > 1:
                        parseWhileStatement()
                elif self.tokenStream[0].type is "BOOL_EXP_IF":
                    if len(self.tokenStream) > 1:
                        parseIfStatement()
                elif self.tokenStream[0].type is "PRINT_STMT":
                    if len(self.tokenStream) > 1:
                        del self.tokenStream[0]
                        parsePrintStatement()
                        del self.tokenStream[0]
                elif self.tokenStream[0].type is "R_BRACE":
                    pass
                elif self.tokenStream[0].type is "L_BRACE":
                    parseBlock()
                elif self.tokenStream[0].type is "STRING_EXPR":
                    print('ERROR Parse: Unassigned String - ' + self.tokenStream[0].type + ' [ ' + self.tokenStream[0].value + ' ] found at [' + str(self.tokenStream[0].position) + ']')
                    del self.tokenStream[0]
                    reportFailure()
                elif self.tokenStream[0].type is "CHAR":
                    print('ERROR Parse: Unassigned CHAR - ' + self.tokenStream[0].type + ' [ ' + self.tokenStream[0].value + ' ] found at [' + str(self.tokenStream[0].position) + ']')
                    del self.tokenStream[0]
                    reportFailure()
                else:
                    reportFailure()
                    del self.tokenStream
                    print("Somthing strange happened :/")
                    pass

            parseStatement()

            if self.tokenStream[0].type is "R_BRACE":
                del self.tokenStream[0]
                #self.endChildren()
            elif self.tokenStream[0].type is not "EOP":
                print(self.tokenStream[0])
                parseStatementList()
                #self.endChildren()
            elif self.tokenStream[0].type is "EOP":
                parseEOF()

        def parseBlock():

            self.addNode("Block", "branch")

            if self.tokenStream[0].type == "L_BRACE":
                del self.tokenStream[0]
                parseStatementList()
            else:
                print("PARSE FAIL: Was expecting closing brace [ } ] got " + "[ " + str(self.tokenStream[0].type) + ", ", str(self.tokenStream[0].value) + " ]")
                reportFailure()

            self.endChildren()

        def parseEOF():

            if self.tokenStream[0].type == "EOP":
                print("Finished Parse")
            else:
                print("PARSE FAIL: Was expecting closing EOF [ $ ] got " + "[ " + str(self.tokenStream[0].type) + ", ", str(self.tokenStream[0].value) + " ]")
                reportFailure()

        parseBlock()

        parseEOF()




        #end parseProgram()
