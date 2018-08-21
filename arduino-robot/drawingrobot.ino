/* Drawing Robot
 by Tommy (sendyourspamhere@posteo.de)

 This sketch uses an Arduino to control 3 servo motors which reassemble a human arm
 It needs an black and white image as input and will paint this image using a pen attached to the robot arm
*/

#include <Servo.h> // library to control the servos

Servo innerarm;  // create servo object to control a servo
Servo outerarm;  // create servo object to control a servo
Servo pen;  // create servo object to control a servo

String inputString = "";         // a String to hold incoming data
boolean stringComplete = false;  // whether the string is complete

int pos = 0; // counter for loops
int innerpos = 0; // position of inner arm
int outerpos = 0; // position of outer arm
//bool penstate = false; // false = pen up, true = pen down
bool arm = false; // false = inner arm; true = outer arm

void setup() {
  Serial.begin(9600);   // initialize serial
  inputString.reserve(200);  // reserve 200 bytes for the inputString
  pen.attach(7);  // Servo to move Pen up and down is at PIN#7 (min delay: 5ms)
  pen.write(60); // pen up
  innerarm.attach(8);  // Servo to move inner arm is at PIN#8 (min delay: 15ms)
  innerarm.write(90); // starting position
  outerarm.attach(9);  // Servo to move outer arm is at PIN#9 (min delay: 5ms)
  outerarm.write(90); // starting position
  
}

void loop() {
  if (stringComplete) { // print the string when a newline arrives:
    Serial.println(inputString);
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
 // pen.write(110);
  //penmover(true);
 // movearm(120, false);
 // movearm(60, true);
  //penmover(false);
 // pen.write(90);
 // movearm(90, true);
 // movearm(90, false);
}

// function lifts / sets down the pen
void penmover(bool penstate) {
  if (penstate == true) {
    for (pos = 90; pos <= 110; pos += 1) {
      pen.write(pos);
      delay(50);
    }
    //penstate = false;
  }
  if (penstate == false) {
    for (pos = 110; pos >= 90; pos -= 1) {
      pen.write(pos);
      delay(50);
    }
    //penstate = true;
  }
}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

// function moves arm to new position
void movearm(int newpos, bool arm) {
  if (arm == false) {
    if (innerpos < newpos) {
      for (pos = innerpos; pos <= newpos; pos+=1) {
        innerarm.write(pos);
        delay(50);
      }
    }
    if (innerpos > newpos) {
      for (pos = innerpos; pos >= newpos; pos-=1) {
        innerarm.write(pos);
        delay(50);
      }
    }
    innerpos = newpos;
  }
  if (arm == true) {
    if (outerpos < newpos) {
      for (pos = outerpos; pos <= newpos; pos+=1) {
        outerarm.write(pos);
        delay(50);
      }
    }
    if (outerpos > newpos) {
      for (pos = outerpos; pos >= newpos; pos-=1) {
        outerarm.write(pos);
        delay(50);
      }
    }
    outerpos = newpos;
  }
 
}

    
