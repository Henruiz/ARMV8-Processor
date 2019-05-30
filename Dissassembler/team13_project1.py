"""
    Title: Project 1 (Disassembler)
   Authors: Henry Ruiz: h_r32@txstate.edu
            Alexander Gonzalez: a_g1593@txstate.edu
   Class: Computer Architecture
   Class #: CS 3339.
   Description: This program is used to decode files filled with binary code
                into ARMv8 proper assembly sim_instructionss, disassembler.
"""
import sys
import os

"""Masks"""
spcialMask = 0x1FFFFF
rnMask = 0x3E0
rmMask = 0x1F0000
rdMask = 0x1F
imMask = 0x3FFc00
shmtMask = 0xFC00  # ARM ShAMT
addrMask = 0x1FF000
addr2Mask = 0xFFFFE0
imsftMask = 0x600000  # shift for IM format
imdataMask = 0x1FFFE0  # data for IM type

"""These variables are going to be used to store the bits from the input file"""
opcode = []  # Storing decimal representation of an opcode
instrSpaced = []  # <type 'list'>: ['0 01000 00000 00001 00000 00000 001010', '1 01000 00000 00001 00000 00000 001010',...]
arg1 = []  # <type 'list'>: [0, 0, 0, 0, 0, 1, 1, 10, 10, 0, 3, 4, 152, 4, 10, 1, 0, 112, 0]
arg2 = []  # <type 'list'>: [0, 1, 1, 0, 1, 0, 10, 3, 4, 5, 0, 5, 0, 5, 6, 1, 1, 0, 0]
arg3 = []  # <type 'list'>: [0, 10, 264, 0, 264, 48, 2, 172, 216, 260, 8, 6, 0, 6, 172, -1, 264, 0, 0]

"""Theses variable are going to be used inside the methods/functions to compare """
opcodeStr = []  # <type 'list'>: ['Invalid sim_instructions', 'ADDI', 'SW', 'Invalid sim_instructions', 'LW', 'BLTZ', 'SLL',...]
arg1Str = []  # <type 'list'>: ['', '\tR1', '\tR1', '', '\tR1', '\tR1', '\tR10', '\tR3', '\tR4', .....]
arg2Str = []  # <type 'list'>: ['', ', R0', ', 264', '', ', 264', ', #48', ', R1', ', 172', ', 216', ...]'
arg3Str = []  # <type 'list'>: ['', ', #10', '(R0)', '', '(R0)', '', ', #2', '(R10)', '(R10)', '(R0)',...]
mem = []  # <type 'list'>: [-1, -2, -3, 1, 2, 3, 0, 0, 5, -5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
binMem = []  # <type 'list'>: ['11111111111111111111111111111111', '11111111111111111111111111111110', ...]
offset = []

PC = 96  # First address
counter = 0
# -------------------------------------------------------------------------------------------------------------------- #
#                                               Start of Class                                                         #
#                   Purpose of this class is to disassemble file filled with ARM (binary code) sim_instructionss            #
# -------------------------------------------------------------------------------------------------------------------- #

