
   Authors:    Alexander Gonzalez: a_g1593@txstate.edu
               Henry Ruiz: h_r32@txstate.edu
   
   Class: Computer Architecture
   
   Class #: CS 3339
   
# Arm-Dissembler
Arm Simulator is a python based program that reads in ARM Machine code, generates Assembly code for the given ARM code,
and simulates pc counter.



## Installation
There are no installation requirements.

## Usage
In order to use the Arm-Dissembler you will need to enter your input and output files as an argument in the terminal.

```
python dissasembler.py -i "test9_bin.txt" -o "team13_out_dist.txt" -o "team13_out.sim.txt"
````

The program will then read in the ARM Code from the input file and generate Assembly code into the output file.

## Notes
The input file needs to be a file containing 32 bit ARM machine code in order for the program to function properly.
If you want to test the code for yourself, please feel free to copy the ARM code below into a text file and test the program for yourself!

```
00010100000000000000000000000001
10010001000000000000000000000001
10110100000000000000000000100001
11010001000000000001000000000001
10110101000000000000000000100001
11111110110111101111111111100111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
11111111111111111111111111111111
```
## TO DO LIST
get registers to output correct data & get data to be printed correctly