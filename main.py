###############################################################################
# Mini Web Server
#
# Created by Zerynth Team 2015 CC
# Authors: G. Baldi, D. Mazzei
###############################################################################
# webserver+weather No threads
#
# Thanks to Zerynth Team 2015 CC
# Author: Vikas Reddy @ vikaskichik@gmail.com
#
# Device: ESP32 Dev Kit V1
###############################################################################


# import streams & socket
import streams
import socket

# import json parser, will be needed later
import json

# import the wifi interface
from wireless import wifi

# import the http module
import requests

# the wifi module needs a networking driver to be loaded
# in order to control the board hardware.
# FOR THIS EXAMPLE TO WORK, A NETWORK DRIVER MUST BE SELECTED BELOW

# uncomment the following line to use the CC3000 driver (Particle Core or CC3000 Wifi shields)
# from texas.cc3000 import cc3000 as wifi_driver

# uncomment the following line to use the BCM43362 driver (Particle Photon)
# from broadcom.bcm43362 import bcm43362 as wifi_driver
from espressif.esp32net import esp32wifi as wifi_driver

streams.serial()

new_resource("index.html")

print("Device booted up.....Enjoy")

# init the wifi driver!
# The driver automatically registers itself to the wifi interface
# with the correct configuration for the selected board
wifi_driver.auto_init()
# use the wifi interface to link to the Access Point
# change network name, security and password as needed
print("Connecting to Wifi Access Point...")
try:
    # FOR THIS EXAMPLE TO WORK, "Network-Name" AND "Wifi-Password" MUST BE SET
    # TO MATCH YOUR ACTUAL NETWORK CONFIGURATION
    wifi.link("Tuppu",wifi.WIFI_WPA2,"qualcomm123")
except Exception as e:
    print("ooops, something wrong while conecting to Wifi Access Point:(", e)
    while True:
        sleep(1000)

# Yes! we are connected
print("Connected to Wifi!")

# Let's print our ip, it will be needed soon
info = wifi.link_info()
print("My IP is:",info[0])


api_key = "bd4ba90e2b397e24a925e436a9d8fed9"
        
for i in range(3):
    try:
        print("Retrieving Hyderabad,IN weather information----->")
        # to get weather info you need to specify a correct api url
        # there are a lot of different urls with different functions
        # they are all documented here http://openweathermap.org/api
        
        # let's put the http query parameters in a dict
        params = {
            "APPID":api_key,
            "q":"Hyderabad,IN"   # <----- here it goes your city
        }
        
        # the following url gets weather information in json based on the name of the city
        url="http://api.openweathermap.org/data/2.5/weather"
        # url resolution and http protocol handling are hidden inside the requests module
        response = requests.get(url,params=params)
        # if we get here, there has been no exception, exit the loop
        break
    except Exception as e:
        print(e)

try:
    # check status and print the result
    if response.status==200:
        print("Got new weather value!!")
        print("-------------")
        # it's time to parse the json response
        js = json.loads(response.content)
        # super easy!
        print("Weather:",js["weather"][0]["description"])
        print("Temperature:",js["main"]["temp"]-273,"degrees")
        print("Pressure:",js["main"]["pressure"],"hPa")
        print("Humidity:",js["main"]["humidity"],"%")
        print("Wind speed:",js["wind"]["speed"],"meter/sec")
        print("Wind angle:",js["wind"]["deg"],"degrees")
        print("-------------")
except Exception as e:
    print("Oops dint retreive weather value. Try next time :(",e)

# Now let's create a socket and listen for incoming connections on port 80
sock = socket.socket()
sock.bind(80)
sock.listen()


while True:
    
    try:
        # Type in your browser the board ip!
        print("Waiting for connection...")
        # here we wait for a connection
        clientsock,addr = sock.accept()
        print("Incoming connection from",addr)

        # yes! a connection is ready to use
        # first let's create a SocketStream
        # it's like a serial stream, but with a socket underneath.
        # This way we can read and print to the socket
        client = streams.SocketStream(clientsock)
        
        # let's read all the HTTP headers from the browser
        # stop when a blank line is received
        line = client.readline()
        while line!="\n" and line!="\r\n":
            line = client.readline()
        print("HTTP request received!")
        
        f = open("resource://index.html",'r')
        
        html_response = "HTTP/1.1 200 OK \r\n"
        html_response += "Content-Type: text/html\r\n"
        html_response += "Content-Length: "+str(f.size)+"\r\n"
        html_response += "Connection: close \r\n\r\n"
        
        clientsock.send(html_response)
        
        line = f.readline()
        while line:
            line = line.replace('rNum',str(random(0,100)))
            line = line.replace('qqq',str(js["weather"][0]["description"]))
            line = line.replace('www',str(js["main"]["temp"]-273))
            line = line.replace('eee',str(js["main"]["pressure"]))
            line = line.replace('rrr',str(js["main"]["humidity"]))
            line = line.replace('ttt',str(js["wind"]["speed"]))
            
            clientsock.send(line)
            line  = f.readline()

        clientsock.close()
    except Exception as e:
        print("ooops, something wrong while serving the http request",e)
        
        
        
