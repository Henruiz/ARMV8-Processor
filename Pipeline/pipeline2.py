

"""
    Title: Project 2 (Simulator)
    Authors: Henry Ruiz: h_r32@txstate.edu
            Alexander Gonzalez: a_g1593@txstate.edu
   Class: Computer Architecture
   Class #: CS 3339.
   Description: This program is used to decode files filled with binary code
                into ARMv8 proper assembly sim_instructionss, disassembler. Then it will properly update the PC Cycles and
                Counter.
"""
import sys


#"""These hex value will be used to properly mask the bits to get the correct output"""
specialMask = 0x1FFFFF
rnMask = 0x3E0  # 1st argument ARM Rn
rmMask = 0x1F0000  # second argument ARM rm
rdMask = 0x1F  # destination ARM Rd
imMask = 0x3FFC00  # ARM I Immediate
shmtMask = 0xFC00  # ARM ShAMT
addrMask = 0x1FF000  # ARM address for ld and st
addr2Mask = 0xFFFFE0  # addr for CB format
addr3Mask = 0x3FFFFFF # addr for B format
imsftMask = 0x600000  # shift for IM format
imdataMask = 0x1FFFE0  # data for IM type
# """These variables are going to be used to store the bits from the input file"""
opcodeStr = []
instrSpaced = []
arg1 = []
arg2 = []
arg3 = []
# """Theses variable are going to be used inside the methods/functions to compare """
arg1Str = []
arg2Str = []
arg3Str = []
# """These variables are going to be used for updating the pc cycles and counter"""
data = []
bindata = []
opcode = []
memory_pc = []
reg = []
sim_instructionsString = []
# file names
outputFileName = ''
inputFileName = ''

# Cache like list set up [valid, dirty, tag, data, data]
# Note: This is 4 sets of two blocks with 2 words per block
#           and each block has a valid, dirty, tag entry.
cacheSets = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]  # <-- 2 sets
            ,[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]] # <-- 2 sets

lruBit = [0, 0, 0, 0]

# Pre Buffers
# [instruciton index, instruciton index, instruciton index, instruciton index]
# [instruciton index, instruciton index]
preIssueBuffer = [0, 0, 0, 0]
preMemBuffer = [-1, -1]
preAluBuffer = [-1, -1]

# Post Buffers
# [instruciton index, instruciton index]
postMemBuffer = [-1, -1]
postAluBuffer = [-1, -1]

# will be used to hold the register values R1, R2, ...
registers = []

destinationReg = []
src2Register = []
src1Register = []




def bin_to_str_R(s):
    spacedStr = s[0:11] + " " + s[11:16] + " " + s[16:22] + " " + s[22:27] + " " + s[27:32]
    return spacedStr


def bin_to_str_D(s):
    spacedStr = s[0:11] + " " + s[11:20] + " " + s[20:22] + " " + s[22:27] + " " + s[27:32]
    return spacedStr


def bin_to_str_Break(s):
    spacedstr = s[0:8] + " " + s[8:11] + " " + s[11:16] + " " + s[16:21] + " " + s[21:26] + " " + s[26:32]
    return spacedstr


def bin_to_str_B(s):
    spacedStr = s[0:6] + " " + s[6:32]
    return spacedStr


def bin_to_str_I(s):
    spacedStr = s[0:10] + " " + s[10:22] + " " + s[22:27] + " " + s[27:32]
    return spacedStr


def bin_to_str_CB(s):
    spacedStr = s[0:8] + " " + s[8:27] + " " + s[27:32]
    return spacedStr


def bin_to_str_IM(s):
    spacedStr = s[0:9] + " " + s[9:11] + " " + s[11:27] + " " + s[27:32]
    return spacedStr


def immBitTo32BitConverter(num, bitsize):

    if bitsize == 19:
        negBitMask = 0x40000
        negExtendMask = 0xFFF80000
        negbit = (num & negBitMask) >> 18

        if negbit == 1:
            return num ^ negExtendMask
        else:
            return num
    elif bitsize == 26:
        negBitMask = 0x2000000
        negExtendMask = 0xFC000000
        negbit = (num & negBitMask) >> 25

        if negbit == 1:
            return num ^ negExtendMask
        else:
            return num


