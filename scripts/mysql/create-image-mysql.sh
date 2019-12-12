#!/usr/bin/env bash

APP_FILENAME="conf"
MYSQL_DATA_FILENAME="mysqldata"
IMAGE_NAME="mysql:5.6"
CONTAINER_NAME="mysql-3000"

if [ ! -d $MYSQL_DARA_FILENAME]; then
    mkdir "$MYSQL_DATA_FILENAME"
fi

echo "【1】 下载 mysql:5.6 版本"
docker pull mysql:5.6

echo "【2】先用原本镜像生成容器，初始化不需要密码（后续添加），并进行持久化配置"
echo "$PWD/$MYSQL_DATA_FILENAME"

docker run --name $CONTAINER_NAME -d \
 -v "$PWD/$MYSQL_DATA_FILENAME":/var/lib/mysql \
 -p 3000:3306 \
 -e MYSQL_ROOT_PASSWORD=12345678 mysql:5.6 \
 --character-set-server=utf8mb4 \
 --collation-server=utf8mb4_unicode_ci

echo "【3】然后把 app 文件拷贝到容器里面"
docker cp $PWD/$APP_FILENAME $CONTAINER_NAME:/

echo "【4】执行容器内的初始化脚本"
docker exec $CONTAINER_NAME sh /$APP_FILENAME/init.sh
