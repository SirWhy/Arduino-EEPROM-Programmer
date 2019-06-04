// EEPROM Programmer
// Mark Anderson
// June 4th, 2019
//
// Quick & dirty EEPROM programmer using shift registers
// Reads/Writes to ROM

#define WE 13
#define SHIFT_DATA 2
#define SHIFT_CLK 3
#define SHIFT_LATCH 4
#define D0 5
#define D7 12

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
	for (int pin = D0; pin <= D7; pin++){
		pinMode(pin, INPUT); // Set pins for reading
	}
	setAddr(addr, true);
	byte data = 0;
	for (int pin = D7; pin >= D0; pin--){
		data = (data << 1) + digitalRead(pin); // Read each pin individually
	}
	return data;
}

void setup(){
	// Set control pins as outputs
	pinMode(WE, OUTPUT);
	pinMode(SHIFT_DATA, OUTPUT);
	pinMode(SHIFT_CLK, OUTPUT);
	pinMode(SHIFT_LATCH, OUTPUT);
	digitalWrite(WE, HIGH);

	// Read EEPROM
	
}

void loop(){
	// nothing here yet
	// need to add serial comms
}
