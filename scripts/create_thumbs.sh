#!/bin/bash
IMG_PATH=${IHS_DATA_DIR}
FILENAME=$1
convert ${IMG_PATH}/${FILENAME} -resize 75x75\> ${IMG_PATH}/${FILENAME}_thumbs.png