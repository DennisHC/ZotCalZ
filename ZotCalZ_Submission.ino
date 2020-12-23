#include "rgb_lcd.h"

// Declaring Global Variables
float weight_reading = 0;

// SCALE/LOADCELL Library and Variables
#include "HX711.h"
#define LOADCELL_DOUT_PIN  3
#define LOADCELL_SCK_PIN  2
#define calibration_factor 446 // 205,000 for lbs | 445-446 for g
HX711 scale;


// ESP Wi-Fi Module Library
#include <SoftwareSerial.h>
#include "WiFiEsp.h"

// dtostrf Library
#include <stdio.h>

// Emulate Serial1 on pins 6/7 if not present
#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"
SoftwareSerial Serial1(10, 11); // RX, TX
#endif

// Initialize ESP Wi-Fi Module
// SoftwareSerial ESPserial(10, 11); // RX | TX
// Initialize the Ethernet client object
WiFiEspClient client;

// Not real values representative of sensitive data
char ssid[] = "MyNetwork"; // your network SSID (name)
char pass[] = "My Password"; // your network password
int status = WL_IDLE_STATUS; // the Wifi radio's status
char server[] = "My EC2 AWS Instance"; //
char var[100] = "weight_in_grams";
char get_request[200];


void setup() 
{
  Serial.begin(115200); // Set baudrate

  // Initialize Serial for ESP Module
  Serial1.begin(115200); // communication with the host computer

  // WiFi: Start the software serial for communication with the ESP8266
  WiFi.init(&Serial1);
  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) 
  {
    Serial.println("WiFi shield not present");
    // don't continue
    while (true);
  }

  // Reminders to self to setup program
  Serial.println("");
  Serial.println("Remember to to set Both NL & CR in the serial monitor.");
  Serial.println("Ready");
  Serial.println("");

  // Attempt to connect to WiFi network
  while ( status != WL_CONNECTED) 
  {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);

    // Connect to WPA/WPA2 network
    status = WiFi.begin(ssid, pass);
  }
  Serial.println("You're connected to the network");
  printWifiStatus();
  
  //------------------[LOAD CELL / SCALE]------------------------------- 
  Serial.println("HX711 calibration sketch");
  Serial.println("Remove all weight from scale");

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale();
  scale.tare(); //Reset the scale to 0
  
  long zero_factor = scale.read_average(); //Get a baseline reading
  Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
  Serial.println(zero_factor);

  scale.set_scale(calibration_factor); //Adjust to this calibration factor
  //-----------------------------------------------------------------
}

void loop() 
{
  //------------------[Weight Reading]------------------------------- 
  Serial.print("Weight Reading: ");
  weight_reading = scale.get_units();
  // If the weight_reading is negative, print 0
  if (weight_reading < 0) 
  {
    weight_reading = 0;
  }
  Serial.print(weight_reading, 2); // 2nd Param is Precision
  Serial.print(" g");
  Serial.println();
  //-----------------------------------------------------------------

  
  if (!client.connected())
  {
    Serial.println("Starting connection to server...");
    client.connect(server, 5000);
  }

  // Printing to Console in Server
  Serial.println("Connected to server");

  dtostrf(weight_reading, 4, 2, var);

  
  // Make a HTTP request (Host: IP-Address not representative of real values now after project completion)
  sprintf(get_request,"GET /?var=%s HTTP/1.1\r\nHost: 00.00.0.000\r\nConnection: close\r\n\r\n", var);
  client.print(get_request);
  delay(500);
  
  while (client.available()) 
  {
    char c = client.read();
    Serial.write(c);
  }
  
  // Delay is needed or causes problems in GET Requests
  delay(20000);
}


void printWifiStatus()
{
  // print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength
  long rssi = WiFi.RSSI();
  Serial.print("Signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}