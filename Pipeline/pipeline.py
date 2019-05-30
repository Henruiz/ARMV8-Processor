

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
tagMask = 4294967264
setMask = 24
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
justMissedList = [] #implies address's that result from ma

# file names
outputFileName = ''
inputFileName = ''

# Cache like list set up [valid, dirty, tag, data, data]
# Note: This is 4 sets of two blocks with 2 words per block
#           and each block has a valid, dirty, tag entry.
cacheSets = [ [ [0,0,0,0,0], [0,0,0,0,0] ], [ [0,0,0,0,0], [0,0,0,0,0] ],
             [ [0,0,0,0,0], [0,0,0,0,0] ], [ [0,0,0,0,0], [0,0,0,0,0] ] ] # <-- 2 sets

lruBit = [0, 0, 0, 0]

# Pre Buffers
# [instruciton index, instruciton index, instruciton index, instruciton index]
# [instruciton index, instruciton index]
preIssueBuffer = [-1, -1, -1, -1]
preMemBuffer = [-1, -1]
preAluBuffer = [-1, -1]

# Post Buffers
# [instruciton index, instruciton index]
postMemBuffer = [-1, -1]
postAluBuffer = [-1, -1]

# will be used to hold the register values R1, R2, ...
registers = []
pc = 96

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

    sim_index = (address - startAddress) / 4

    if sim_index > len(data):
        fullsim_index = (sim_index % 7) + sim_index + 1
        for i in range(fullsim_index - len(data)):
            data.append(0)


    return sim_index

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


class Pipeline:

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
        while True:
            self.WB_Unit.run()
            self.Alu_Unit.run()


P = Pipeline()

# class WB_unit:
# Will save the dat of the post Buffers if there is something. Else do nothing

class WB_Unit():

    def __init__(self):
        global postALUBuff
        global postMemBuff
        global reg

    def run(self):


        if postALUBuff[1] != -1:
            reg[postALUBuff[1]] = postALUBuff[0]
            postALUBuff[0] = -1
            postALUBuff[1] = -1

        if postMemBuff[1] != 1:
            reg[postMemBuff[1]] = postMemBuff[0]
            postMemBuff[0] = -1
            postMemBuff[1] = -1


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

class Alu_Unit():

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

class Mem_Unit():
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
        pass

    def run(self):

        if preMemBuffer == -1:
            pass
        elif preMemBuffer != -1:
            instruction_index = preMemBuffer[0]
            current_instruction = opcodeStr[preMemBuffer[0]]
            preMemBuffer[0] = preMemBuffer[1]
            preMemBuffer[1] = -1


        if current_instruction == 'STUR':
            #cache.accessMem(memIndex, i, isSW, sim.R[sim.arg2[i]]

            #if cache returns with a hit, update the preMemBuffer setting
            #preMemBuffer[0] = preMemBuffer[1] and then reset preMemBuffer[1] = -1
            #Then either write cache for a STORE OR A WRITE value obtained from cache to
            #the postMemBuffer.
            pass
        if current_instruction == 'LDUR':
            # cache.accessMem(memIndex, i, isSW, sim.R[sim.arg2[i]]
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


class Issue_Unit():
    def __init__(self):
        global preIssueBuffer
        global preAluBuffer
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

    def isMemop(index):

        if opcode[index] == 1986 or opcode[index] == 1984:
            return True

    def run(self):
        numIssued = 0
        numInPreIssuedBuffer = 0
        issuedIndex = [-1,-1]


        if preIssueBuffer[0] != -1:
            curr = preBuff[0]

        for element in preIssueBuffer:
            if element != -1:
                numInPreIssuedBuffer += 1

        while numIssued <2 and numInPreIssuedBuffer > 0 and curr < 4:
            index = preIssueBuffer[curr]
            issueMe = True

            if curr > 0:
             for i in range(0, curr):
                 if des[index] == des[preIssueBuffer[i]]:
                     issueMe = False
                     break

             if isMemOp(index):
                 for i in range(0, len(preMemBuffer)):
                     if preMemBuffer[i] != -1:
                         if des[index] == des[preMemBuffer[i]]:
                             issueMe = False
                             break #WAW HAZARD found

             if not isMemOp(index):
                 for i in range(0, len(preAluBuffer)):
                     if preAluBuffer[i] != -1:
                         if des[index] == des[preAluBuffer[i]]:
                             issueMe = False
                             break #WAW HAZARD found
             if isMemOp(index):
                 for i in range(0, len(preMemBuffer)):
                     if preMemBuffer[0] != -1:
                         if src1[index] == des[preMemBuffer[1]] or src2[index] == des[preMemBuffer[1]]:
                             issueMe = False
                             break #RAW HAZARD FOUND
             if not isMemOp(index):
                 for i in range(0, len(preAluBuffer)):
                     if preAluBuffer[0] != -1:
                         if src1[index] == des[preAluBuffer] or src2[index] == des[postAluBuffer[1]]:
                             issueMe = False
                             break
             if isMemOp(index):
                 for i in range(0, len(postMemBuffer)):
                     if postMemBuffer[0] != -1:
                         if src1[index] == des[postMemBuffer[1]] or src2[index] == des[postMemBuffer[1]]:
                             issueMe = False
                             break #RAW HAZARD FOUND
             if not isMemOp(index):
                 for i in range(0, len(postAluBuffer)):
                     if postAluBuffer[0] != -1:
                         if src1[index] == des[postAluBuffer] or src2[index] == des[postAluBuffer[1]]:
                             issueMe = False
                             break #RAW HAZARD FOUND

             for i in range(curr, len(preIssueBuffer)):
                 if preIssueBuffer[curr] == 1986 and preIssueBuffer[i] == 1984:
                     temp = preIssueBuffer[curr]
                     preIssueBuffer[curr] = preIssueBuffer[curr+1]
                     preIssueBuffer[curr+1] = temp
                     issueMe = False

             if issueMe:
                 numIssued += 1
                 #copy the instruction to app buffer
                 #the assumption here is that we have a -1 in the right spot! Think we will.
                 if isMemOp(index):
                     preMemBuffer[preMemBuffer.index(-1)] = index
                 else:
                     preAluBuffer[preAluBuffer.index(-1)] = index

                 #move the instruction in the pre issue buff down one level
                 preIssueBuffer[0:curr] = preIssueBuffer[0:curr]
                 print"pre" + str(preIssueBuffer[curr+1:])
                 preIssueBuffer[curr:3] = preIssueBuffer[curr+1:]# dropped 4, think will go to end always
                 preIssueBuffer[3] = -1
                 numInPreIssuedBuffer -= 1

             curr +=1




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