def imm32Bit2ComplementToDec(num):
    flipBitsMak = 0xFFFFFFFF

    signBitMask = 0x80000000

    if (num & signBitMask) >> 31:
        return -((num-1) ^ flipBitsMak)
    else:
        return num


def imm32BitUnsignedTo32BitSignedConverter(s):
    spacedStr = s[0:32] & specialMask
    return spacedStr


def simPrint(cycle, memory_pc, sim_instructions_string, currentAddress):

    if cycle == 1:
        f = open(outputFileName + "_sim.txt", 'w')
    else:
        f = open(outputFileName + "_sim.txt", 'a')


    f.write("=" * 20 + '\n')
    f.write("cycle:"+ str(cycle) + '\t' + str(memory_pc) + '\t' + sim_instructions_string + '\n\n')
    f.write("registers:" + '\n')
    f.write("r00:" + "\t" + str(reg[0]) + "\t" + str(reg[1]) + "\t" + str(reg[2]) + "\t" + str(reg[3]) + "\t"
            + str(reg[4]) + "\t" + str(reg[5]) + "\t" + str(reg[6]) + "\t" + str(reg[7]) + "\n")
    f.write("r08:" + "\t" + str(reg[8]) + "\t" + str(reg[9]) + "\t" + str(reg[10]) + "\t" + str(reg[11]) + "\t"
            + str(reg[12]) + "\t" + str(reg[13]) + "\t" + str(reg[14]) + "\t" + str(reg[15]) + "\n")
    f.write("r16:" + "\t" + str(reg[16]) + "\t" + str(reg[17]) + "\t" + str(reg[18]) + "\t" + str(reg[19]) + "\t"
            + str(reg[20]) + "\t" + str(reg[21]) + "\t" + str(reg[22]) + "\t" + str(reg[23]) + "\n")
    f.write("r24:" + "\t" + str(reg[24]) + "\t" + str(reg[25]) + "\t" + str(reg[26]) + "\t" + str(reg[27]) + "\t"
            + str(reg[28]) + "\t" + str(reg[29]) + "\t" + str(reg[30]) + "\t" + str(reg[31]) + "\n\n")
    f.write("data:")


    for i in range(len(data)):

        if i % 8 != 0:
            f.write(str(data[i]) + "\t")
        else:
            f.write("\n" + str(currentAddress) + ":\t" + str(data[i]) + "\t")
            currentAddress += 4 * 8


    f.write("\n")

    f.close()


def getCurrentMemory(address, startAddress):

    instruction_index = (address - startAddress) / 4

    if instruction_index > len(data):
        fullinstruction_index = (instruction_index % 7) + instruction_index + 1
        for i in range(fullinstruction_index - len(data)):
            data.append(0)


    return instruction_index

# -------------------------------------------------------------------------------------------------------------------- #
#                                               Start of Dissambler                                                    #
#                   Purpose of this class is to disassemble file filled with ARM (binary code) sim_instructionss       #
#                   Then to simulate the pc counter and updating the cycle correctly                                   #
# -------------------------------------------------------------------------------------------------------------------- #


