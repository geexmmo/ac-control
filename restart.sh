#!/bin/bash
# running
cd /root/ac-control
source bin/activate
RUNNERPID=$(ps -eo pid,comm,args|awk '{print $1,$3,$4}'|grep -E '\n*\spython3 runner.py'|awk 'NR==1{print $1}')
echo 'runner.py' $RUNNERPID
RESTARTERPID=$(ps -eo pid,comm,args|awk '{print $1,$3,$4}'|grep -E '\n*\sbash restart.sh'|awk 'NR==1{print $1}')
echo 'restarter.sh' $RESTARTERPID
if [ -z "$RUNNERPID" ]
then
    python3 runner.py &
else
    echo "killing old runner.py" $RUNNERPID
    kill $RUNNERPID
    sleep 1
    python3 runner.py &
    sleep 1
    RUNNERPID=$(ps -eo pid,comm,args|awk '{print $1,$3,$4}'|grep -E '\n*\spython3 runner.py'|awk 'NR==1{print $1}')
    echo "new runner.py pid" $RUNNERPID
fi
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/$0
echo 'Restarter'
# gpio restart
BLNK1="/sys/class/gpio/gpio452/value"
BLKN2="/sys/class/gpio/gpio453/value"
while true
do
  GPIOBUTTON=$(cat /sys/class/gpio/gpio436/value)
  if [ $GPIOBUTTON -ge "1" ]; 
  then
    echo 'button pressed'
    for i in {1..15}
    do
        echo '1' > $BLNK1
        sleep 0.1
        echo '0' > $BLNK1
        sleep 0.1
    done
    echo '0' > $BLNK1
    echo '0' > $BLKN2
    logger 'GPIO BUTTON RELOAD'
    echo 'killing runner.py' $RUNNERPID
    kill $RUNNERPID
    sleep 1
    python3 runner.py &
    RUNNERPID=$(ps -eo pid,comm,args|awk '{print $1,$3,$4}'|grep -E '\n*\spython3 runner.py'|awk 'NR==1{print $1}')
    echo "new runner.py pid" $RUNNERPID
    # echo 'killing restarter.sh'
    # bash ./$(basename $0)
    # kill $RESTARTERPID &&
    # echo 'dies...'
    # exec $SCRIPTPATH
  fi
    sleep 0.5
done