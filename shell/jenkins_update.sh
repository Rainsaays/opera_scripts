#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

DOCKER_USER=user
DOCKER_PASSWD=passwd
DOCKER_HOST=host

APP_NAME=$1
NOWVER=$2
APP_MODULE=ppxws
BUILD_PATH=/data/dockerfile/test
DOCKER_REGISTRY=$DOCKER_HOST/$APP_MODULE
_docker () {
    echo ">> docker $@"
    docker $@  >/dev/null
        }	
	
	
docker_login(){
	docker login -u  $DOCKER_USER -p $DOCKER_PASSWD https://$DOCKER_HOST 
}
docker_get_img(){
	curl -u"$DOCKER_USER:$DOCKER_PASSWD" -s -X GET  'https://'$DOCKER_HOST'/api/repositories/'$APP_MODULE'%2F'$1'/tags'
}

docker_rm_img(){
	curl -u"$DOCKER_USER:$DOCKER_PASSWD" -s -X DELETE  -u $DOCKER_USER:$DOCKER_PASSWD  'https://'$DOCKER_HOST'/api/repositories/'$APP_MODULE'%2F'$1'/tags/'$2''
	
}

docker_build(){
	docker_login
	cd $BUILD_PATH/$APP_NAME

	IMG_CHKSTATS=0
	for IMGSVNVER in $(docker_get_img $APP_NAME |grep "name"|awk -F '[_"]' '$0=$(NF-1)');do
              [ $IMGSVNVER = $NOWVER ] && IMG_CHKSTATS=1 && break
	done
	if [ $IMG_CHKSTATS -eq 0 ];then
		APP_VER_CONU=$(docker_get_img $APP_NAME |grep "name"|wc -l)
		if [ $APP_VER_CONU -gt 6 ];then
			RM_VER=$(docker_get_img $APP_NAME|grep "name"|awk -F '"' '{print $4}'|sort|head -n 1)
			docker_rm_img $APP_NAME $RM_VER && echo "$APP_NAME:$RM_VER docker rmi sucessful" 
		fi
		echo "$APP_NAME docker镜像构建"
		_docker build -t $DOCKER_REGISTRY/$APP_NAME:$NOWVER .  && echo "$APP_NAME docker build sucessful"||echo "$APP_NAME docker build failed"
		_docker push $DOCKER_REGISTRY/$APP_NAME:$NOWVER   && echo "$APP_NAME:$NOWVER docker push sucessful"||echo "$APP_NAME:$NOWVER docker build failed"

		_docker rmi $DOCKER_REGISTRY/$APP_NAME:$NOWVER && echo "docker rmi local $APP_NAME:$NOWVER  sucessful"||echo "docker rmi local $APP_NAME:$NOWVER  failed" 

	else

		echo "镜像存在，忽略构建动作！"
	fi	
	
}
docker_update(){
    if [ $IMG_CHKSTATS -eq 0 ];then
       sleep 3
       ansible host_name -m shell -a "docker login -u  $DOCKER_USER -p $DOCKER_PASSWD https://$DOCKER_HOST"
       ansible host_name -m shell -a "sed -i s@image:\ $DOCKER_HOST/$APP_MODULE/$APP_NAME.*@image:\ $DOCKER_HOST/$APP_MODULE/$APP_NAME:$NOWVER@g $APP_NAME.yml && kubectl apply -f $APP_NAME.yml chdir=/data/deploy/test/"
    fi    
}

if [ $# -eq 2 ];then
   docker_build
   docker_update
else 
  echo "请输入2个正常参数"
fi
