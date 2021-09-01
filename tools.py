import re, getpass

def reg_input(text,type):
    expression = ""
    if(type == str):
        expression = r'(^[a-zA-Z0-9$@$!%*?&#^-_. +:]+)'
    elif(type == int):
        expression = r'(^[0-9]+)'
    elif(type == "pwd"):
        expression = r'(^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$)'
    valid = False
    while not valid:
        if(type == "pwd"):
            i = getpass.getpass(text)
        else:
            i = input(text)
        res_str = re.fullmatch(expression,i)
        if(res_str != None):
            valid = True
        else:
            print("Please enter a valid input")
            if(type == "pwd"):
                print("A password must be at least 8 chars and contain at least 1 number, 1 Capital and 1 special char")
    return i

    #Creates and sends a received receipt back to the sender
    def received_receipt(self, sender, type):
        receipt = {
            'target':sender,
            'received':type,
            'time_sent':str(datetime.now().strftime("%H:%m")),
            'sender':self.__username
            }
        data = js.dumps(receipt)
        self.send_to_server(data)