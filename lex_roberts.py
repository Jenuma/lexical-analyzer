#=============================================================================|
# Clifton Roberts                                                             |
# CSC-333 Program Language Theory                                             |
# Programming Assignment - Python                                             |
# Fall 2014                                                                   |
#=============================================================================|
# Imported Modules
import sys  # For grabbing command line arguments.
import os   # For checking if the file exists.
#=============================================================================|
# inject                                                                      |
#-----------------------------------------------------------------------------|
# Injects a string into another string at a certain position.                 |
# @param string The string that is being altered.                             |
# @param injection The string to be injected.                                 |
# @param pos The position at which the injection should take place.           |
#=============================================================================|
def inject(string, injection, pos):
    return string[:pos] + injection + string[pos:]
#=============================================================================|
# is_numeric                                                                  |
#-----------------------------------------------------------------------------|
# Checks to see if a string is numeric or not. I have done my best to make it |
# conform to Java's multiple types of number literals, including binary and   |
# hex literals, exponentials, and float/long specifiers.                      |
# @param string The string being checked.                                     |
# @return True if the string is numeric, False otherwise.                     |
#=============================================================================|
def is_numeric(string):
    # Float and long specifiers should be at the end.
    if 'f' in string:
        if string.index('f') != len(string)-1: return False
    if 'l' in string:
        if string.index('l') != len(string)-1: return False
    
    # Positions of binary and hex literal specifiers are incorrect.
    if 'b' in string:
        if string.index('b') != 1: return False
        if '0' in string:
            if string.index('b') == 1 and string.index('0') != 0:
                return False
    elif 'x' in string:
        if string.index('x') != 1: return False
        if '0' in string:
            if string.index('x') == 1 and string.index('0') != 0:
                return False
            
    # Exponential should be between numbers.
    if 'e' in string:
        if string.index('e') == 0 or string.index('e') == len(string)-1:
            return False;
    
    # Impossible combination of specifiers.
    if 'f' in string and 'l' in string: return False
    if 'b' in string and 'h' in string: return False
    
    # Impossible combination of parity operators.
    if '+' in string and '-' in string: return False
    
    decimals_count = 0
    exponential_count = 0
    parity_count = 0
    binary_count = 0
    hex_count = 0
    float_count = 0
    long_count = 0
    number_count = 0
    
    for char in string:
        # Contains illegal characters.
        if char not in '0123456789beflx+-.': return False
        else:
            if char == '.': decimals_count += 1
            elif char == 'e': exponential_count += 1
            elif char in '+-': parity_count += 1
            elif char == 'b': binary_count += 1
            elif char == 'x': hex_count += 1
            elif char == 'f': float_count += 1
            elif char == 'l': long_count += 1
            elif char in '0123456879': number_count += 1
        # Contains too many decimals, exponentials, or parity operators.
        if decimals_count > 1 or exponential_count > 1 or parity_count > 1:
            return False
        # Contains too many binary or hex literal specifiers.
        elif binary_count > 1 or hex_count > 1:
            return False
        # Contains too many float or long literal specifiers.
        elif float_count > 1 or long_count > 1:
            return False
        # There needs to be at least one number.
        elif number_count < 1:
            return False
    return True
#=============================================================================|
# remove_tabs                                                                 |
#-----------------------------------------------------------------------------|
# Removes all tab characters from a list of strings.                          |
# @param oldlist The list of strings with tab characters to be removed.       |
# @return The new list with all tab characters removed.                       |
#=============================================================================|
def remove_tabs(oldlist):
    newlist = []
    for line in oldlist:
        line = line.replace('\t', '')
        newlist.append(line)
    return newlist
#=============================================================================|
# remove_empty_strings                                                        |
#-----------------------------------------------------------------------------|
# Removes all empty elements from a list of strings.                          |
# @param oldlist The list of strings with empty elements to be removed.       |
# @return The new list with all empty elements removed.                       |
#=============================================================================|
def remove_empty_strings(oldlist):
    newlist = []
    for line in oldlist:
        if line == '' or line == '\n':
            continue
        newlist.append(line)
    return newlist
