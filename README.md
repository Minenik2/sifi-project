# Interactive Music Generator using Sifi Labs armband

This project is made using SifiLabs dependencies found here:
https://github.com/SiFiLabs/sifi-bridge-pub
https://github.com/SiFiLabs/sifi-bridge-py

Installation:

download the latest release in sifi-bridge-pub
windows recommended: sifibridge-1.1.3-x86_64-pc-windows-msvc.zip

make sure you have python version 3.12

make sure you have the application version 1.1.3 because 1.2.0 is not currently supported
make sure the sifi-bridge-py is 1.1.3, if you have python version 3.12 it will support 1.1.3

use the command:
PIP install sifi-bridge-py

copy the executable from pub examples into the sifi folder

## setting up a server

in the project folder write in terminal "python BridgeScriptExamples\ExamplesBiopoint\python_server.py"
this will start a websocket server using the python dependencies, this is also used by the javascript website,

Then in another terminal start the bioarm client by writing: "python bridgescriptexamples\Examplesbiopoint\javavscript.py"  
this will launch a connection with the bioarm via bluetooth, it will automatically start gathering data and sending it into the python socketserver

lastly you'll now need to open the website index.html, in vsCode you can open it with live server, this will show a visualized display of the data true javascript library called p5.js

Thats it for now! <3



