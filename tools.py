import re

def reg_input(text,type):
    expression = ""
    if(type == str):
        expression = r'(^[a-zA-Z0-9$@$!%*?&#^-_. +:]+)'
    elif(type == int):
        expression = r'(^[0-9]+)'
    valid = False
    while not valid:
        i = input(text)
        res_str = re.fullmatch(expression,i)
        if(res_str != None):
            valid = True
        else:
            print("Please enter a valid input")
    return i