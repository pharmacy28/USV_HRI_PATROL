import tobii_research as tr
import time
found_eyetrackers = tr.find_all_eyetrackers()

print("Found " + str(len(found_eyetrackers)) + " eye tracker(s):")
print(found_eyetrackers)
my_eyetracker = found_eyetrackers[0]
print("Address: " + my_eyetracker.address)
print("Model: " + my_eyetracker.model)
print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
print("Serial number: " + my_eyetracker.serial_number)