class Dissasembler:

    def run(self):
        global opcodeStr
        global instrSpaced
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        global mem
        global binMem
        global opcode
        global memory_pc
        global sim_instructionsString
        global inputFileName
        global outputFileName

        pc = 0

        for i in range(len(sys.argv)):
            """ Reading in system arguments from terminal"""
            if sys.argv[i] == '-i' and i < (len(sys.argv) - 1):
                inputFileName = sys.argv[i + 1]
                print(inputFileName)
            elif sys.argv[i] == '-o' and i < (len(sys.argv) - 1):
                outputFileName = sys.argv[i + 1]
                print(outputFileName)

        """ Opening file test3_bin.txt"""
        sim_instructionss = [line.rstrip() for line in open(inputFileName, 'rb')]

        """Iterating through the file to be saved in their respected list"""
        for i in range(len(sim_instructionss)):
            opcode.append(int(sim_instructionss[i][0:11], 2))

            # This section is for R format sim_instructions
            if opcode[i] == 1112:
                opcodeStr.append("ADD")
                arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_R(sim_instructionss[i]))
                memory_pc.append(96 + (pc*4))

            elif opcode[i] == 1624:
                opcodeStr.append("SUB")
                arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_R(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 1104:
                opcodeStr.append("AND")
                arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_R(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 1360:
                opcodeStr.append("ORR")
                arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_R(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 1872:
                opcodeStr.append("EOR")
                arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg2.append((int(sim_instructionss[i], base=2) & rmMask) >> 16)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_R(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif 160 <= opcode[i] <= 191:
                opcodeStr.append("B")
                arg1.append(imm32Bit2ComplementToDec(immBitTo32BitConverter(int(sim_instructionss[i], base=2) & addr3Mask, 26)))
                arg2.append(0)
                arg3.append(0)
                arg1Str.append("\t#" + str(arg1[i]))
                arg2Str.append('')
                arg3Str.append('')
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_B(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            # This section is for I sim_instructionss
            elif 1160 <= opcode[i] <= 1161:
                opcodeStr.append("ADDI")
                arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg2.append((int(sim_instructionss[i], base=2) & imMask) >> 10)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(arg2[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_I(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif 1672 <= opcode[i] <= 1673:
                opcodeStr.append("SUBI")
                arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg2.append((int(sim_instructionss[i], base=2) & imMask) >> 10)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(arg2[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_I(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 1986:
                opcodeStr.append("LDUR")
                arg1.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg2.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg3.append((int(sim_instructionss[i], base=2) & addrMask) >> 12)
                arg1Str.append("\tR" + str(arg1[i]))
                arg2Str.append(", [R" + str(arg2[i]))
                arg3Str.append(", #" + str(arg3[i]) + "]")
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_D(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 1984:
                opcodeStr.append("STUR")
                arg1.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg2.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg3.append((int(sim_instructionss[i], base=2) & addrMask) >> 12)
                arg1Str.append("\tR" + str(arg1[i]))
                arg2Str.append(", [R" + str(arg2[i]))
                arg3Str.append(", #" + str(arg3[i]) + "]")
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_D(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif 1440 <= opcode[i] <= 1447:
                opcodeStr.append("CBZ")
                arg1.append(imm32Bit2ComplementToDec(immBitTo32BitConverter(((int(sim_instructionss[i], base=2) & addr2Mask) >> 5), 19)))
                arg2.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg3.append(0)
                arg1Str.append("\tR" + str(arg2[i]))
                arg2Str.append(", #" + str(arg1[i]))
                arg3Str.append("")
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_CB(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif 1448 <= opcode[i] <= 1455:
                opcodeStr.append("CBNZ")
                arg3.append(0)
                arg1.append(imm32Bit2ComplementToDec(immBitTo32BitConverter((int(sim_instructionss[i], base=2) & addr2Mask) >> 5, 19)))
                arg2.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg2[i]))
                arg2Str.append(", #" + str(arg1[i]))
                arg3Str.append("")
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_CB(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif 1684 <= opcode[i] <= 1687:

                opcodeStr.append("MOVZ")
                arg1.append((int(sim_instructionss[i], base=2) & imsftMask) >> 21)
                arg2.append((int(sim_instructionss[i], base=2) & imdataMask) >> 5)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", " + str(arg2[i]))
                arg3Str.append(", LSL " + str(arg1[i]*16))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_IM(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif 1940 <= opcode[i] <= 1943:
                opcodeStr.append("MOVZK")
                arg1.append((int(sim_instructionss[i], base=2) & imsftMask) >> 21)
                arg2.append((int(sim_instructionss[i], base=2) & imdataMask) >> 5)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", " + str(arg2[i]))
                arg3Str.append(", LSL " + str(arg1[i]*16))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_IM(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 1690:
                opcodeStr.append("LSR")
                arg1.append((int(sim_instructionss[i], base=2) & shmtMask) >> 10)
                arg2.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg2[i]))
                arg3Str.append(", #" + str(arg1[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_D(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 1691:
                opcodeStr.append("LSL")
                arg1.append((int(sim_instructionss[i], base=2) & shmtMask) >> 10)
                arg2.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg2[i]))
                arg3Str.append(", #" + str(arg1[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_D(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 1692:
                opcodeStr.append("ASR")
                arg1.append((int(sim_instructionss[i], base=2) & rnMask) >> 5)
                arg2.append((int(sim_instructionss[i], base=2) & shmtMask) >> 10)
                arg3.append((int(sim_instructionss[i], base=2) & rdMask) >> 0)
                arg1Str.append("\tR" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", #" + str(arg2[i]))
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_R(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 0:
                opcodeStr.append("NOP")
                arg1.append(0)
                arg2.append(0)
                arg3.append(0)
                arg1Str.append("")
                arg2Str.append("")
                arg3Str.append("")
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_Break(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))

            elif opcode[i] == 2038:
                opcodeStr.append("BREAK")
                arg1.append(0)
                arg2.append(0)
                arg3.append(0)
                arg1Str.append("")
                arg2Str.append("")
                arg3Str.append("")
                sim_instructionsString.append(opcodeStr[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
                instrSpaced.append(bin_to_str_Break(sim_instructionss[i]))
                memory_pc.append(96 + (pc * 4))
                pc += 1
                break

            pc += 1

        for i in range(pc, len(sim_instructionss)):
            bindata.append(sim_instructionss[i])
            data.append(imm32Bit2ComplementToDec(int(sim_instructionss[i], base=2)))
            memory_pc.append(96 + (pc * 4))
            pc += 1

        with open(outputFileName + "_dis.txt", 'w') as output:
            for i in range(len(memory_pc) - len(data)):
                output.write(instrSpaced[i])
                output.write("\t"+str(memory_pc[i])+"\t")
                output.write(sim_instructionsString[i])
                output.write("\n")

            for i in range(len(data)):
                output.write(bindata[i])
                output.write("\t" + str(memory_pc[(len(memory_pc) - len(data)) + i]))
                output.write("\t" + str(data[i]))
                output.write("\n")


D = Dissasembler()
D.run()

# -------------------------------------------------------------------------------------------------------------------- #
#                                               Start of Pipeline Class                                               #
#                   Purpose of this class is to Simulate an ARM (binary code) processor                                #
#                   Then to simulate the pc counter and updating the cycle correctly                                   #
# -------------------------------------------------------------------------------------------------------------------- #


class ControlUnit:

    def __init__ (self):
        global opcodeStr
        global instrSpaced
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        global mem
        global binMem
        global opcode
        global memory_pc
        global registers


    def run(self):
        go = True
        while go:
            self.WB_Unit.run()
            self.Alu_Unit.run()
            self.Mem_Unit.run()



C = ControlUnit()
# C.run()

# class WB_unit:
# Will save the data of the post Buffers if there is something. Else do nothing
# This will write back to the registers


class WB_Unit:

    def __init__(self):
        global postMemBuffer
        global postAluBuffer
        global registers

    def run(self):

        if postMemBuffer == -1:
            pass
        elif postMemBuffer != -1:
            registers[postMemBuffer[1]] = postMemBuffer[0]
            postMemBuffer[0] = -1
            postMemBuffer[1] = -1

        if postAluBuffer == -1:
            pass
        elif postAluBuffer != -1:
            registers[postAluBuffer[1]] = postMemBuffer[0]
            postAluBuffer[0] = -1
            postAluBuffer[1] = -1


# class ALU_unit:
#     the input will be preALUBUF
#         preALUBUFF will hold two instructions at the same time [instruction index, instruction index]
#
#         if the opcodestr == I or  R instructions
#             postALuBUFF = register[[Arg3 + arg1], i] #
#
#             preALUBUFF indexes will be updated first index replaced by second index
#                 second index = -1
#
#     the output will postALUBUff
#         postALUBUFF will hold [data, instruction] data will be the number in the instruction

class Alu_Unit:

    def __init__(self):
        global postMemBuffer
        global postAluBuffer
        global registers
        global opcodeStr
        global instrSpaced
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        global mem
        global binMem
        global opcode
        global memory_pc

    def run(self):

        if preAluBuffer[0] == -1:
            pass
        elif preAluBuffer[0] != -1:
            instruction_index = preAluBuffer[0]
            actual_instruction = opcodeStr[preAluBuffer[0]]
            preAluBuffer[0] = preAluBuffer[1]
            preAluBuffer[1] = -1

        # Transferring data to from register to Buffer
        if actual_instruction == 'ADD' or actual_instruction == 'ADDI':
            postAluBuffer[0] = registers[arg1[instruction_index] + arg2[instruction_index]]

        if actual_instruction == 'SUB' or actual_instruction == 'SUBI':
            postAluBuffer[0] = registers[arg1[instruction_index] - arg2[instruction_index]]

        if actual_instruction == 'AND':
            postAluBuffer[0] = registers[arg1[instruction_index] & arg2[instruction_index]]

        if actual_instruction == 'OR':
            postAluBuffer[0] = registers[arg1[instruction_index] | arg2[instruction_index]]

        if actual_instruction == 'EOR':
            postAluBuffer[0] = registers[arg1[instruction_index] ^ arg2[instruction_index]]

        if actual_instruction == 'LSL':
            postAluBuffer[0] = registers[arg2[instruction_index] << arg3[instruction_index]]

        if actual_instruction == 'LSR':
            postAluBuffer[0] = (registers[arg2[instruction_index]] % (1 << 64)) >> arg1[instruction_index]

        if actual_instruction == 'ASR':
            postAluBuffer[0] = registers[arg1[instruction_index] >> arg2[instruction_index]]

        if actual_instruction == 'MOVZ':
            postAluBuffer[0] = arg2[instruction_index] << (arg2[instruction_index] * 16)

        if actual_instruction == 'MOVK':
            if arg1[instruction_index] == 0:
                reg[arg3[instruction_index]] = (reg[arg3[instruction_index]] % (1 << 64)) >> 16
                reg[arg3[instruction_index]] = reg[arg3[instruction_index]] << 16
                reg[arg3[instruction_index]] = reg[arg3[instruction_index]] ^ arg2[instruction_index]

            elif arg1[instruction_index] == 1:
                rightSplitMask = 0x000000FF
                rightSplit = rightSplitMask & reg[arg3[instruction_index]]
                leftSplit = (reg[arg3[instruction_index]] % (1 << 64)) >> 32
                leftShiftedSplit = leftSplit << 32
                immShifted = arg2[instruction_index] << 16

                reg[arg3[instruction_index]] = rightSplit ^ immShifted
                reg[arg3[instruction_index]] = reg[arg3[instruction_index]] ^ leftShiftedSplit

            elif arg1[instruction_index] == 2:
                rightSplitMask = 0x0000FFFF
                rightSplit = rightSplitMask & reg[arg3[instruction_index]]
                leftSplit = (reg[arg3[instruction_index]] % (1 << 64)) >> 48
                leftShiftedSplit = leftSplit << 48
                immShifted = arg2[instruction_index] << 32

                reg[arg3[instruction_index]] = rightSplit ^ immShifted
                reg[arg3[instruction_index]] = reg[arg3[instruction_index]] ^ leftShiftedSplit

            elif arg1[instruction_index] == 3:
                rightSplitMask = 0x00FFFFFF
                rightSplit = rightSplitMask & reg[arg3[instruction_index]]
                immShifted = arg2[instruction_index] << 48

                reg[arg3[instruction_index]] = rightSplit ^ immShifted
            pass


# class mem_unit:
#     input preMemBuff will hold two instructions at the same time [instruction index, instruction index]
#
#     if instruction index is STUR(cannot write to the cache)(look back on slide 52 on deck 16) or LDUR
#         check cache for address (cache.accessMem(memIndex, i, isSW, arg1))
#     if miss
#         cache will return miss on first cycle and handle memory access
#         and cache load in the same cycle and should return a hit on next cycle
#     if hit
#         return true with value
#         update preMEmBuff indexes will be updated first index replaced by second index
#               second index = -1 in the cache
#         here will store or load mem values
#
#
#     output postMemBuff will hold [data, instruction] data will be the number in the instruction
#
#     indexes will be updated first index replaced by second index          second index = -1 in the cache

class Mem_Unit:
    def __init__(self):
        global preMemBuffer
        global registers
        global opcodeStr
        global instrSpaced
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        global mem
        global binMem
        global opcode
        global memory_pc


    def run(self):

        if preMemBuffer == -1:
            pass
        elif preMemBuffer != -1:
            instruction_index = preMemBuffer[0]
            actual_instruction = opcodeStr[preMemBuffer[0]]
            preMemBuffer[0] = preMemBuffer[1]
            preMemBuffer[1] = -1


        if actual_instruction == 'STUR':
            pass
        if actual_instruction == 'LDUR':
            pass

        pass

# class Issue_Unit: (look back at slide deck16)
#     input preIssueBuff will hold four instruction indexes
#
#     loop thru preIssueBuff to check for hazard
#         if not hazard
#             set first two instruction indexes to preMemBuffer or preALuBuffer
#
#     output prememBuffer and preALuBuffer and both first num is index, second is index


class Issue_Unit:
    def __init__(self):
        global preIssueBuffer
        global opcodeStr
        global instrSpaced
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        global mem
        global binMem
        global opcode
        global memory_pc
        pass

    def run(self):
        pass

# class Fetch:
#     takes all the lists from dissassembler
#
#     go over slide deck when we get here
#
#     output will be issueBuffer
#
# class cache:
#     def flush will write out all dirty blocks to memory at the end
#     def accessMem will take memIndex, instructionIndex, isWritetoMem, datatoWrite
#         returns boolean got a hit and data/instruction at cache location


class Fetch_Unit:
    def __init__(self):
        global preIssueBuffer
        global opcodeStr
        global instrSpaced
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        global mem
        global binMem
        global opcode
        global memory_pc
        pass

    def run(self):
        pass


# class cache:
#     def flush will write out all dirty blocks to memory at the end
#     def accessMem will take memIndex, instructionIndex, isWritetoMem, datatoWrite
#         returns boolean got a hit and data/instruction at cache location

class Cache:
    def __init__(self):
        global tag
        global memory_pc
        global setNum
        global wbAddr
        global data1
        global data2
        pass

    def run(self):
        pass

    def flush(self):
        pass

    def access_memory(self, memIndex, instructionIndex, isWriteToMem, dataToWrite):
        hit = True
        miss = False
        if self.memory_pc % 8 == 0:
            dataWord = 0  # block 0 was the address
            address1 = memory_pc
            address2 = memory_pc + 4
            # check for "alignment"
            # this picks the second word as address so we need to fix it
            # set address1 - block 1 address to address - 4
            if self.memory_pc % 8 != 0:
                dataWord = 1  # block 1 was the address
                address1 = memory_pc - 4
                address2 = memory_pc

        if self.cacheSets[setNum][self.IruBit[setNum]][1] == 1:
            # write back the memory address asociated with the block
            wbAddr = self.cacheSets[setNum][self.lruBit[setNum]][2] #tag
            # modify tag to get back to the original address, remember all addresses are inherently word aligned    \
            # lower 2 bits are zero !!!!
            wbAddr = (wbAddr << 5) + (setNum << 3)

        if wbAddr >= (C.numInstructions * 4) + 96:
            C.memory[C.getIndexOfMemAddress(wbAddr)] = self.cacheSets[setNum][self.lruBit[setNum]][3]

        if wbAddr + 4 >= (C.numInstructions * 4) + 96:
            C.memory[C.getIndexOfMemAddress(wbAddr+ 4 )] = self.cacheSets[setNum][self.lruBit[setNum]][4]

        # now update the cache flag bits
        self.cacheSets[setNum][self.IruBit[setNum]][0] = 1  # valid we are writing a block
        self.cacheSets[setNum][self.IruBit[setNum]][1] = 0  # reset the dirty bit
        if isWriteToMem:
            # dirty if is data mem is dirty again, intruction mem never dirty
            self.cacheSets[setNum][self.IruBit[setNum]][1] = 1
            # update both words in the actual cache block in set
        self.cacheSets[setNum][self.lruBit[setNum]][2] = tag  # tag
        self.cacheSets[setNum][self.lruBit[setNum]][3] = data1  # data
        self.cacheSets[setNum][self.lruBit[setNum]][4] = data2  # nextData
        self.lruBit[setNum] = (self.lruBit[setNum] + 1) % 2  # set lru to show block is recently used

        # Return boolean got a hit and data/instruction at cache location
        # dataword was the actual word that generated the hit
        return [True, self.cacheSets[setNum][(self.lruBit[setNum] + 1) % 2][dataWord + 3]]



print opcodeStr
print registers
