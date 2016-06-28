#!/bin/bash
IMGPATH=/home/comslav/user_assets
convert ${IMGPATH}/profilePicture.jpg -resize 'x300' ${IMGPATH}/profilePicture_L.jpg
convert ${IMGPATH}/profilePicture_L.jpg -resize 50% ${IMGPATH}/profilePicture_S.jpg
convert ${IMGPATH}/profilePicture_L.jpg -resize 75% ${IMGPATH}/profilePicture_M.jpg
convert ${IMGPATH}/profilePicture_L.jpg -filter Gaussian -resize 25% -define filter:sigma=15 -resize 400% ${IMGPATH}/profilePicture_header.jpg