class Fetch_Unit():

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


    def getIndexOfMemAdress(address, bool):
        startingAddIndex = len(memory_pc) - len(data) - 1

        if bool == True:
            for i in range(0, memory_pc):
                if memory_pc[i] == address:
                    return i
        else:
            for i in range(0, memory_pc):
                if memory_pc[i] == address:
                    return i - startingAddIndex

    def run(self):

        #fetch two empty solts in the preissue buffer
        # fetchInstruction = [preIssueBuffer[0],preIssueBuffer[1]]
        index1 = getIndexOfMemAddress(pc, True)
        index2 = getIndexOfMemAddress(pc + 4, True)
        index1hit = False
        index2hit = False

        for i in range(0, 4):
            for j in range(0, 2):
                if cacheSets[i][j][3] == index1 or cacheSets[i][j][4] == index1:
                    index1hit = True
                    # we have a match

        #No Branch and non Branch Instruction feed the index into preIssueBuffer

                if cacheSets[i][j][4] == index1 or cacheSets[i][j][4] == index2:
                    index2hit = True
                    #we have a match

        if index1hit:
            #need to check for hazards
            # B instruction
            if 160 <= opcode[index1] <= 191:
                index2 = -1
                pc += arg1[index1] * 4
                return True
            # CBZ Instruction
            if 1440 <= opcode[index1] <= 1447:
                pass
            # CNBZ Instruction
            if 1448 <= opcode[index1] <= 1455:
                pass
            # BREAK
            if opcode[index1] == 2038:
                pass
            for n in range(0, preIssueBuffer):
                if n != -1:
                    preIssueBuffer[n] = index1
                    pc += 4
                    break
                else:
                    pass
            if index2hit:
                if 160 <= opcode[index2] <= 191:
                    index2 = -1
                    pc += arg1[index2] * 4
                    return True
                    # CBZ Instruction
                if 1440 <= opcode[index2] <= 1447:
                    pass
                    # CNBZ Instruction
                if 1448 <= opcode[index2] <= 1455:
                    pass
                for n in range(0, preIssueBuffer):
                    if n != -1:
                        preIssueBuffer[n] = index2
                        pc += 4
                        break
                    else:
                        pass

        elif index1hit == False:
            #accessing memory for index1
            access_memory(-1, index1, 1, index1, D.sim_instructionss[index1])
            if index2hit == False:
                access_memory(-1, index2, 1, index2, D.sim_instructionss[index2])

        return True


        #if the opcodeStr[i] is NOT in the cache, the cache unit will
        #fetch the instruction from memory and it will be in the cache at
        #the next clock cycle

        #if a branch instruction (B, CBZ, CNBZ) is fetched along with its next
        #instruction, the next instruction will be discarded
        #if branch instruction is fetched, the fetch unit will try to read all
        #the argument registers in order to calculate the target address

            #if registers are ready, or the target is immediate, the PC will be
            #updated at the end of the cycle. (MOV and MOVK)
            #Otherwise, the fetch unit stalls until all arguments registers are avliable
        #
        # if opcodeStr[i] == "NOP" or "BREAK" or "B":
        #     #Fetch will handle this here
        #     pass
        # if preIssueBuffer[0] == -1:
        #     preIssueBuffer[0] = opcodeStr[i]
        #     #send instruction to cache to check if it's in there
        #     #if we are returned with a hit determine if its a branch or B instructions
        #     #if branch instruction will check for hazards and if none perform branch
        #     #B is done without checking





