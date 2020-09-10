from lexHelp import Token, Lexer
from ASThelp import AST, Scope
from SAhelp2 import Semantic
from parseHelp2 import ParseTree
from CodeGenHelp import CodeGenerator
import sys
import time

grammer = [
    ('\$', 'EOP'),
    ('if', 'BOOL_EXP_IF'),
    ('int', 'TYPE_INT'),
    ('string', 'TYPE_STR'),
    ('boolean', 'TYPE_BOOL'),
    ('print', 'PRINT_STMT'),
    ('while', 'BOOL_EXP_WHILE'),
    ('true', 'BOOL_EXP_TRUE'),
    ('false', 'BOOL_EXP_FALSE'),
    ##('[a-z]\w+','IDENTIFIER'),
    ('/\\*.*?\\*/', 'COMMENT'),
    ('/\*', 'BEGIN_COMMENT'),
    ('\*/', 'END_COMMENT'),
    ('\{', 'L_BRACE'),
    ('\}', 'R_BRACE'),
    ('\(', 'L_PAREN'),
    ('\)', 'R_PAREN'),
    ('\+', 'PLUS_OP'),
    ('==', 'BOOL_OP_EQUALS'),
    ('!=', 'BOOL_OP_NOT_EQUALS'),
    ('=', 'ASSIGN_OP'),
    ('(\d)+?', 'DIGIT'),
    ('(\"(.*?)\")', 'STRING_EXPR'),
    ('[a-z]?','CHAR')
]

try:
    print('\n')
    print("Looking for your code at, " + str(sys.argv[1]))
except IndexError:
    print("Provide file path arg")

print("INFO Lexer - Lexing Program")
fileName = str(sys.argv[1])
f = open(fileName, 'r', encoding = 'utf-8')

# create empty list for lines of the file
lineArray = []

# run through the lines, strip new lines
for line in f:
    justLine = line.rstrip('\n')
    lineArray.append(justLine)
f.close()

# bring all the lines together (multiple programs, delim'd by $)
lines = "".join(lineArray)

# split on the EOP, these are programs
programs = lines.split('$')


#create a list of 'cleaned programs'
cleanedPrograms = []

# give the EOP token back to the list of lines, it was removed in .split() ...
# we now have cleaned programs, seperate, but retaining EOP tok

for program in programs:
    cleaned = program + "$"
    cleanedPrograms.append(cleaned)


# grab last program, it's a blank $, remove

last = len(cleanedPrograms)
del cleanedPrograms[last - 1]

for i, program in enumerate(cleanedPrograms):
    lex = Lexer(grammer)
    print("INFO Lexer - Lexing Program " + str(i + 1))
    lex.load(program)
    lex.tokenize()
    tokenStream = lex.printTokens()
    astStream = tokenStream.copy()

    for token in tokenStream:
        print(str(token))

    if lex.fail is False:
        print("INFO Lex - Succesful Lex")
        parse = ParseTree(tokenStream)
        parse.parseProgram()


        if parse.fail is False:
            print('\n')
            traversalResult = parse.toString()
            print(traversalResult)

        else: print("INFO Parse - This parse failed, NO CST")
    else:
        print("ERROR Lex - Unsuccessful, Won't Parse")


    ast = AST(astStream)
    ast.parseProgram()
    result = ast.toString()
    print(result)


    semantic = Semantic(ast)
    result = semantic.toString()
    print(result)

    cleanAST = semantic.cleanAST(result)

    for node in cleanAST:
        print(node)

    print('\n')

    semantic.createScopeAreas(cleanAST)

    semantic.parseSymbols(cleanAST)

    semantic.parseAssign(cleanAST)

    semantic.parsePrintStatement(cleanAST)

    semantic.parseChildrenComparability(cleanAST)

    semantic.printScopeAreas()

    codeGenerator = CodeGenerator(cleanAST)

    codeGenerator.processAndPrintAST()

    codeGenerator.createExecutionEnviornmnet()

    codeGenerator.generateCode()

    codeGenerator.printExecutionEnviornmnet()

    codeGenerator.printEnv()




    # for i, scope in enumerate(symbolTable):
    #     print("Scope", i)
    #     for x, y in scope.items():
    #         print(x, y)
    # print('\n')
