// EEPROM Programmer
// Mark Anderson
// June 4th, 2019
//
// Quick & dirty EEPROM programmer using shift registers
// Reads/Writes to ROM

#define CE 10
#define OE 11
#define WE 12
#define SHIFT_DATA 2
#define SHIFT_CLK 3
#define SHIFT_LATCH 4

#define READMEM 0xFA
#define WRITEMEM 0xFB
#define SUCCESS 0x01

#define ROM_SIZE 8

// Shift register usage
void setAddr(int addr, bool outputEnable){
	shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, (addr >> 8) | (outputEnable ? 0x00 : 0x80));
	shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, addr);

	// May need to add delay in here but digitalWrite may be slow enough
	digitalWrite(SHIFT_LATCH, LOW);
	digitalWrite(SHIFT_LATCH, HIGH);
	digitalWrite(SHIFT_LATCH, LOW);
}

// Read one byte at a time
byte readEEPROM(int addr){
    DDRD &= 0x00;
	setAddr(addr, true);
    digitalWrite(CE, LOW);
    digitalWrite(OE, LOW);
	byte data = PIND;
    digitalWrite(CE, HIGH);
    digitalWrite(OE, HIGH);
	return data;
}

// Read a block of memory
void readMem(){
    while (Serial.available < 3) {} // Wait for serial buffer
    
    int addr = (Serial.read() << 8); // High byte address
    addr |= Serial.read(); // Low byte address

    int count = Serial.read();
    for (int i = 0; i < count; i++){
        byte data = readEEPROM(addr);
        Serial.write(data);
        addr ++;
    }
}

// Write to ROM
void writeMem(){
    static int ledState = LOW;

    while (Serial.available() < 3) {} // Wait for buffer

    int addr = (Serial.read() << 8); // High byte address
    addr |= Serial.read(); // Low byte address
    int count = Serial.read();
    byte data;

    while (Serial.available() < count) {} // Wait for buffer

    for (int i = 0; i < count; i++){
        setAddr(addr);
        DDRD |= 0xFF;

        b = Serial.read();
        PORTD = b;
        digitalWrite(WE, LOW);
        digitalWrite(CE, LOW);
        digitalWrite(WE, HIGH);
        digitalWrite(CE, LOW);
        DDRD &= 0x00;
        addr++;
    }

    while (readByte(addr-1) != b) {}

    digitalWrite(13, ledState);
    ledState = (ledState == HIGH) ? LOW : HIGH;

    Serial.write(SUCCESS);
}

void error(){
    for(;;){
        digitalWrite(13, HIGH);
        delay(500);
        digitalWrite(13, LOW);
        delay(500);
    }
}

void setup(){
	// Set control pins as outputs
    pinMode(CE, OUTPUT);
    pinMode(OE, OUTPUT);
	pinMode(WE, OUTPUT);
	pinMode(SHIFT_DATA, OUTPUT);
	pinMode(SHIFT_CLK, OUTPUT);
	pinMode(SHIFT_LATCH, OUTPUT);
    
    digitalWrite(CE, HIGH);
    digitalWrite(OE, HIGH);
	digitalWrite(WE, HIGH);

	// Initialise Serial
    Serial.begin(38400);

    // Status LED
    digitalWrite(13, HIGH);
}

void loop(){
    if (Serial.available() > 0){
        byte in = Serial.read(); // Command byte
        switch(in){
            case readMem:
                readMem();
                break;
            case writeMem:
                writeMem();
                break;
            default:
                error();
         }
    }
}