class Dissasembler:
    def __init__(self):
        return None

    def run(self):
        global opcodeStr
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        global mem
        global binMem
        global opcode
        global PC


    def immBitTo32BitConverter(num, bitsize):
        #need to read in 12 or 16 or 26 bit offset then convert it too 32 big
        if bitsize == 19:
            negBitMask = 0x800
            extendMask = 0xFFFFF000
            neg = (num & negBitMask) >> 18

            if neg == 0:
                return  num
            else:
                return (num ^ extendMask)

        elif bitsize == 26:
            negBitMask = 0x2000000
            extendMask = 0xFC00000
            neg = (num & negBitMask) >> 25

            if neg == 0:
                return num
            else:
                return (num ^ extendMask)

    def imm32BitUnsignedTo32BitSignedConverter(num):
        return num

    def immSignedToTwosConverter(num):
        return num

    def bin_to_str_R(s):
        spacedStr = s[0:11] + " " + s[11:16] + " " + s[16:22] + " " + s[22:27] + " " + s[27:32]
        return spacedStr

    def bin_to_str_B(s):
        spacedStr = s[0:6] + " " + s[6:32] + "    "
        return spacedStr

    def bin_to_str_I(s):
        spacedStr = s[0:10] + " " + s[10:22] + " " + s[22:27] + " " + s[27:32] + "  "
        return spacedStr

    def bin_to_str_D(s):
        spacedStr = s[0:11] + " " + s[11:20] + " " + s[20:22] + " " + s[22:27] + " " + s[27:32] + "  "
        return spacedStr

    def bin_to_str_CB(s):
        spacedStr = s[0:8] + " " + s[8:27] + " " + s[27:32] + "  "
        return spacedStr

    def bin_to_str_IM(s):
        spacedStr = s[0:9] + " " + s[9:11] + " " + s[11:27] + " " + s[27:32] + "  "
        return spacedStr

    def bin_to_str_Break(s):
        spacedStr = s[0:8] + " " + s[8:11] + " " + s[11:16] + " " + s[16:21] + " " + s[21:26] + " " + s[26:32] + "  "
        return spacedStr

    def bin_to_str_data(s):
        spacedStr = s[0:32] + "      "
        return spacedStr

    def twosCompSigned(num):
        inint = int("{0:b}".format(num))
        flip = ~inint
        flip += 1
        intFlipped = int(str(flip), 2)
        return abs(intFlipped)

    if __name__ == "__main__":

        """ Reading in system arguments from terminal"""
        for i in range(len(sys.argv)):
            if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
                inputFileName = sys.argv[i + 1]
                print (inputFileName)
            elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
                outputFileName = sys.argv[i + 1]

    """ Opening file test3_bin.txt"""
    sim_instructionss = [line.rstrip() for line in open(inputFileName, 'rb')]
    numberOfsim_instructionss = int(len(sim_instructionss))

    """Iterating through the file to be saved in their respected list"""
    for i in range(len(sim_instructionss)):
        opcode.append(int(sim_instructionss[i][0:11], 2))  # opcode 11 bits

        if opcode[i] == 1112:
            opcodeStr.append("ADD")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", R" + str(arg1[i]))
            arg3Str.append(", R" + str(arg2[i]))
            instrSpaced.append(bin_to_str_R(sim_instructionss[i]))

        elif opcode[i] == 1624:
            opcodeStr.append("SUB")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", R" + str(arg1[i]))
            arg3Str.append(", R" + str(arg2[i]))
            instrSpaced.append(bin_to_str_R(sim_instructionss[i]))

        elif opcode[i] == 1104:
            opcodeStr.append("AND")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", R" + str(arg1[i]))
            arg3Str.append(", R" + str(arg2[i]))
            instrSpaced.append(bin_to_str_R(sim_instructionss[i]))

        elif opcode[i] == 1360:
            opcodeStr.append("ORR")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", R" + str(arg1[i]))
            arg3Str.append(", R" + str(arg2[i]))
            instrSpaced.append(bin_to_str_R(sim_instructionss[i]))

       # B , CB & I USE SIGNED VALUE
        elif 160 <= opcode[i] <= 190:
            opcodeStr.append("B")
            # need to change this to extender and then grab that binary and convert too decimal
            # arg1.append('{:032b}'.format(int(sim_instructionss[i][6:32], base=2 & shmtMask)))
            arg1.append(twosCompSigned(int(sim_instructionss[i][6:32], base=2 & spcialMask)))
            arg2.append(' ')
            arg3.append(' ')
            arg1Str.append('#' + str(arg1[i]))
            arg2Str.append(' ')
            arg3Str.append(' ')
            instrSpaced.append(bin_to_str_B(sim_instructionss[i]))

        elif 1160 <= opcode[i] <= 1161:
            opcodeStr.append("ADDI")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & imMask) >> 10)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", R" + str(arg1[i]))
            arg3Str.append(", #" + str(arg2[i]))
            instrSpaced.append(bin_to_str_I(sim_instructionss[i]))

        elif 1672 <= opcode[i] <= 1673:
            opcodeStr.append("SUBI")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & imMask) >> 10)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", R" + str(arg1[i]))
            arg3Str.append(", #" + str(arg2[i]))
            instrSpaced.append(bin_to_str_I(sim_instructionss[i]))

        elif opcode[i] == 1986:
            opcodeStr.append("LDUR")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & imMask) >> 12)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", [R" + str(arg1[i]))
            arg3Str.append(", #" + str(arg2[i]) + "]")
            instrSpaced.append(bin_to_str_D(sim_instructionss[i]))

        elif opcode[i] == 1984:
            opcodeStr.append("STUR")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & imMask) >> 12)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", [R" + str(arg1[i]))
            arg3Str.append(", #" + str(arg2[i]) + "]")
            instrSpaced.append(bin_to_str_D(sim_instructionss[i]))

        elif 1440 <= opcode[i] <= 1447:
            opcodeStr.append("CBZ")
            arg1.append((int(sim_instructionss[i], base=2) & addr2Mask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", #" + str(immBitTo32BitConverter(arg1[i], 19)))
            arg3Str.append(" ")
            instrSpaced.append(bin_to_str_CB(sim_instructionss[i]))

        elif 1448 <= opcode[i] <= 1455:
            opcodeStr.append("CBNZ")
            arg1.append((int(sim_instructionss[i], base=2) & addr2Mask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", #" + str(immBitTo32BitConverter(arg1[i], 19)))
            arg3Str.append(" ")
            instrSpaced.append(bin_to_str_CB(sim_instructionss[i]))

        elif 1684 <= opcode[i] <= 1687:
            opcodeStr.append("MOVZ")
            arg1.append((int(sim_instructionss[i], base=2) & imdataMask) >> 5)
            arg2.append(((int(sim_instructionss[i], base=2) & imsftMask) >> 21) * 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", " + str(arg1[i]))
            arg3Str.append(", LSL " + str(arg2[i]))
            instrSpaced.append(bin_to_str_IM(sim_instructionss[i]))

        elif 1940 <= opcode[i] <= 1943:
            opcodeStr.append("MOVK")
            arg1.append((int(sim_instructionss[i], base=2) & imdataMask) >> 5)
            arg2.append(((int(sim_instructionss[i], base=2) & imsftMask) >> 21) * 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", " + str(arg1[i]))
            arg3Str.append(", LSL " + str(arg2[i]))
            instrSpaced.append(bin_to_str_IM(sim_instructionss[i]))

        elif opcode[i] == 1690:
            opcodeStr.append("LSR")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & imMask) >> 10)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 6)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", R" + str(arg1[i]))
            arg3Str.append(", #" + str(arg2[i]))
            instrSpaced.append(bin_to_str_R(sim_instructionss[i]))

        elif opcode[i] == 1691:
            opcodeStr.append("LSL")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & imMask) >> 19)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 6)
            arg1Str.append("R" + str(arg3[i]))
            arg2Str.append(", R" + str(arg1[i]))
            arg3Str.append(", #" + str(arg2[i]))
            instrSpaced.append(bin_to_str_R(sim_instructionss[i]))

