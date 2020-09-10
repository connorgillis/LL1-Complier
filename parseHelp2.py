import time

class Node:

    def __init__(self, name, kind):
        self.name = name
        self.parent = None
        self.kind = kind
        self.children = []

class ParseTree:

    def __init__(self, tokenStream):

        self.root = None
        self.current = None

        # create empty token steam to hold our tokens
        # self.tokenStream[0] is current token
        self.tokenStream = tokenStream

        # in case things go bad
        self.fail = False


        print("Tokens to parse [type, value]:")

        for token in tokenStream:
            print("[ " + str(token.type) + ", ", str(token.value) + " ]")



    def addNode(self, name, kind):

        node = Node(name, kind)

        if self.root is None:
            self.root = node
            print("We are the root")

        else:
            #we are not the parent, we are the children
            node.parent = self.current
            self.current.children.append(node)

        if (node.kind == "branch"):
            self.current = node

    def endChildren(self):
        # going up
        if self.current.parent is not None:
            self.current = self.current.parent
        #else:
            #print("Something weird")
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



        print("parseProgram()")
        self.addNode("Program", "branch")

        def parseStatementList():

            print("parseStatementList()")
            self.addNode("Statement List", "branch")

            def parseType():

                print("parseType()")
                self.addNode("Type", "branch")

                if self.tokenStream[0].type is "TYPE_INT":
                    self.addNode(self.tokenStream[0].type, "leaf")
                    del self.tokenStream[0]
                elif self.tokenStream[0].type is "TYPE_STR":
                    self.addNode(self.tokenStream[0].type, "leaf")
                    del self.tokenStream[0]
                elif self.tokenStream[0].type is "TYPE_BOOL":
                    self.addNode(self.tokenStream[0].type, "leaf")
                    del self.tokenStream[0]

                #end parseType()
                self.endChildren()

            def parseChar():

                print("parseChar()")

                self.addNode(self.tokenStream[0].value, "leaf")

                del self.tokenStream[0]

                #end parseChar()
                self.endChildren()

            def parseId():

                print("parseId()")

                self.addNode("ID", "branch")

                parseChar()

            def parseVarDecl():

                print("parseVarDecl")

                self.addNode("Var Decl", "branch")


                # VarDecl => [type] [Id]
                parseType()

                if self.tokenStream[0].type is not "CHAR":
                    print('ERROR Parse: Expecting char, got - ' + self.tokenStream[0].type + ' [ ' + self.tokenStream[0].value + ' ] found at [' + str(self.tokenStream[0].position) + ']')
                    del self.tokenStream[0]
                    reportFailure()
                else:
                    parseId()

                #end parseVarDecl()
                self.endChildren()

            def parseExpr():

                print("parseExpr()")

                self.addNode("Expression", "branch")

                def parseIntExpr():

                    print("parseIntExpr()")

                    self.addNode("Int Expr", "branch")

                    def parseIntOp():

                        print("parseIntOp()")

                        self.addNode(self.tokenStream[0].type, "branch")

                        self.addNode("+", "leaf")

                        del self.tokenStream[0]

                        self.endChildren()


                    def parseDigit():

                        print("parseDigit()")

                        self.addNode(self.tokenStream[0].type, "branch")

                        self.addNode(self.tokenStream[0].value, "leaf")

                        del self.tokenStream[0]

                        while(self.tokenStream[0].type is "DIGIT"):
                            print('ERROR Parse: Double Digit Int - ' + self.tokenStream[0].type + ' [ ' + self.tokenStream[0].value + ' ] found at [' + str(self.tokenStream[0].position) + ']')
                            del self.tokenStream[0]


                        self.endChildren()


                    print("doing this routine")
                    #print(self.tokenStream[0])
                    #parseDigit()
                    #print(self.tokenStream[0])
                    #parseIntOp()
                    #print(self.tokenStream[0])

                    if self.tokenStream[0].type is "DIGIT" and self.tokenStream[1].type is not "PLUS_OP":
                        parseDigit()
                    elif self.tokenStream[0].type is "DIGIT" and self.tokenStream[1].type is "PLUS_OP":
                        parseDigit()
                        parseIntOp()
                        parseExpr()
                    else:
                        print("Something strange")


                    print(self.tokenStream[0])

                    self.endChildren()

                def parseBooleanExpr():

                    print("parseBooleanExpr()")

                    self.addNode("BooleanExpr", "branch")

                    def parseBoolVal():
                        print("parseBoolVal()")

                        self.addNode("BoolVal", "branch")

                        if self.tokenStream[0].type is "BOOL_EXP_FALSE":
                            self.addNode("False", "leaf")
                            self.endChildren()

                        elif self.tokenStream[0].type is "BOOL_EXP_TRUE":
                            self.addNode("True", "leaf")
                            self.endChildren()

                        del self.tokenStream[0]


                    def parseBoolOp():
                        self.addNode("BoolOp", "branch")

                        if self.tokenStream[0].type is "BOOL_OP_EQUALS":
                            print("==")
                            self.addNode("==", "leaf")
                        elif self.tokenStream[0].type is "BOOL_OP_NOT_EQUALS":
                            print("!=")
                            self.addNode("!=", "leaf")
                        del self.tokenStream[0]
                        self.endChildren()

                    if self.tokenStream[0].type is "L_PAREN":

                        del self.tokenStream[0]
                        parseExpr()
                        parseBoolOp()
                        parseExpr()

                        if self.tokenStream[0].type is "R_PAREN":
                            del self.tokenStream[0]

                    elif self.tokenStream[0].type is "BOOL_OP_EQUALS" or "BOOL_OP_NOT_EQUALS":
                        parseBoolVal()

                    self.endChildren()

                def parseStringExpr():

                    def parseCharList():
                        self.addNode(self.tokenStream[0].value, "leaf")
                        del self.tokenStream[0]

                    print("parseStingExpr()")
                    self.addNode("STRING_EXPR", "branch")
                    parseCharList()

                    #end parseStringExpr
                    self.endChildren()

                if self.tokenStream[0].type is "DIGIT":
                    parseIntExpr()
                elif self.tokenStream[0].type is "CHAR" or self.tokenStream[0].type is "IDENTIFIER":
                    parseId()
                elif self.tokenStream[0].type is "BOOL_EXP_FALSE":
                    parseBooleanExpr()
                # elif self.tokenStream[1].type is "==":
                #     parseBooleanExpr()
                elif self.tokenStream[0].type is "BOOL_EXP_TRUE" or self.tokenStream[0].type is "BOOL_EXP_FALSE":
                    parseBooleanExpr()
                elif self.tokenStream[0].type is "L_PAREN":
                    parseBooleanExpr()
                elif self.tokenStream[0].type is "STRING_EXPR":
                    parseStringExpr()

                #end parseExpr()
                self.endChildren()



            def parseAssignmentStatement():

                print("parseAssignmentStatement")

                self.addNode("Assignment Statement", "branch")

                parseId()

                if self.tokenStream[0].type is "BOOL_OP_EQUALS":
                    print('ERROR Parse: Bool Statement Operator, You Need (parens) - ' + self.tokenStream[0].type + ' [ ' + self.tokenStream[0].value + ' ] found at [' + str(self.tokenStream[0].position) + ']')
                    del self.tokenStream[0]
                    reportFailure()

                # =

                self.addNode("=", "leaf")
                del self.tokenStream[0]



                parseExpr()

                self.endChildren()


            def parseWhileStatement():

                print("parseWhileStatement()")

                self.addNode("While Statement", "branch")

                del self.tokenStream[0]

                def parseBooleanExpr():

                    print("parseBooleanExpr()")

                    self.addNode("BooleanExpr", "branch")

                    def parseBoolVal():
                        print("parseBoolVal()")

                        self.addNode("BoolVal", "branch")

                        if self.tokenStream[0].type is "BOOL_EXP_FALSE":
                            self.addNode("False", "leaf")
                            self.endChildren()

                        elif self.tokenStream[0].type is "BOOL_EXP_TRUE":
                            self.addNode("True", "leaf")
                            self.endChildren()

                        del self.tokenStream[0]


                    def parseBoolOp():
                        self.addNode("BoolOp", "branch")

                        if self.tokenStream[0].type is "BOOL_OP_EQUALS":
                            print("==")
                            self.addNode("==", "leaf")
                        elif self.tokenStream[0].type is "BOOL_OP_NOT_EQUALS":
                            print("!=")
                            self.addNode("!=", "leaf")
                        del self.tokenStream[0]
                        self.endChildren()

                    if self.tokenStream[0].type is "L_PAREN":

                        del self.tokenStream[0]
                        parseExpr()
                        parseBoolOp()
                        parseExpr()

                        if self.tokenStream[0].type is "R_PAREN":
                            del self.tokenStream[0]

                    elif self.tokenStream[0].type is "BOOL_OP_EQUALS" or "BOOL_OP_NOT_EQUALS":
                        parseBoolVal()

                    self.endChildren()

                parseBooleanExpr()

                parseBlock()

                self.endChildren()


            def parseIfStatement():

                print("parseIfStatement()")

                self.addNode("If Statement", "branch")

                del self.tokenStream[0]

                def parseBooleanExpr():

                    print("parseBooleanExpr()")

                    self.addNode("BooleanExpr", "branch")

                    def parseBoolVal():
                        print("parseBoolVal()")

                        self.addNode("BoolVal", "branch")

                        if self.tokenStream[0].type is "BOOL_EXP_FALSE":
                            self.addNode("False", "leaf")
                            self.endChildren()

                        elif self.tokenStream[0].type is "BOOL_EXP_TRUE":
                            self.addNode("True", "leaf")
                            self.endChildren()

                        del self.tokenStream[0]


                    def parseBoolOp():
                        self.addNode("BoolOp", "branch")

                        if self.tokenStream[0].type is "BOOL_OP_EQUALS":
                            print("==")
                            self.addNode("==", "leaf")
                        elif self.tokenStream[0].type is "BOOL_OP_NOT_EQUALS":
                            print("!=")
                            self.addNode("!=", "leaf")
                        del self.tokenStream[0]
                        self.endChildren()

                    if self.tokenStream[0].type is "L_PAREN":

                        del self.tokenStream[0]
                        parseExpr()
                        parseBoolOp()
                        parseExpr()

                        if self.tokenStream[0].type is "R_PAREN":
                            del self.tokenStream[0]

                    elif self.tokenStream[0].type is "BOOL_OP_EQUALS" or "BOOL_OP_NOT_EQUALS":
                        parseBoolVal()

                    self.endChildren()

                parseBooleanExpr()

                parseBlock()

                self.endChildren()


            def parsePrintStatement():

                print("parsePrintStatement()")

                self.addNode("Print Statement", "branch")

                del self.tokenStream[0]

                parseExpr()

                self.endChildren()


            def parseStatement():

                print("parseStatement()")

                self.addNode("Statement", "branch")

                if (self.tokenStream[0].type is "TYPE_INT"
                or self.tokenStream[0].type is "TYPE_STR"
                or self.tokenStream[0].type is "TYPE_BOOL"):
                    if len(self.tokenStream) > 1:
                        print("Begin Var Declr")
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

                self.endChildren()



            parseStatement()

            if self.tokenStream[0].type is "R_BRACE":
                del self.tokenStream[0]
                self.endChildren()
            elif self.tokenStream[0].type is not "EOP":
                print(self.tokenStream[0])
                parseStatementList()
                self.endChildren()
            elif self.tokenStream[0].type is "EOP":
                parseEOF()

        def parseBlock():

            print("parseBlock()")

            self.addNode("Block", "branch")



            if self.tokenStream[0].type == "L_BRACE":
                self.addNode("{", "leaf")
                del self.tokenStream[0]
                parseStatementList()
                self.addNode("}", "leaf")


            elif self.tokenStream[0].type is "R_BRACE":
                self.addNode("}", "leaf")

            else:

                print("PARSE FAIL: Was expecting closing brace [ } ] got " + "[ " + str(self.tokenStream[0].type) + ", ", str(self.tokenStream[0].value) + " ]")
                reportFailure()

            self.endChildren()

        def parseEOF():

            print("parseEOF()")

            self.addNode("$", "leaf")
            if self.tokenStream[0].type == "EOP":
                print("Finished Parse")
            else:

                print("PARSE FAIL: Was expecting closing EOF [ $ ] got " + "[ " + str(self.tokenStream[0].type) + ", ", str(self.tokenStream[0].value) + " ]")
                reportFailure()
            self.endChildren()

        parseBlock()
        parseEOF()

        #end parseProgram()
        self.endChildren()
