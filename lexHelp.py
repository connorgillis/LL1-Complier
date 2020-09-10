import re

class Token(object):

    # creating a token obj to store retrived token data
    # tokens need to contain attrib for type, valuee, and posistion

    def __init__(self, type, value, position):
        self.type = type
        self.value = value
        self.position = position


    def __str__(self):
        return 'DEBUG Lexer - ' + self.type + ' [ ' + self.value + ' ] found at [' + str(self.position) + ']'

class Lexer(object):

    def __init__(self, grammer):

        # a place for a grammer dict, containing expressions and corresponding types
        self.grammer = []

        # a place for tokens to stay
        self.tokensOut = []

        self.tokenStream = []

        self.fail = False

        # for each of the (expression, type) pairs in grammer, we need to compile
        #   the pattern into a regex obj
        for expression, type in grammer:

            self.grammer.append((re.compile(expression), type))

    # method to load the input into the buffer, start value for position 'pointer'
    def load(self, inputBuffer):
        self.inputBuffer = inputBuffer
        self.position = 0

    # we need a method to work through the input buffer, returning tokens and
    # posistion as they're matched to a specific regex object group
    def token(self):

        # tokenize method needs to know when we're at the end of the inputBuffer
        #   time to stop ..
        if self.position >= len(self.inputBuffer):
            return None


        #whitespace
        match = re.compile('\S').search(self.inputBuffer, self.position)

        #print(match)

        if match:
            self.position = match.start()
        else:
            return None

        # run through the grammer
        for expression, type in self.grammer:

            # match the pattern of the current expression in the grammer
            #   with the current inputBuffer

            match = expression.match(self.inputBuffer, self.position)

            if match:
                token = Token(type, match.group(), self.position)
                # update position to the end of the current match and return the
                #   token
                self.position = match.end()
                return token

        if match is None:
            # there was an error in the input buffer
            # the error occured somewhere btwn self.position and
            # the end of the input inputBuffer
            # self.postion in this case is match.end() of previous token
            print("ERROR Lexer - Lex error in this program ")
            print("ERROR LEXER - Error begins at " + str(self.position))
            buffer = self.inputBuffer[self.position:]
            print("ERROR LEXER - input <<< " + buffer + " >>> did not match any patterns")
            self.fail = True
            return None

    def tokenize(self):

        while True:
            token = self.token()
            if token is None:
                break
            self.tokensOut.append(token)

    def printTokens(self):

            # do not add the EOP into tokenStream, but it signals to return
            for line in self.tokensOut:
                if line.type == "EOP":
                    self.tokenStream.append(line)
                    return self.tokenStream
                if line.type is not "COMMENT":
                    self.tokenStream.append(line)
            # and if somthing weird happens..
            return self.tokenStream
