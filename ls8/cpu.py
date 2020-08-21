"""CPU functionality."""

import sys

# List of the codes and corresponding names.
HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
MUL = 0b10100010
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

# FL bits: 00000LGE

# L Less-than
# G Greater-than
# E Equal


# Main CPU class
class CPU:
    # Construct a new CPU
    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7  # stack pointer is always register 7
        self.fl = [0] * 8

        self.dispatchtable = {
            JNE: self.jne,
            JEQ: self.jeq,
            JMP: self.jmp,
            CMP: self.CMP,
            MUL: self.mul,
            ADD: self.add,
            PRN: self.prn,
            LDI: self.ldi,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self.ret
        }

    # Load a program into memory

    def load(self, file_name):
        address = 0

        with open(file_name, 'r') as f:
            for line in f:
                if line.startswith('#') or line.startswith('\n'):
                    continue
                else:
                    instruction = line.split(' ')[0]
                    self.ram[address] = int(instruction, 2)
                    address += 1

    # Read RAM at address then return  value

    def ram_read(self, mar):
        return self.ram[mar]

    # Write a value at given address

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    # Arithmetic and Logic Unit

    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        if op == "CMP":
            self.fl[7] = 0
            self.fl[6] = 0
            self.fl[5] = 0
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl[7] = 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl[5] = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl[6] = 1

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "JEQ":
            if self.fl[7] == 1:
                self.jmp(reg_a, reg_b)
            else:
                self.pc += 2

        elif op == "JNE":
            if self.fl[7] == False:
                self.jmp(reg_a, reg_b)
            else:
                self.pc += 2

        else:
            raise Exception("Unsupported ALU operation")

    # Handy function to print out the CPU state.
    # You might want to call this from run() if you need help debugging.

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # Handle CMP

    def CMP(self, reg_a, reg_b):
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3

    # Handle JMP

    def jmp(self, reg_a, reg_b):
        self.pc = self.reg[reg_a]

    # Handle JEQ

    def jeq(self, reg_a, reg_b):
        self.alu("JEQ", reg_a, reg_b)

    # Handle JNE

    def jne(self, reg_a, reg_b):
        self.alu("JNE", reg_a, reg_b)

    # Handle MUL

    def mul(self, reg_a, reg_b):
        self.alu("MUL", reg_a, reg_b)
        self.pc += 3

    # Handle ADD

    def add(self, reg_a, reg_b):
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3

    # Handle PRN

    def prn(self, reg_a, reg_b):
        print(self.reg[reg_a])
        self.pc += 2

    # Handle LDI

    def ldi(self, reg_a, reg_b):
        self.reg[reg_a] = reg_b
        self.pc += 3

    # Handle PUSH

    def push(self, reg_a, reg_b):
        self.sp -= 1
        self.ram_write(self.sp, self.reg[reg_a])
        self.pc += 2

    # Handle POP

    def pop(self, reg_a, reg_b):
        self.reg[reg_a] = self.ram_read(self.sp)
        self.sp += 1
        self.pc += 2

    # Handle CALL

    def call(self, reg_a, reg_b):
        self.sp -= 1
        self.ram_write(self.sp, self.pc + 2)
        self.pc = self.reg[reg_a]

    # Handle RET

    def ret(self, reg_a, reg_b):
        self.pc = self.ram_read(self.sp)
        self.sp += 1

    # Run the CPU

    def run(self):
        running = True

        while running:
            ir = self.ram_read(self.pc)
            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)

            if ir == HLT:
                running = False
            else:
                self.dispatchtable[ir](reg_a, reg_b)