# AFTER BREAK IS PRINTED WE MUST START PROCESSING DATA
        elif opcode[i] == 2038:
            opcodeStr.append("BREAK")
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
            arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append(" ")
            arg2Str.append(" ")
            arg3Str.append(" ")
            instrSpaced.append(bin_to_str_Break(sim_instructionss[i]))
            True

        elif opcode[i] == 2047:
            counter -= 1
            opcodeStr.append(counter)
            arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 32)
            arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
            arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
            arg1Str.append(" ")
            arg2Str.append(" ")
            arg3Str.append(" ")
            instrSpaced.append(bin_to_str_data(sim_instructionss[i]))

    # for i in range(numberOfsim_instructionss, len(sim_instructionss)):
    #     mem.append(imm32BitUnsignedTo32BitSignedConverter(int(sim_instructionss[i], base=2)))
    #     binMem.append(sim_instructionss[i])

        """ Writing to file test13_out.txt"""
        with open(outputFileName, 'w') as of:
            for x in range(len(instrSpaced)):
                of.write(str(instrSpaced[x]))
                of.write("\t")
                of.write(str(PC + x * 4))
                of.write("\t")
                of.write(str(opcodeStr[x]))
                of.write("\t")
                of.write(str(arg1Str[x]))
                of.write(str(arg2Str[x]))
                of.write(str(arg3Str[x]))
                of.write("\n")

            # for i in range(len(data)):
            #     of.write(binMem[i])
            #     of.write("\t" + str(mem[(len(mem) - len(data)) + i]))
            #     of.write("\t" +str(data[i]))
            #     of.write("\n")


dissasemble = Dissasembler()
dissasemble.run()



