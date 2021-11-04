#!/bin/bash
# rsync -a --info=progress2 192.168.178.70:/mnt/ftp/camera ~/camera
rsync -a --info=progress2 ubuntu-server-new:/home/fberchtold/camera/camera/ ~/workspace/timelapse/camera
