#!/bin/bash

# This utility is to start and stop and check the status of the running containers
# You can start as many containers you want to start or stop
# NUMBER_OF_CONTAINERS >> number of containers you wish to start
# CONTAINERS_RUNNING >> already running containers
# START_CONTAINERS_COUNT >> name counter for container name like ei-local-manager-1, ei-local-manager-2 .... etc
# EXT_PORT >> port number mapped with host from container port
# INT_PORT >> port number of container
# STOP_CONTAINER_NUMBER >> number of containers you wish to stop

SERVICE_NAME="EI Utility Containers"
BUILD_ARGS="-e CAF_SYSTEM_SERIAL_ID=FCW2610Y10Y  -e CAF_SYSTEM_PRODUCT_ID=IR1101-K9  -e CAF_APP_PERSISTENT_DISK_SIZE_KB=256000  -e CAF_APP_LOG_DIR=/data/logs"
IMAGE_NAME="dockerhub-master.cisco.com/iot-darkphoenix-docker/ei-edge-testing:1.16.20"
CONTAINER_NAME="ei-local-manager"
EXT_PORT=9000
INT_PORT=8008
COMMAND=$1
NUMBER_OF_CONTAINERS=$2

HOST_IP=10.105.58.119
PIPELINE_NAME=pipeline
PIPELINE_NUMBER=1
DATA_SOURCE_FILE=data_source_1.json
DATA_LOGIC_FILE=data_logic_1.json
DATA_TARGET_FILE=data_target_1.json
DATA_VARIABLES_FILE=data_vars_1.json

OUTPUT_FILE="inventory.yml"

CONTAINERS_RUNNING=`docker ps|grep -v NAME | awk '{print $NF}' | wc -l`
NAME_OF_CONTAINERS_RUNNING=`docker ps|grep -v NAME | awk '{print $NF}' | awk -F '-' '{print $4}' | head -n1`

if [ $CONTAINERS_RUNNING -eq $NAME_OF_CONTAINERS_RUNNING  ]; then
     sleep 0
else
     CONTAINERS_RUNNING=$NAME_OF_CONTAINERS_RUNNING
fi

start_service() {

     if [ -z $COMMAND ] || [ -z $NUMBER_OF_CONTAINERS ]; then
       echo "========= Incomplete Arguments, Both arguments must be provided  ========="
       echo "Exp:- sh ei-container.sh start 10|20"
       exit 0
    fi

    #Check if any containers are running
    echo "Numbers of $SERVICE_NAME already running : " $CONTAINERS_RUNNING

    if [ $CONTAINERS_RUNNING -gt 0 ]; then
	     START_CONTAINERS_COUNT=$((CONTAINERS_RUNNING + 1))
	     echo " $CONTAINERS_RUNNING $SERVICE_NAME are already running.... , Creating new containers from $NEW_CONTAINERS"
    else
	     echo "No $SERVICE_NAME found, starting $NUMBER_OF_CONTAINERS containers "
	     START_CONTAINERS_COUNT=1
    fi

    echo "Starting $NUMBER_OF_CONTAINERS $SERVICE_NAME..."

    NOC=$NUMBER_OF_CONTAINERS
    CONTAINER_NUMBER=$START_CONTAINERS_COUNT
    EXT_PORT=$((EXT_PORT + $START_CONTAINERS_COUNT))

    for ((i=1; i<=NOC; i++))
    do
       echo "start container $CONTAINER_NAME-$CONTAINER_NUMBER"
       docker run -dit $BUILD_ARGS -p $EXT_PORT:$INT_PORT --name $CONTAINER_NAME-$CONTAINER_NUMBER $IMAGE_NAME
       cat <<EOL >> $OUTPUT_FILE
- DEVICE_IP: ${HOST_IP}:${EXT_PORT}
  PIPELINE_NAME: $PIPELINE_NAME$PIPELINE_NUMBER
  DATA_SOURCE_FILE: ${DATA_SOURCE_FILE}
  DATA_LOGIC_FILE: ${DATA_LOGIC_FILE}
  DATA_TARGET_FILE: ${DATA_TARGET_FILE}
  DATA_VARIABLES_FILE: ${DATA_VARIABLES_FILE}
EOL
       EXT_PORT=$((EXT_PORT + 1))
       PIPELINE_NUMBER=$((PIPELINE_NUMBER + 1))
       CONTAINER_NUMBER=$((CONTAINER_NUMBER + 1 ))
     done
}

stop_service() {

    if [ -z $COMMAND ] || [ -z $NUMBER_OF_CONTAINERS ]; then
       echo "========= Incomplete Arguments, Both arguments must be provided  ========="
       echo "Exp:- sh ei-container.sh stop 10|20|all"
       exit 0
    fi

    if [ $NUMBER_OF_CONTAINERS == "all" ]; then
	      NUMBER_OF_CONTAINERS=$CONTAINERS_RUNNING
	      rm -rf inventory.yml
	      if  [ $NUMBER_OF_CONTAINERS -eq 0 ]; then
                  echo "No $SERVICE_NAME are running"
	      fi
    fi

    COUNTNER=1
    if [ $NUMBER_OF_CONTAINERS -le $CONTAINERS_RUNNING ]; then
	        echo "Stopping $NUMBER_OF_CONTAINERS $SERVICE_NAME..."
	        STOP_CONTAINER_NUMBER=$CONTAINERS_RUNNING
	        while [ $COUNTNER -le $NUMBER_OF_CONTAINERS ]; do
	             echo "stoping and removing $CONTAINER_NAME-$STOP_CONTAINER_NUMBER container....."
		     docker stop -t 0 $CONTAINER_NAME-$STOP_CONTAINER_NUMBER
	             docker rm $CONTAINER_NAME-$STOP_CONTAINER_NUMBER | 2> /dev/null
		     sed -i "/${HOST_IP}:$((EXT_PORT + STOP_CONTAINER_NUMBER))/,+5d" inventory.yml
	             COUNTNER=$((COUNTNER + 1 ))
		     STOP_CONTAINER_NUMBER=$((STOP_CONTAINER_NUMBER - 1))
		     if [ $CONTAINERS_RUNNING -eq 0 ]; then
			 exit 0
		     fi
	        done
    elif [ $CONTAINERS_RUNNING -eq 0 ]; then
          echo "=============== No $SERVICE_NAME are running ==============="
    else
          echo "=============== Only $CONTAINERS_RUNNING $SERVICE_NAME are running, pls provide value $CONTAINERS_RUNNING or less ==============="
    fi
}

status_service() {
    echo "Checking status of $SERVICE_NAME... "
    echo "$CONTAINERS_RUNNING $SERVICE_NAME are running...."
}

case "$COMMAND" in
    start)
	start_service
        ;;
    stop)
        stop_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac

exit 0
