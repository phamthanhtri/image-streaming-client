#! /bin/sh

cd /home/pi/AILab/image-streaming-client
sudo /home/pi/.virtualenvs/dl-py3/bin/python -u record_video.py &>> /home/pi/AILab/image-streaming-client/log.txt &
