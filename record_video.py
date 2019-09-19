#!/usr/bin/env python3

import datetime

import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import subprocess

# FRAME_WIDTH = 1280
# FRAME_HEIGHT = 720

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

MOVEMENT_THRESHOLD = 5


def record_video(camera_id):
    # cv2.namedWindow('frame')
    # cv2.namedWindow('dist')

    cap = cv2.VideoCapture(camera_id)
#    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
#    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    command = "v4l2-ctl -d {} --set-ctrl=brightness=180 \
                           --set-ctrl=contrast=150 \
                           --set-ctrl=saturation=140 \
                           --set-ctrl=gain=130 \
                           --set-ctrl=sharpness=180 \
                           --set-ctrl=exposure_auto=1 \
                           --set-ctrl=exposure_auto_priority=1 \
                           --set-ctrl=exposure_absolute=77 \
                           --set-ctrl=focus_auto=0 \
                           --set-ctrl=zoom_absolute=150".format(camera_id)
    output = subprocess.call(command, shell=True)
    print('output', output)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    curr_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    
    FRAME_WIDTH = cap.get(3)
    FRAME_HEIGHT = cap.get(4)
    output = f'{curr_datetime}_cut.avi'
    out = cv2.VideoWriter(output, fourcc, 30, (FRAME_WIDTH, FRAME_HEIGHT))
    print(f'Record video is saving in file {output}')
    print(f'Start record video...')

    _, frame1 = cap.read()
    _, frame2 = cap.read()

    while (cap.isOpened()):
        start_time = time.time()
        ret, frame3 = cap.read()
        if ret is True:
            # stDev, mod = motion_detector(frame1, frame3)

            # frame1 = frame2
            frame2 = frame3

            # if stDev > MOVEMENT_THRESHOLD:
            #   cv2.imshow('frame', frame2)
            #   out.write(frame2)
            # cv2.imshow('frame', frame2)
            out.write(frame2)
            # cv2.imshow('dist', mod)

            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        else:
            break
        print('fps', 1/(time.time() - start_time))

    print("Finish record video")
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def motion_detector(frame1, frame3):
    def distMap(frame1, frame2):
        frame1_32 = np.float32(frame1)
        frame2_32 = np.float32(frame2)
        diff32 = frame1_32 - frame2_32
        norm32 = np.sqrt(diff32[:, :, 0]**2 + diff32[:, :, 1]**2 + diff32[:, :, 2]**2) / np.sqrt(255**2 + 255**2 +
                                                                                                 255**2)
        dist = np.uint8(norm32 * 255)
        return dist

    dist = distMap(frame1, frame3)
    mod = cv2.GaussianBlur(dist, (9, 9), 0)
    _, thresh = cv2.threshold(mod, 100, 255, 0)
    _, stDev = cv2.meanStdDev(mod)
    return stDev, mod


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


if __name__ == '__main__':
    camera_id = find(5)
    record_video(camera_id)
