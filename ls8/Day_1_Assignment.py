"""CPU functionality."""


import sys


LDI = 0b10000010
PRN = 0b01000111
MULT = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
HLT = 0b00000001
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
     
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.SP = 8 # ? last item in our regsiters
        self.pc = 0 # PROGRAM COUNTER

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1
    def ram_read(self, MAR):
        # MAR = memory address register
        return self.ram[MAR]

    
    def ram_write(self, MAR, MDR):
        # MAR = memory address register
        # MDR = memory data register
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        if len(sys.argv) != 2:
            print("Usage: cpu.py filename")
            sys.exit(1)
        
        filename = sys.argv[1]

        try:
            with open(filename) as f:
                for line in f:
                    
                    instruction = line.split("#")[0].strip()
                    
                    if instruction == "":
                        continue

                    val = int(instruction, 2)    

                    self.ram_write(address, val)

                    address += 1

        except FileNotFoundError:
            print(f"File {filename} not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        if op == "CMP":          

            if self.reg[reg_a] > self.reg[reg_b]:
                flag = 0b0000010

            elif self.reg[reg_a] < self.reg[reg_b]:
                flag = 0b00000100

            else:
                flag = 0b00000001

            self.SP -= 1
            self.reg[self.SP] = flag

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        
        running = True
        
        while running:

            command = self.ram[self.pc]

 
            if command == LDI: # LDI R0,8
                reg_idx = self.ram[self.pc + 1]
                reg_val = self.ram[self.pc + 2]
                self.reg[reg_idx] = reg_val
                self.pc += 3
            
            elif command == PRN: # PRN R0
                reg_idx = self.ram[self.pc + 1] 
                print(self.reg[reg_idx])
                self.pc += 2

            elif command == MULT: # MULT
                reg_a_idx = self.ram[self.pc + 1]
                reg_b_idx = self.ram[self.pc + 2]

                val = self.reg[reg_a_idx] * self.reg[reg_b_idx]

                self.reg[reg_a_idx] = val

                self.pc += 3

            elif command == PUSH:

                reg_idx = self.ram[self.pc + 1]

                val = self.reg[reg_idx]
                
                self.SP -= 1

                self.reg[self.SP] = val

                self.pc += 2


            elif command == POP:
                
                reg_idx = self.ram[ self.pc + 1 ]

                val = self.reg[ self.SP ] 

                self.reg[reg_idx] = val

                self.SP += 1

                self.pc += 2

            elif command == CALL:

                self.SP -= 1

                reg_idx = self.ram[self.pc + 1]

                self.reg[self.SP] = self.pc + 2

                self.pc = self.reg[reg_idx]

            elif command == RET:

                ret_idx = self.reg[self.SP]

                self.pc = ret_idx

                self.SP += 1

            elif command == ADD:

                reg_a_idx = self.ram[self.pc + 1]
                reg_b_idx = self.ram[self.pc + 2]

                self.reg[reg_a_idx] += self.reg[reg_b_idx]

                self.pc += 3

            elif command == CMP:
                reg_a_idx = self.ram[self.pc + 1]
                reg_b_idx = self.ram[self.pc + 2]
                self.alu("CMP", reg_a_idx, reg_b_idx)
                self.pc += 3

            elif command == JMP:
                reg_a_idx = self.ram[ self.pc + 1]
                self.pc = self.reg[reg_a_idx]


            elif command == JEQ:

                flag = self.reg[self.SP]

                self.SP += 1

                if flag == 1:

                    reg_idx = self.ram[self.pc + 1]
                    address = self.reg[reg_idx]
                    self.pc = address
                
                else:
                    self.pc += 2

            elif command == JNE:
                flag = self.reg[self.SP]

                self.SP += 1

                if flag > 1:
                    reg_idx = self.ram[self.pc + 1]
                    self.pc = self.reg[reg_idx]

                else:
                    self.pc += 2
                

            elif command == HLT: # HLT
                self.pc += 1
                running = False
            
            else:
                print(f"Unknown instruction: {command:b}")
                sys.exit(1)