class Cache:
    def __init__(self):
        global tag
        global memory_pc
        global setNum
        global wbAddr
        global data1
        global data2

        pass

    def getIndexOfMemAdress(address, bool):
        startingAddIndex = len(memory_pc) - len(data) - 1

        if bool == True:
            for i in range(0, memory_pc):
                if memory_pc[i] == address:
                    return i
        else:
            for i in range(0, memory_pc):
                if memory_pc[i] == address:
                    return i - startingAddIndex

    def run(self):
        pass

    def flush(self):
        #writes out all dirty blocks to memory at the conclusion of execution
        pass

    def access_memory(self, memIndex, instructionIndex, isWriteToMem, dataToWrite):
        hit = False
        miss = False

        if(memIndex == _-1):
            addressLocal = 96 (4 * instructionIndex)
        else:
            addressLocal = 96 (4 * len(opcode) + 1) + (4 * memIndex)

        if memory_pc % 8 == 0:
            dataWord = 0  # block 0 was the address
            address1 = memory_pc
            address2 = memory_pc + 4
            # check for "alignment"
            # this picks the second word as address so we need to fix it
            # set address1 - block 1 address to address - 4
        if memory_pc % 8 != 0:
            dataWord = 1  # block 1 was the address
            address1 = memory_pc - 4
            address2 = memory_pc

        if address1 < 96 + (4 * numInstructions):
            data1 = D.sim_instructionss[getIndexOfMemAdress(address1,False)]
        else:
            data1 = data[getIndexOfMemAddress(address1, False)]

        if address2 < 96 + (4 * numInstructions):
            data1 = D.sim_instructionss[getIndexOfMemAdress(address1,False)]
        else:
            data1 = data[getIndexOfMemAddress(address1, False)]

        if isWriteToMem and dataToWrite == 0:
            data1 = dataToWrite

        elif isWriteToMem and dataWord == 1:
            data2 = dataToWrite

        setNum = (address1 & self.setMask) >> 3
        tag = (address1 & self.tagMask) >> 5

        if(self.cacheSets[setNum][0][0] == 1 and self.cacheSets[setNum][0][2] == tag):
            hit =True
            assocblock = 0

        elif self.cacheSets[setNum][1][0] == 1 and self.cacheSets[setNum][1][2] == tag:
            hit = True
            assocblock = 1

        if(hit):
            if hit and isWriteToMem:
                self.cacheSets[setNum][assocblock] = 1 #dirty bit
                self.lruBit[setNum] = (assocblock + 1) % 2  # lru bit
                self.cacheSets[setNum][assocblock][dataWord + 3] = dataToWrite  # +3
            elif hit:
                self.lrubit[setNum] = (assocblock + 1) % 2

            return[True, self.cacheSets[setNum][assocblock][dataWord+3]]
        if address1 in self.justMissedList:
            while(self.justMissedList.count(address1) > 0):
                self.justMissedList.remove(address1)

        if self.cacheSets[setNum][self.lruBit[setNum]][1] == 1:
            wbAddr = self.cacheSets[setNum][self.lruBit[setNum]][2]  # tag
            # modify tag to get back to the original address, remember all addresses are inherently word aligned
            # lower 2 bits are zero !!!!
            wbAddr = (wbAddr << 5) + (setNum << 3)

        if (wbAddr >= (len(opcode)+ 1 * 4) + 96):
            data[getIndexOfMemAddress(wbAddr, False)] = self.cacheSets[setNum][self.lruBit[setNum]][3]
        if (wbAddr + 4 >= (sim.numInstructions * 4) + 96):
            data[getIndexOfMemAddress(wbAddr + 4, False)] = self.cacheSets[setNum][self.lruBit[setNum]][4]

        self.cacheSets[setNum][self.lruBit[setNum]][0] = 1  # valid  we are writing a block
        self.cacheSets[setNum][self.lruBit[setNum]][1] = 0  # reset the dirty bit
        if (isWriteToMem):
            self.cacheSets[setNum][self.lruBit[setNum]][
                1] = 1  # dirty if is data mem is dirty again, instruction mem never dirty
            # update both words in the actual cache block in set
            self.cacheSets[setNum][self.lruBit[setNum]][2] = tag  # tag
            self.cacheSets[setNum][self.lruBit[setNum]][3] = data1  # data
            self.cacheSets[setNum][self.lruBit[setNum]][4] = data2  # nextData
            self.lruBit[setNum] = (self.lruBit[setNum] + 1) % 2  # set lru to show block is recently used  1 means block 0 MRU and 0 means block 1 MRU

            return [True, self.cacheSets[setNum][(self.lruBit[setNum] + 1) % 2][dataWord + 3]]
        else:
            # VALID MISS on cycle
            # add the memory address to the just missed list
            if (self.justMissedList.count(address1) == 0):
                self.justMissedList.append(address1)
            return [False, 0]





print preIssueBuffer
print opcodeStr
