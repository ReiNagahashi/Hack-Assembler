class Assembler():
    # 定義済みシンボルでシンボルテーブルを初期化しておく
    symbol_table = {
        "SP":0,
        "LCL":1,
        "ARG":2,
        "THIS":3,
        "THAT":4,
        "R0":0,
        "R1":1,
        "R2":2,
        "R3":3,
        "R4":4,
        "R5":5,
        "R6":6,
        "R7":7,
        "R8":8,
        "R9":9,
        "R10":10,
        "R11":11,
        "R12":12,
        "R13":13,
        "R14":14,
        "R15":15,
        "SCREEN":16384,
        "KBD":25576
    }
    # comp Aレジスタ操作 a = 0
    comp_A_table = {
        "0": "101010",
        "1": "111111",
        "-1": "111010",
        "D": "001100",
        "A": "110000",
        "!D": "001101",
        "!A": "110001",
        "-D": "001111",
        "-A": "110011",
        "D+1": "011111",
        "A+1": "110111",
        "D-1": "001110",
        "A-1": "110010",
        "D+A": "000010",
        "D-A": "010011",
        "A-D": "000111",
        "D&A": "000000",
        "D|A": "010101",
    }
    # comp メモリ操作 a = 1
    comp_M_table = {
        "M": "110000",
        "!M": "110001",
        "-M": "110011",
        "M+1": "110111",
        "M-1": "110010",
        "D+M": "000010",
        "D-M": "010011",
        "M-D": "000111",
        "D&M": "000000",
        "D|M": "010101"
    }
    dest_table = {
        "null":"000",
        "M":"001",
        "D":"010",
        "MD":"011",
        "A":"100",
        "AM":"101",
        "AD":"110",
        "AMD":"111"
    }
    jump_table = {
        "null":"000",
        "JGT":"001",
        "JEQ":"0101",
        "JGE":"011",
        "JLT":"100",
        "JNE":"101",
        "JLE":"110",
        "JMP":"111"
    }

    def __init__(self):
        self.current_max_memory_address = 16
        self.current_command_type = ""
        self.current_rom_address = 0
        self.current_row = 0
        self.label_table = {}
        self.input_file = []

    def readFile(self, file_path):
        self.input_file = []

        with open(file_path, "r") as f:
            for line in f:
                self.input_file.append(line.strip())
        
    def isNotCommand(self):
        return len(current_command) == 0 or (len(current_command) > 1 and current_command[0] == "/" and current_command[1] == "/")
    

    def hasMoreCommands(self):
        return self.current_row < len(self.input_file)
    
    def advance(self):
        return self.input_file[self.current_row]
    
    # この判定は擬似コマンドだけに対してtrueを返す→つまり(ラベル名)というやつだけ
    def isLCommand(self):
        current_command = self.input_file[self.current_row]

        return len(current_command) > 1 and current_command[0] == "(" and current_command[-1] == ")"


    def commandType(self):
        current_command = self.input_file[self.current_row]

        if self.isLCommand():
            self.current_command_type = "L_COMMAND"
            return
        if current_command[0] == "@":
            self.current_command_type = "A_COMMAND"
            return
        
        self.current_command_type = "C_COMMAND"



    def getBinary(self):
        if self.current_command_type == "L_COMMAND":
            return self.getBinaryFromCommandL()
        if self.current_command_type == "A_COMMAND":
            return self.getBinaryFromCommandA()
        elif self.current_command_type == "C_COMMAND":
            return self.getBinaryFromCommandC()

        return ""


    def getBinaryFromCommandL(self):
        if self.current_command_type != "L_COMMAND" : return ""
        
        symbol = self.input_file[self.current_row][1:]
        if symbol not in self.label_table:
            return ""
        
        binary_data = self.convertBinary(self.label_table[symbol])

        return binary_data
        

    # 現在のコマンドがA_COMMANDの時にのみ実行可能→これにはラベルテーブルにシンボルが入っている場合の処理も含む
    def getBinaryFromCommandA(self):
        if self.current_command_type != "A_COMMAND": return ""
        symbol_or_digit = self.input_file[self.current_row][1:]
        # 結果の値の初期化
        decimal_value = -1

        # ラベルテーブルに入っている場合は、変数ではなくラベルとしての処理をする
        if symbol_or_digit in self.label_table:
            decimal_value = self.label_table[symbol_or_digit]
        # 変数であり、なおかつ単なる整数でない場合は、その変数をシンボルテーブルから取得する
        elif not symbol_or_digit.isdigit():
            symbol = symbol_or_digit
            self.setSymbolTable(symbol)
            decimal_value = self.symbol_table[symbol]
        # 単なる整数の場合は、整数型にする
        else:
            decimal_value = int(symbol_or_digit)

        binary_data = self.convertBinary(decimal_value)

        return binary_data
    

    def comp(self, key):
        if key in self.comp_A_table:
            return "0" + self.comp_A_table[key]
        
        return "1" + self.comp_M_table[key]
    

    def dest(self, key):
        return self.dest_table[key]


    def jump(self, key):
        return self.jump_table[key]


    def getBinaryFromCommandC(self):
        if self.current_command_type != "C_COMMAND": return ""

        current_command = self.input_file[self.current_row]

        comp_binary = ""
        dest_binary = ""
        jump_binary = ""
        # iで走査して=があったら、そのインデックスを格納。ない場合はそれを報告して条件式と判断して、それに応じた処理を書く
        equal_symbol_id = -1
        semicolon_symbol_id = -1
        for i in range(len(current_command)):
            if current_command[i] == "=":
                equal_symbol_id = i
            if current_command[i] == ";":
                semicolon_symbol_id = i
        # =と;が両方ある場合
        if equal_symbol_id != -1 and semicolon_symbol_id != -1:
            # =がある場合は、 =より前の文字列は書き込み対象のdestのために処理する
            # =以降の値はcompテーブルのキーになる 
            dest_binary += self.dest(current_command[:equal_symbol_id])
            comp_binary += self.comp(current_command[equal_symbol_id+1: semicolon_symbol_id])
            jump_binary += self.jump(current_command[semicolon_symbol_id+1:])
        # =のみの場合
        elif equal_symbol_id != -1:
            dest_binary += self.dest(current_command[:equal_symbol_id])
            comp_binary += self.comp(current_command[equal_symbol_id+1:])
            jump_binary += self.jump("null")
        # ;のみの場合
        else:
            dest_binary += self.dest("null")
            comp_binary += self.comp(current_command[:semicolon_symbol_id])
            jump_binary += self.jump(current_command[semicolon_symbol_id+1:])
    

        return "111" + comp_binary + dest_binary + jump_binary



    # 現在のコマンドがL_COMMANDの時にのみ実行可能 格納されるROMアドレスは現在のROMアドレス+1。Lコマンドの時には実際にROMアドレスは更新されないことに注意
    def setLabelTable(self):
        if self.current_command_type != "L_COMMAND": return

        l_command = self.input_file[self.current_row][1:]
        self.label_table[l_command[:-1]] = self.current_rom_address

    # ラベルテーブルに格納されているROMアドレスを取得する→条件式の際に呼び出すとき、このラベルとしてのシンボルは格納されている命令アドレス値が二進数に変換される
    def getRomAddressFromRebel(self):
        if self.current_command_type != "L_COMMAND": return
        # 先頭の@を省く
        l_command = self.input_file[self.current_row][1:]
        # L_commandは既にlabel_tableに入っている
        return self.label_table[l_command]


    def setSymbolTable(self, value):
        if value not in self.symbol_table:
            self.symbol_table[value] = self.current_max_memory_address
            self.current_max_memory_address += 1


    def convertBinary(self, decimal):
        return format(decimal, '016b')



commands = input().split()
if commands[0] != "Assembler" or len(commands) != 2 or commands[1][-4:] != ".asm":
    exit()

file_path = commands[1]
asm = Assembler()
asm.readFile(file_path)
while asm.hasMoreCommands():
    current_command = asm.advance()
    # コメント ないし 空白である場合は次の行にいく
    if asm.isNotCommand():
        asm.current_row += 1
        continue

    asm.commandType()
    
    if asm.current_command_type== "L_COMMAND":
        asm.setLabelTable()
    else:
        asm.current_rom_address += 1
    
    asm.current_row += 1


asm.readFile(file_path)
asm.current_row = 0


# 目的：A, Cコマンドそれぞれをバイナリにした文字列に変換してそれを出力する。
while asm.hasMoreCommands():
    # 解析する命令を取得
    current_command = asm.advance()
    if asm.isNotCommand():
        asm.current_row += 1
        continue


    asm.commandType()
    if asm.isLCommand():
        asm.current_row += 1
        continue


    binary_data = asm.getBinary()

    with open(file_path[:-4] + ".hack", "a") as o:
        print(binary_data, file=o)
    asm.current_row += 1
    

    