A set of utilities for interfacing with a M48Z128-85PM1 battery-backed SRAM chip that has been used in The Grid by Midway. This is the chip that stores all of the player profiles so that players can track their statistics, name and call name across different games. The ``ArduinoSRAMReader`` directory contains an Arduino sketch that can interface with the ``dump.py`` utility inside the ``GridUtilities`` directory. When used together, an SRAM chip can be partially or fully read or written. The ``print.py`` utility takes a dumped 128KB SRAM file (or a MAME ``nvram`` file) and prints profiles contained in it. The ``editor.py`` utility presents a curses interface where you can add, edit and delete profiles from an SRAM file (or a MAME ``nvram`` file). The ``util.py`` utility contains helpful functions for combining split ROM files and byteswapping binary data.

All of the scripts require Python 3.6 or greater due to their use of type hints. The ``editor.py`` script additionally requires that [dragoncurses](https://github.com/DragonMinded/dragoncurses) be installed. All utilites are meant to be run from the commandline and all utilities include help. Edited profiles are fully compatible with both the emulated MAME release of The Grid as well as actual arcade hardware. If everything is working correctly, it should take about a minute to dump a full SRAM chip and about a minute and a half to write a full SRAM chip.

## Arduino Schematic for Real Hardware

The following is a simple schematic that I built in order to edit profiles on an SRAM chip that I had in my posession. I've connected the 8 bidirectional data lines directly to 8 Arduino pins. I've connected two Arduino pins through inverters to the write enable and output enable lines to programatically select read/write mode. I've connected two Arduino pins to three serial to parallel shift registers in order to drive the necessary 17 address lines from two Arduino pins. If you use the same Arduino line, tied directly to the output enable line, and through an inverter to the write enable line (ensuring startup defaults to read), you can probably get away with using only two shift registers and tying A16 directly to the unused Arduino pin. I have not tested this. I have not included decoupling capacitors or a power supply. I recommend 0.1uF decoupling capacitors for each chip including the M48Z128. The datasheet for the SRAM also recommends a 1N5817 diode connected between its VCC and GND pins to protect against data loss when powering the chip. You should be able to take +5V and GND from the Arduino and it will supply enough voltage. I assume that you can either build your own CMOS inverters using BJTs or use a 7400 series inverter chip such as a quad NAND gate with both inputs tied together for each gate. When referring to a free floating pin, this indicates a connection to an Arduino Uno pin. In order to make an ASCII diagram possible, connections between the 74LS164 shift registers handling the address logic and the M48Z128 chip are not drawn. Instead they are labelled. It goes without saying but if you use an external PSU to provide +5V, connect the grounds from the Arduino, all of the ground points in the diagram, and the PSU.


                                                        o +5V pin
                           +-----------------------+    |
                           |1  NC            VCC 32|----/
      74LS164 3 Qa (3)-----|2  A16           A15 31|-----74LS164 2 Qh (13)
     74LS164 2 Qg (12)-----|3  A14            NC 30|                                           /|
     74LS164 2 Qe (10)-----|4  A12            !W 29|-----------------------------------------o |-----o Pin 12
     74LS164 1 Qh (13)-----|5  A7      M     A13 28|-----74LS164 2 Qf (11)                     \|
     74LS164 1 Qg (12)-----|6  A6      4      A8 27|-----74LS164 2 Qa (3)
     74LS164 1 Qf (11)-----|7  A5      8      A9 26|-----74LS164 2 Qb (4)
     74LS164 1 Qe (10)-----|8  A4      Z     A11 25|-----74LS164 2 Qd (6)                      /|
      74LS164 1 Qd (6)-----|9  A3      1      !G 24|-----------------------------------o |-----o Analog Pin 2
      74LS164 1 Qc (5)-----|10 A2      2     A10 23|-----74LS164 2 Qc (5)                      \|
      74LS164 1 Qb (4)-----|11 A1      8      !E 22|----------------o GND (chip always enbled)
      74LS164 1 Qa (3)-----|12 A0            DQ7 21|-----o Pin 9
               Pin 2 o-----|13 DQ0           DQ6 20|-----o Pin 8
               Pin 3 o-----|14 DQ1           DQ5 19|-----o Pin 7
               Pin 4 o-----|15 DQ2           DQ4 18|-----o Pin 6
                      /----|16 GND           DQ3 17|-----o Pin 5
                      |    +-----------------------+
              GND pin o
   
                                   74LS164 1         o +5V pin
                              +-----------------+    |
                 Pin 10 o-----|1  A       VCC 14|----/
     +5V pin o----------------|2  B        Qh 13|-----A7 (5) and 74LS164 2 A (1)
                  A0 (12)-----|3  Qa       Qg 12|-----A6 (6)
                  A1 (11)-----|4  Qb       Qf 11|-----A5 (7)
                  A2 (10)-----|5  Qc       Qe 10|-----A4 (8)
                   A3 (9)-----|6  Qd     !CLR  9|---------------o +5V pin
                         /----|7  GND     CLK  8|-----o Pin 11
                         |    +-----------------+
                 GND pin o
   
                                   74LS164 2         o +5V pin
                              +-----------------+    |
        74LS164 1 Qh (13)-----|1  A       VCC 14|----/
     +5V pin o----------------|2  B        Qh 13|-----A15 (31) and 74LS164 3 A (1)
                  A8 (27)-----|3  Qa       Qg 12|-----A14 (3)
                  A9 (26)-----|4  Qb       Qf 11|-----A13 (28)
                 A10 (23)-----|5  Qc       Qe 10|-----A12 (4)
                 A11 (25)-----|6  Qd     !CLR  9|---------------o +5V pin
                         /----|7  GND     CLK  8|-----o Pin 11
                         |    +-----------------+
                 GND pin o
   
                                   74LS164 3         o +5V pin
                              +-----------------+    |
      74LS164 2 Qh (13) o-----|1  A       VCC 14|----/
     +5v pin o----------------|2  B        Qh 13|
                  A16 (2)-----|3  Qa       Qg 12|
                              |4  Qb       Qf 11|
                              |5  Qc       Qe 10|
                              |6  Qd     !CLR  9|---------------o Connect to +5v to disable
                         /----|7  GND     CLK  8|-----o Pin 11
                         |    +-----------------+
                 GND pin o

## PCB and KiCad Schematic

If you don't want to hand-wire a circuit, I have tested out an Arduino shield board that you can have manufactured and then assemble yourself. If you just want to get a board manufactured, check out https://oshpark.com/shared_projects/tCR4N9Gb which has the BOM as well as the board laid out and ready to be ordered. You will still need to assemble the board yourself which requires some soldering experience. For the source files (made in KiCad), check out the `Board/` folder.
