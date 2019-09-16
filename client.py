# USAGE
# python client.py --server-ip SERVER_IP

# import the necessary packages
import imutils
from imutils.video import VideoStream
from imagezmq import imagezmq
import argparse
import socket
import time
import cv2
from matplotlib import pyplot as plt
import subprocess
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
	help="ip address of the server to which the client will connect")
ap.add_argument("-d", "--debug", action='store_true',
	help="debug mode")
args = vars(ap.parse_args())


def find(max_id):
    """Find camera id."""
    plt.ion()
    plt.show()

    cap = cv2.VideoCapture()

    device = max_id
    print('Finding camera device...')
    while device >= 0:
        cap.open(device)
        if cap.isOpened():
            print('Found a camera device, id: {}'.format(device))
            # show preview
            _, frame = cap.read()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            plt.imshow(rgb_frame, aspect='equal', extent=None)
            plt.draw()
            plt.axis('off')
            plt.pause(0.001)

            cap.release()
            break
        device -= 1
    else:
        print('Cannot start video capture. Please connect camera and run again')

    plt.close('all')
    cap.release()
    cv2.destroyAllWindows()

    return device

	
# initialize the ImageSender object with the socket address of the
# server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
	args["server_ip"]))
# sender = imagezmq.ImageSender(connect_to="http://{}".format(
# 	args["server_ip"]))
# sender = imagezmq.ImageSender(connect_to="tcp://127.0.0.1:5555")


# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()
#vs = VideoStream(usePiCamera=True).start()
camera_id = find(10)
# camera_id = 0
vs = VideoStream(src=camera_id, resolution=(1028, 720)).start()
time.sleep(1.0)

command = "v4l2-ctl -d {} --set-ctrl=brightness=193 \
                          --set-ctrl=contrast=172 \
                          --set-ctrl=saturation=143 \
                          --set-ctrl=gain=130 \
                          --set-ctrl=sharpness=255 \
                          --set-ctrl=exposure_auto=1 \
                          --set-ctrl=exposure_auto_priority=1 \
                          --set-ctrl=exposure_absolute=156 \
                          --set-ctrl=focus_auto=0 \
                          --set-ctrl=zoom_absolute=150 \
                          --set-fmt-video=width=1028 \
                          --set-fmt-video=height=720".format(camera_id)
output = subprocess.call(command, shell=True)
 
while True:
	# read the frame from the camera and send it to the server
	try:
		start_time = time.time()
		frame = vs.read()
		if hasattr(frame, 'flags'):
			# frame = imutils.resize(frame, width=1028, height=720)
			sender.send_image(rpiName, frame)
            	
		if args["debug"]:
			print('fps', 1/(time.time() - start_time))
            
			cv2.imshow('Frame', frame)
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break
	except Exception as e:
		print('error: {}'.format(e)) 



