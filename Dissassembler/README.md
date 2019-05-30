
   Authors: Alexander Gonzalez: a_g1593@txstate.edu
            Henry Ruiz: h_r32@txstate.edu
   Class: Computer Architecture
   Class #: CS 3339.
# Arm-Dissembler
Arm Dissembler is a python based program that reads in ARM Machine code and generates Assembly code for the given ARM code.


## Installation
There are no installation requirements.

## Usage
In order to use the Arm-Dissembler you will need to enter your input and output files as an argument in the terminal.

```
python dissasembler.py -i "test3_bin.txt" -o "team13_out_dist.txt"
````

The program will then read in the ARM Code from the input file and generate Assembly code into the output file.

## Notes
The input file needs to be a file containing 32 bit ARM machine code in order for the program to function properly.
If you want to test the code for yourself, please feel free to copy the ARM code below into a text file and test the program for yourself!

```
10001011000000100000000000100011
11001011000000100000000000100011
10001010000000100000000000100011
10101010000000100000000000100011
00010100000000000010011100010000
10010001000001100100000001000001
11010001000001100100000001000001
11111000010001100100000001000001
11111000000001100100000001000001
10110100000000000000000001110011
10110101000000000000000001110011
11010010100000000001111111100001
11110010111111111110000000000010
11010011010000000001000000100000
11010011011000000001000000100000
11111110110111101111111111100111
11111111111111111111111111111111
11111111111111111111111111111110
11111111111111111111111111111101
```
