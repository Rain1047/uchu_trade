#!/bin/bash

docker run \
    -it \
    -e TZ=Asia/Shanghai \
    -v /Users/rain/Documents/trade_db.db:/path/in/container/trade_db.db \
    -v /本地路径:/容器路径 \
    -p 8080:8000 \
    your_image_name \
    /bin/bash
