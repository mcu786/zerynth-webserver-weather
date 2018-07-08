###############################################################################
# Mini Web Server
#
# Created by Zerynth Team 2015 CC
# Authors: G. Baldi, D. Mazzei
###############################################################################
# webserver+weather multiple threads
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

#Start serial port
streams.serial()

#Adding html file as a new resource and use it
new_resource("index.html")

print("Device boot up Success")

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
    wifi.link("Wifi-AP",wifi.WIFI_WPA2,"password")
except Exception as e:
    print("ooops, something wrong while conecting to Wifi Access Point:(", e)
    while True:
        sleep(1000)

# Yes! we are connected
print("Connected to Wifi!")

# Let's print our ip, it will be needed soon
info = wifi.link_info()
print("My IP is:",info[0])

#Weather api key
api_key = "Get api key from openweather.org"

#Have global varable for storing weather information
global Winfo
Winfo = {"Weather":"NA","Temperature":"NA","Pressure":"NA","Humidity":"NA","Windspeed":"NA","Clouds": "NA","Rainfall":"NA"}

#Weather Thread function
def weatherThread(tdelay):
    print()
    print("+++++++++++++++++++++++start Weather thread+++++++++++++++++++++++")
    while True:
        for j in range(3):
            try:
                print("#############################################################")
                print("Retrieving Hyderabad,IN weather information-----> ")
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
                print("Oops couldn't connect o weather api. Try next time :(",e)
        try:
            # check status and print the result
            if response.status==200:
                print("Got new weather value!!")
                print("-------------")
                # it's time to parse the json response
                js = json.loads(response.content)
                # super easy!
                Winfo["Weather"] = js["weather"][0]["description"]
                Winfo["Temperature"] = js["main"]["temp"]-273
                Winfo["Pressure"] = js["main"]["pressure"]
                Winfo["Humidity"] = js["main"]["humidity"]
                Winfo["Windspeed"] = js["wind"]["speed"]
                Winfo["Clouds"] = js["clouds"]["all"]

                print("Weather: ",Winfo["Weather"])
                print("Temperature: ",Winfo["Temperature"],"degrees")
                print("Pressure: ",Winfo["Pressure"],"hPa")
                print("Humidity: ",Winfo["Humidity"],"%")
                print("Wind speed: ",Winfo["Windspeed"],"meter/sec")
                print("Clouds:",Winfo["Clouds"],"%")
                print("#############################################################")
        except Exception as e:
            print("Oops dint retreive weather value. Try next time :(",e)

        #thread delay
        sleep(tdelay)


#Start weather thread function for every 10 mins
thread(weatherThread,600000)

# Now let's create a socket and listen for incoming connections on port 80
sock = socket.socket()
sock.bind(80)
sock.listen()

#Webserver Thread function
def webserverThread():
    print("start Webserver thread")
    while True:
        try:
            # Type in your browser the board ip!
            print("+++++++++++++++++++++++Waiting for Http connection+++++++++++++++++++++++")
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
                line = line.replace('rNum',str(random(0,1000)))
                line = line.replace('qqq',str(Winfo["Weather"]))
                line = line.replace('www',str(Winfo["Temperature"]))
                line = line.replace('eee',str(Winfo["Pressure"]))
                line = line.replace('rrr',str(Winfo["Humidity"]))
                line = line.replace('ttt',str(Winfo["Windspeed"]))
                line = line.replace('yyy',str(Winfo["Clouds"]))

                clientsock.send(line)
                line  = f.readline()

            clientsock.close()
        except Exception as e:
            print("ooops, something wrong while serving the http request",e)

#Start weather thread function
thread(webserverThread)
        
