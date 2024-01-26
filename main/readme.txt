General robot SDK -> https://docs.ubtrobot.com/alphamini/python-sdk-en/mini.html
The final prototype file is unreliablesensorintegrated where there are comments explaining what does what
To connect the robot follow these steps
1. Connect the robot to wifi via Maatje platform (Note that to program the robot both the laptop and robot has to connect to same network (Using hotspot is an option))
2. Have an IDE with python installed
3. Install alphamini with pip install alphamini 
4. It is recommended to get the example project (https://github.com/marklogg/mini_demo.git) where it contains the function examples to test run

Notes: - Replace the robot right ID in test_connect
- If the robot doesnt connect, consider turning off the firewall
- The program should be able to be packaged and integrated into the robot based on the sdk but this was never tried out
