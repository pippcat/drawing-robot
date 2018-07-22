/* Drawing Robot
 by Tommy (sendyourspamhere@posteo.de)

 This sketch uses an Arduino to control 3 servo motors which reassemble a human arm
 It needs an black and white image as input and will paint this image using a pen attached to the robot arm
*/

#include <Servo.h> // library to control the servos

Servo innerarm;  // create servo object to control a servo
int innerpos = 0;    // variable to store the servo position

Servo outerarm;  // create servo object to control a servo
int outerpos = 0;    // variable to store the servo position

Servo pen;  // create servo object to control a servo
int penpos = 0;    // variable to store the servo position

int pos = 0;

void setup() {
  innerarm.attach(8);  // Servo to move inner arm is at PIN#8 (min delay: 15ms)
  outerarm.attach(9);  // Servo to move outer arm is at PIN#9 (min delay: 5ms)
  pen.attach(7);  // Servo to move Pen up and down is at PIN#7 (min delay: 5ms)
}

void loop() {
  for (pos = 45; pos <= 135; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    innerarm.write(innerpos);              
    outerarm.write(outerpos);              
    pen.write(penpos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 135; pos >= 45; pos -= 1) { // goes from 180 degrees to 0 degrees
    innerarm.write(innerpos);              
    outerarm.write(outerpos);              
    pen.write(penpos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
}
    