#=============================================================================|
# remove_comments                                                             |
#-----------------------------------------------------------------------------|
# Removes all the comments from the source.                                   |
# @param oldlist The list of strings with comments to be removed.             |
# @return The new list with all comments removed.                             |
#=============================================================================|
def remove_comments(oldlist):
    newlist = []
    
    # Flag for indicating whether a block comment is being removed.
    # If /* or /** is found, we know a block comment is beginning.
    # No lines should be appended until */ is found.
    removing_block_flag = False
    
    for line in oldlist:
        if not removing_block_flag:
            # Block comment detected. Start removing.
            if '/*' in line:
                removing_block_flag = True
                continue
            # Line comment at the beginning of the line detected.
            elif line[0:2] == "//":
                continue
            # Line comment somewhere in the line.
            elif '//' in line:
                index = line.index('//')
                newlist.append(line[:index])
            # No comments detected.
            else:
                newlist.append(line)
        else:
            # End of block comment detected. Start reading lines again.
            if '*/' in line:
                removing_block_flag = False
                continue
    
    return newlist
#=============================================================================|
# separate_tokens                                                             |
#-----------------------------------------------------------------------------|
# Separates certain tokens from others. This makes for easier analyzing at    |
# the chunk level later.                                                      |
# @param oldlist The list of strings to be manipulated.                       |
# @return The new list of strings, more pleasantly organized.                 |
#=============================================================================|
def separate_tokens(oldlist):
    newlist = []
    for line in oldlist:
        # The character is the only one in the line.
        if len(line) == 1:
            newlist.append(line)
            continue
        
        # Index of the current character.
        index = 0
        
        # Flag indicating open quotations.
        # If its closed, separate the symbols. Otherwise, they're part of
        # the string.
        flag = False
        
        # Iterate over each character.
        for char in line:
            # Toggle the flag if a " is scanned.
            if char == '\"': flag = not flag
                
            if char in ';()=+-/*<>!{}[]|&' and flag == False:
                # The character is the first in the line. [Insert After]
                if index == 0:
                    # Check for compound operators.
                    # These don't need to be separated.
                    if char in '<>=!' and line[index+1] == '=':
                        index += 1
                        continue
                    elif char == '|' and line[index+1] == '|':
                        index += 1
                        continue
                    elif char == '&' and line[index+1] == '&':
                        index += 1
                        continue
                    if line[index+1] != ' ':
                        line = inject(line, ' ', index+1)
                        # Adjust index for the newly injected character.
                        index += 1
                # The character is the last in the line. [Insert Before]
                elif index == len(line)-1:
                    # Check for compound operators.
                    # These don't need to be separated.
                    if char == '=' and line[index-1] in '<>=!':
                        index += 1
                        continue
                    elif char == '|' and line[index-1] == '|':
                        index += 1
                        continue
                    elif char == '&' and line[index-1] == '&':
                        index += 1
                        continue
                    if line[index-1] != ' ':
                        line = inject(line, ' ', index)
                        # Adjust index for the newly injected character.
                        index += 1
                # The character is in the middle of the line. [Insert Both]
                else:
                    # Check for compound operators.
                    # These don't need to be separated.
                    if char in '<>=!' and line[index+1] == '=':
                        index += 1
                        continue
                    elif char == '=' and line[index-1] in '<>=!':
                        index += 1
                        continue
                    elif char == '|' and line[index+1] == '|':
                        index += 1
                        continue
                    elif char == '|' and line[index-1] == "|":
                        index += 1
                        continue
                    elif char == '&' and line[index+1] == '&':
                        index += 1
                        continue
                    elif char == '&' and line[index-1] == '&':
                        index += 1
                        continue
                    if line[index-1] != ' ':
                        line = inject(line, ' ', index)
                        # Adjust index for the newly injected character.
                        index += 1
                    if line[index+1] != ' ':
                        line = inject(line, ' ', index+1)
                        # Adjust index for the newly injected character.
                        index += 1
            index += 1
        newlist.append(line)
    return newlist
