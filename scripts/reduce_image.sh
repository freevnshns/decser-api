#!/bin/bash
IMG_PATH=${IHS_DATA_DIR}
convert ${IMG_PATH}/profilePicture.jpg -resize 'x300' ${IMG_PATH}/profilePicture_L.jpg
convert ${IMG_PATH}/profilePicture_L.jpg -resize 50% ${IMG_PATH}/profilePicture_S.jpg
convert ${IMG_PATH}/profilePicture_L.jpg -resize 75% ${IMG_PATH}/profilePicture_M.jpg
convert ${IMG_PATH}/profilePicture_L.jpg -filter Gaussian -resize 25% -define filter:sigma=15 -resize 400% ${IMG_PATH}/profilePicture_header.jpg
