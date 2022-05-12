import os, time, logging, json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

COOLDOWNTIMER = int(os.getenv('COOLDOWNTIMER'))
TEMPTHRESHOLD = int(os.getenv('TEMPTHRESHOLD'))
RELAY1 = int(os.getenv('RELAY1'))
RELAY2 = int(os.getenv('RELAY2'))
RELAY3 = int(os.getenv('RELAY3'))
BLINKER1 = int(os.getenv('BLINKER1'))
BLINKER2 = int(os.getenv('BLINKER2'))

try:
    import gpio as GPIO
except RuntimeError:
    print("Error importing GPIO!")

try:
    from pi1wire import Pi1Wire
except RuntimeError:
    print('Error importing pi1wire!')
    
#
import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True
})

# mapping GPIOs and resetting to 0 LOW
relays = {
    '1': RELAY1, 
    '2': RELAY2, 
    '3': RELAY3,
    '4': BLINKER1,
    '5': BLINKER2
    }

for i in relays:
    GPIO.setup(relays[i], GPIO.OUT)

#  finding all of the 1Wire temperature sensors

for s in Pi1Wire().find_all_sensors():
    print('%s = %.2f' % (s.mac_address, s.get_temperature()))

# measures temperature across all sensors and return average temperature
def measureTemp():
    avgtemp = []
    for s in Pi1Wire().find_all_sensors():
        # mac = s.mac_address
        temp = s.get_temperature()
        avgtemp.append(temp)
    return sum(avgtemp)/len(avgtemp)

def blinkerSwitch(pos):
    if pos:
        GPIO.output(relays['4'], GPIO.HIGH)
        GPIO.output(relays['5'], GPIO.LOW)
    else:
        GPIO.output(relays['4'], GPIO.LOW)
        GPIO.output(relays['5'], GPIO.HIGH)

if __name__ == "__main__":
    print('starting')
    currenttime = time.time()
    start = 0
    status = {
        'temp': 0,
        'work': 'idle',
        'msg': []
    }
    while True:
        msg = []
        temp = measureTemp()
        status['temp'] = temp
        # msg.append(temp)
        currenttime = int(time.time())
        if temp >= TEMPTHRESHOLD:
            GPIO.output(relays['1'], GPIO.HIGH)
            blinkerSwitch(True)
            status['work'] = 'triggered'
            # msg.append('trig')
            start = int(time.time())
            # msg.append('diff: '+str((currenttime-start)))
        else:
            if (currenttime - COOLDOWNTIMER) >= start:
                status['work'] = 'offline'
                # msg.append('off')
                GPIO.output(relays['1'], GPIO.LOW)
                blinkerSwitch(False)
                start = 0
        # msg.append('diff: '+str((currenttime-start)))
        status['msg'].append('ct: '+str(datetime.utcfromtimestamp(currenttime).strftime('%Y-%m-%d %H:%M:%S')))
        status['msg'].append('st: '+str(datetime.utcfromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S')))
        # print(status)
        f = open("/var/www/html/index.json", "w")
        f.write(json.dumps(status))
        f.close()
        status['msg'].clear()
        time.sleep(0.5)
else:
   print("Execute this file directly")