const unsigned long MEM_SIZE = 0x20000L;
const unsigned int STATUS_LED = 13;

unsigned char read_byte() {
  // Loop forever until we read a byte
  while(!Serial.available());

  // Grab a byte, return it
  return (unsigned char)(Serial.read() & 0xFF);
}

void return_general_error(char * str) {
  Serial.print("NG");
  Serial.print(str);
  Serial.write(0);
  Serial.flush();
}

void return_address_error(char * name, unsigned long address) {
  Serial.print("NG");
  Serial.print(name);
  Serial.print(" address ");
  Serial.print(address);
  Serial.print(" out of bounds!");
  Serial.write(0);
  Serial.flush();
}

void send_success() {
  Serial.print("OK");
  Serial.flush();
}

void send_continue() {
  Serial.print("CO");
  Serial.flush();
}

void read_and_execute_command() {  
  // First, sync to any start of message
  if(read_byte() != 'S') { return; }
  if(read_byte() != 'R') { return; }
  if(read_byte() != 'A') { return; }
  if(read_byte() != 'M') { return; }
  
  // Now, grab the instruction
  unsigned int instruction = read_byte();
  
  if (instruction == 'R') {
    // Read a chunk of memory, specified by start and end address
    unsigned long startaddr = ((long)read_byte() << 16) | ((long)read_byte() << 8) | (long)read_byte();
    unsigned long endaddr = ((long)read_byte() << 16) | ((long)read_byte() << 8) | (long)read_byte();
    
    if (startaddr >= MEM_SIZE) {
      return_address_error("Starting", startaddr);
      return;
    }
    if (endaddr > MEM_SIZE) {
      return_address_error("Ending", endaddr);
      return;
    }
    if (startaddr >= endaddr) {
      return_general_error("Address bounds out of order!");
      return;
    }
    
    // Valid command, send response along with data
    send_continue();
    
    int cont = 0;
    for (unsigned long addr = startaddr; addr < endaddr; addr++) {
      if (cont % 32 == 0) {
        if(read_byte() != 'C') {
          return_general_error("Unexpected continuation from client!");
          return;
        }
        if(read_byte() != 'O') {
          return_general_error("Unexpected continuation from client!");
          return;
        }
      }
      cont++;
      
      // TODO: Read from chip
      Serial.write(addr & 0xff);          
    }
    
    // Finished reading
    send_success();
    return;
  }
  
  if (instruction == 'W') {
    // Write a chunk of memory, specified by start and end address
    unsigned long startaddr = ((long)read_byte() << 16) | ((long)read_byte() << 8) | (long)read_byte();
    unsigned long endaddr = ((long)read_byte() << 16) | ((long)read_byte() << 8) | (long)read_byte();
        
    if (startaddr >= MEM_SIZE) {
      return_address_error("Starting", startaddr);
      return;
    }
    if (endaddr > MEM_SIZE) {
      return_address_error("Ending", endaddr);
      return;
    }
    if (startaddr >= endaddr) {
      return_general_error("Address bounds out of order!");
      return;
    }
    
    int cont = 0;
    for (unsigned long addr = startaddr; addr < endaddr; addr++) {
      // Flow control
      if (cont % 32 == 0) {
        send_continue();
      }
      cont++;
      
      // TODO: Write to chip
      unsigned char byteval = read_byte();
    }

    // Finished writing!
    send_success();
    
    return;
  }
  
  if (instruction == 'S') {
    // Status ping
    send_success();
    
    return;
  }
  
  return_general_error("Unknown command!");
}

void setup() {
  // initialize serial:
  Serial.begin(230400);
  pinMode(STATUS_LED, OUTPUT);     
  
}

void loop() {
  digitalWrite(STATUS_LED, LOW);   // turn the LED on (HIGH is the voltage level)
  delay(100);               // wait for a second
  digitalWrite(STATUS_LED, HIGH);    // turn the LED off by making the voltage LOW
  read_and_execute_command();
}








