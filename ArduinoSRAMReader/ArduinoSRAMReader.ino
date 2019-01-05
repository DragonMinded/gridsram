const unsigned long MEM_SIZE = 0x20000L;
const unsigned int STATUS_LED = 13;
const unsigned int DQ0 = 2;
const unsigned int DQ1 = 3;
const unsigned int DQ2 = 4;
const unsigned int DQ3 = 5;
const unsigned int DQ4 = 6;
const unsigned int DQ5 = 7;
const unsigned int DQ6 = 8;
const unsigned int DQ7 = 9;

const unsigned int SERDAT = 10;
const unsigned int SERCLK = 11;

void read_mode() {
  pinMode(DQ0, INPUT);
  pinMode(DQ1, INPUT);
  pinMode(DQ2, INPUT);
  pinMode(DQ3, INPUT);
  pinMode(DQ4, INPUT);
  pinMode(DQ5, INPUT);
  pinMode(DQ6, INPUT);
  pinMode(DQ7, INPUT);
}

void add_address_bit(unsigned long val) {
  digitalWrite(SERCLK, LOW);
  digitalWrite(SERDAT, val ? HIGH : LOW);
  delayMicroseconds(1);
  digitalWrite(SERCLK, HIGH);
  delayMicroseconds(1);
  digitalWrite(SERCLK, LOW);
}

unsigned char read_sram(unsigned long address) {
  for(unsigned int i = 0; i < 24; i++) {
    add_address_bit((address >> (23 - i)) & 0x1);
  }

  delayMicroseconds(1);

  return (
    ((digitalRead(DQ0) == HIGH) ? 0x01 : 0) |
    ((digitalRead(DQ1) == HIGH) ? 0x02 : 0) |
    ((digitalRead(DQ2) == HIGH) ? 0x04 : 0) |
    ((digitalRead(DQ3) == HIGH) ? 0x08 : 0) |
    ((digitalRead(DQ4) == HIGH) ? 0x10 : 0) |
    ((digitalRead(DQ5) == HIGH) ? 0x20 : 0) |
    ((digitalRead(DQ6) == HIGH) ? 0x40 : 0) |
    ((digitalRead(DQ7) == HIGH) ? 0x80 : 0)
  );
}

void write_mode() {
  pinMode(DQ0, INPUT);
  pinMode(DQ1, INPUT);
  pinMode(DQ2, INPUT);
  pinMode(DQ3, INPUT);
  pinMode(DQ4, INPUT);
  pinMode(DQ5, INPUT);
  pinMode(DQ6, INPUT);
  pinMode(DQ7, INPUT);
}

unsigned char read_serial() {
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
  if(read_serial() != 'S') { return; }
  if(read_serial() != 'R') { return; }
  if(read_serial() != 'A') { return; }
  if(read_serial() != 'M') { return; }
  
  // Now, grab the instruction
  unsigned int instruction = read_serial();
  
  if (instruction == 'R') {
    // Read a chunk of memory, specified by start and end address
    unsigned long startaddr = ((long)read_serial() << 16) | ((long)read_serial() << 8) | (long)read_serial();
    unsigned long endaddr = ((long)read_serial() << 16) | ((long)read_serial() << 8) | (long)read_serial();
    
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

    // Put data lines into read mode
    read_mode();
    
    // Valid command, send response along with data
    send_continue();
    
    int cont = 0;
    for (unsigned long addr = startaddr; addr < endaddr; addr++) {
      if (cont % 32 == 0) {
        if(read_serial() != 'C') {
          return_general_error("Unexpected continuation from client!");
          return;
        }
        if(read_serial() != 'O') {
          return_general_error("Unexpected continuation from client!");
          return;
        }
      }
      cont++;
      
      // Read from chip, output to PC.
      Serial.write(read_sram(addr));
    }
    
    // Finished reading
    send_success();
    return;
  }
  
  if (instruction == 'W') {
    // Write a chunk of memory, specified by start and end address
    unsigned long startaddr = ((long)read_serial() << 16) | ((long)read_serial() << 8) | (long)read_serial();
    unsigned long endaddr = ((long)read_serial() << 16) | ((long)read_serial() << 8) | (long)read_serial();
        
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
    
    // Put data lines into write mode
    write_mode();

    int cont = 0;
    for (unsigned long addr = startaddr; addr < endaddr; addr++) {
      // Flow control
      if (cont % 32 == 0) {
        send_continue();
      }
      cont++;
      
      // TODO: Write to chip
      unsigned char byteval = read_serial();
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

  // Initialize LED
  pinMode(STATUS_LED, OUTPUT);
  
  // Initialize address logic
  pinMode(SERCLK, OUTPUT);
  pinMode(SERDAT, OUTPUT);
  digitalWrite(SERCLK, LOW);
  digitalWrite(SERDAT, LOW);
}

void loop() {
  // Show some activity
  digitalWrite(STATUS_LED, LOW);
  delay(100);
  digitalWrite(STATUS_LED, HIGH);

  // Wait for command
  read_and_execute_command();
}