#=============================================================================|
# main                                                                        |
#-----------------------------------------------------------------------------|
# Where program flow begins.                                                  |
# @param filename This is the name of the text file to be analyzed via        |
#                 command line argument.                                      |
#=============================================================================|
def main(filename):
    # Make sure the file exists.
    if not os.path.isfile(filename):
        print(filename + ' does not exist.')
        sys.exit()
    
    # Open the file.
    file = open(filename, 'r')
    lines = file.read().split('\n')
    
    # Print out the table's header.
    print("--------------------------------------")
    print("Token\t\t\t\tLexeme")
    print("--------------------------------------")
    
    # Remove tab characters, empty elements and comments.
    lines = remove_tabs(lines)
    lines = remove_empty_strings(lines)
    lines = remove_comments(lines)
    
    # Put space between certain operators.
    lines = separate_tokens(lines)
    
    # For each line of the source...
    for line in lines:
        # Divide the line into "chunks" separated by spaces.
        chunks = line.split()
        
        # Flag indicating open quotations.
        # If its closed, the chunk is not in a string. Otherwise it is.
        flag = False
        astring = ''
        
        # For each chunk in the line...
        for chunk in chunks:
            # STRING_CONSTANT
            # Flag is open so we're in a string. Add the chunk and continue.
            if flag and '\"' not in chunk:
                astring += chunk + ' '
                continue
            # Flag is open but there is a " in the chunk, so it's the end.
            # Add the string, print it, and reset the string related variables.
            elif flag and '\"' in chunk:
                astring += chunk
                print('STRING_CONSTANT\t\t\t' + astring)
                astring = ''
                flag = not flag
            # The flag is closed but there is a " in the chunk, so it's the
            # beginning of a string. Add it and toggle the flag.
            elif not flag and '\"' in chunk:
                astring += chunk + ' '
                flag = not flag
            # CHARACTER_CONSTANT
            elif chunk[0] == '\'' and chunk[len(chunk)-1] == '\'':
                print('CHARACTER_CONSTANT\t\t' + chunk)
            # INT_LITERAL
            elif is_numeric(chunk) and '.' not in chunk and 'f' not in chunk:
                print('INT_LITERAL\t\t\t' + chunk)
            # REAL_LITERAL
            elif is_numeric(chunk) and '.' in chunk:
                print('REAL_LITERAL\t\t\t' + chunk)
            # SEMICOLON
            elif chunk == ';': print('SEMICOLON\t\t\t' + chunk)
            # LEFT_PARENTHESIS
            elif chunk == '(': print('LEFT_PARENTHESIS\t\t' + chunk)
            # RIGHT_PARENTHESIS
            elif chunk == ')': print('RIGHT_PARENTHESIS\t\t' + chunk)
            # ASSIGN_OP
            elif chunk == '=': print('ASSIGN_OP\t\t\t' + chunk)
            # ADD_OP
            elif chunk == '+': print('ADD_OP\t\t\t\t' + chunk)
            # SUB_OP
            elif chunk == '-': print('SUB_OP\t\t\t\t' + chunk)
            # DIV_OP
            elif chunk == '/': print('DIV_OP\t\t\t\t' + chunk)
            # MUL_OP
            elif chunk == '*': print('MUL_OP\t\t\t\t' + chunk)
            # LT_OP
            elif chunk == '<': print('LT_OP\t\t\t\t' + chunk)
            # GT_OP
            elif chunk == '>': print('GT_OP\t\t\t\t' + chunk)
            # LTE_OP
            elif chunk == '<=': print('LTE_OP\t\t\t\t' + chunk)
            # GTE_OP
            elif chunk == '>=': print('GTE_OP\t\t\t\t' + chunk)
            # EQ_OP
            elif chunk == '==': print('EQ_OP\t\t\t\t' + chunk)
            # NEQ_OP
            elif chunk == '!=': print('NEQ_OP\t\t\t\t' + chunk)
            # LEFT_BRACE
            elif chunk == '{': print('LEFT_BRACE\t\t\t' + chunk)
            # RIGHT_BRACE
            elif chunk == '}': print('RIGHT_BRACE\t\t\t' + chunk)
            # LEFT_BRACKET
            elif chunk == '[': print('LEFT_BRACKET\t\t\t' + chunk)
            # RIGHT_BRACKET
            elif chunk == ']': print('RIGHT_BRACKET\t\t\t' + chunk)
            # OR_OP
            elif chunk == '||': print('OR_OP\t\t\t\t' + chunk)
            # AND_OP
            elif chunk == '&&': print('AND_OP\t\t\t\t' + chunk)
            # IDENTIFIER
            else: print('IDENTIFIER\t\t\t' + chunk)

# This line is required for the program to begin on its own.
main(sys.argv[1])
