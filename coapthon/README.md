# CoAP Fuzzer Instructions
### To run our fuzzer for the CoAP application:
1. Place all the files in this repository's 'coapthon' folder into the 'CoAPthon' folder provided in the course project.
2. Assuming you have already built CoAPthon in your system, open a terminal and run the following commands:
   
   _sudo apt install gdb_

   _sudo gdb -ex run -ex backtrace --args python2 coapserver.py -i 127.0.0.1 -p 5683_

3. Next, with this terminal running, open a new terminal and run:

   _coverage run simple_fuzzing.py_

   You should be able to see the fuzzer running now.

5. The fuzzer output is saved in a file called error.txt that will appear in the CoAPthon folder.

   (Before you run the file simple_fuzzing.py again, make sure to clear this output text file first.)
