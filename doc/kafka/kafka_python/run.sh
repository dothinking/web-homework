PY_IMAGE_NAME="python-kafka:3.6"
PY_CONTAINER_NAME="python-kafka"
APP_NET="app_net"

# network
echo "creating network: ${APP_NET}..."
if [ -n "$(docker network ls -f name=${APP_NET} -q)" ]; then
    docker network rm  ${APP_NET}
else
    docker network create ${APP_NET}
fi

# kafka
echo "starting kafka..."
docker-compose up -d

# kafka-python
if [ ! -n "$(docker image ls ${PY_IMAGE_NAME} -q)" ]; then 
    echo "building python image..."
    docker build -t ${PY_IMAGE_NAME} .
fi
echo "starting python container..."
docker run  -itd \
            --name ${PY_CONTAINER_NAME} \
            -v $(pwd):/app \
            python-kafka:3.6

# share network
echo "connecting kafka and python network..."
docker network connect ${APP_NET} ${PY_CONTAINER_NAME}

echo "entering python container..."
docker exec -it ${PY_CONTAINER_NAME} /bin/sh

echo "shutting down..."
docker-compose down
docker rm -f ${PY_CONTAINER_NAME}
docker network rm ${APP_NET}
echo "goodbye!"