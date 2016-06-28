#!/bin/bash
IMGPATH=/home/comslav/user_file_uploads
FILENAME=$1
convert ${IMGPATH}/${FILENAME} -resize 75x75\> ${IMGPATH}/${FILENAME}_thumbs.png