import json
import sys

import logging
import paho.mqtt.client as mqtt
import time
import websocket
import yaml
import colorsys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

with open("settings.yml", 'r') as stream:
    settings = yaml.safe_load(stream)

programs = {}
programNames = []


def parse_programs_frame(b):
    global programs
    global programNames
    s = b.decode("utf8")
    for l in s.split('\n'):
        p = l.split('\t')
        if len(p[0]) > 0:
            programs[p[0]] = p[1]
            programs[p[1]] = p[0]
            programNames.append(p[1])


def save_programs():
    global programs
    with open("programs.yml", "w+") as p:
        yaml.dump({v: k for k, v in programs.items()}, p)


def on_message(ws, message):
    global programs
    global current_program
    global current_brightness
    global prev_brightness
    global current_vars
    global current_mqtt

    if message[0] is 0x07:
        if message[1] & 0x01 == 0x01:
            programs.clear()
        parse_programs_frame(message[2:])
        if message[1] & 0x04 == 0x04:
            save_programs()
    else:
        try:
            message_json = json.loads(message)
            if 'activeProgram' in message_json:
                current_program = message_json['activeProgram']['activeProgramId']
                current_vars = message_json['activeProgram']['controls']
            elif 'brightness' in message_json:
                current_brightness = message_json['brightness']
                if not prev_brightness:
                    prev_brightness = message_json['brightness']



        except:
            logging.info('Got WS message "%s"', message)




def on_error(ws, error):
    logging.error(error)


def on_close(ws):
    global current_ws
    current_ws = None


def ws_send(p):
    if current_ws is not None:
        logging.debug("Sending %s", json.dumps(p))
        current_ws.send(json.dumps(p))


def on_open(ws):
    global current_ws

    logging.info("Websocket open")
    current_ws = ws


    ws_send({
        "listPrograms": True
    })

    get_config()
    mqtt_publish_settings()

def get_config():
    ws_send({
        "getConfig": True
        })

    set_available()
    mqtt_publish_settings()


def set_brightness(b):
    ws_send({
        "brightness": b,
        "save": False
    })

    get_config()


def set_switch(switch):
    global prev_brightness
    global current_brightness

    if switch.lower() == 'on':
        if prev_brightness > 0:
            set_brightness(prev_brightness)
        else:
            set_brightness(1)
    elif switch.lower() =='off':
        get_config()

        prev_brightness = current_brightness
        set_brightness(0)

def set_toggle():
    global current_brightness
    global prev_brightness

    get_config()

    if current_brightness > 0:
        prev_brightness = current_brightness
        set_brightness(0)
    elif prev_brightness > 0:
        set_brightness(prev_brightness)
    else:
        set_brightness(1)



def set_active_program(id):

    ws_send({
        "activeProgramId": id,
        "save": False
    })

    get_config()

def set_vars(vars):

    ws_send({
        "setVars": vars
        })

    get_config()

def set_any(progID=None, brightness=None, progVars=None):
    toSend = {}
    if progID:
        toSend['activeProgramId'] = progID
    if brightness is not None:
        toSend['brightness'] = brightness
    if progVars:
        toSend['setVars'] = progVars

    if toSend:
        ws_send(toSend)
        get_config()


def set_solid(hsv):
    try:
        h, s, v = hsv
        h = h if h < 1 else h/255.0
        s = s if s < 1 else s/255.0
        v = v if v < 1 else v/255.0
        set_any(
            programs[settings["ext_color_prog"]],
            progVars={
                "ext_h": h,
                "ext_s": s,
                "ext_v": v
            })
        get_config()
    except ValueError:
        logging.error("Could not parse payload")


def set_notify(hsv):
    global prev_brightness
    global prev_program
    global prev_vars
    global prev_time


    if time.time() - prev_time > 3:
        get_config()
    
        if 'notify' not in current_program:
            prev_program = current_program
            prev_brightness = current_brightness
            prev_vars = current_vars

        try:
            h, s , v = map(lambda x: float(x.strip()), hsv.split(','))
            set_any(
                programs["notify"], 
                1.0,
                {
                "ext_h": h / 255.0,
                "ext_s": s / 255.0,
                "ext_v": v / 255.0
                })

            time.sleep(2)

            set_any(prev_program, prev_brightness, prev_vars)
            prev_time = time.time()

        except ValueError as e:
            logging.error("Could not parse payload: " + e)

def set_notify2(hsv):
    global prev_brightness
    global prev_program
    global prev_vars
    global prev_time

    if time.time() - prev_time > 3:
        get_config()
        
        if 'notify' not in current_program:
            prev_program = current_program
            prev_brightness = current_brightness
            prev_vars = current_vars

        try:
            h1, s1 , v1, h2, s2, v2 = map(lambda x: float(x.strip()), hsv.split(','))
            delay = 1
            set_any(
                programs["notify"], 
                1.0,
                {
                "ext_h": h1 / 255.0,
                "ext_s": s1 / 255.0,
                "ext_v": v1 / 255.0
                })

            time.sleep(delay)

            set_any(
                programs["notify"], 
                1.0,
                {
                "ext_h": h2 / 255.0,
                "ext_s": s2 / 255.0,
                "ext_v": v2 / 255.0
                })

            time.sleep(delay)

            set_any(prev_program, prev_brightness, prev_vars)
            prev_time = time.time()

        except ValueError as e:
            logging.error("Could not parse payload: " + e)

def set_notify3(hsv):
    global prev_brightness
    global prev_program
    global prev_vars
    global prev_time

    if time.time() - prev_time > 3:
        get_config()

        if 'notify' not in current_program:
            prev_program = current_program
            prev_brightness = current_brightness
            prev_vars = current_vars

        try:
            h, s , v = map(lambda x: float(x.strip()), hsv.split(','))
            set_solid([h,s,v])
            delay = 0.5
            set_brightness(1)
            time.sleep(delay)
            set_brightness(0)
            time.sleep(delay)
            set_brightness(1)
            time.sleep(delay)

            set_any(prev_program, prev_brightness, prev_vars)
            prev_time = time.time()

        except ValueError as e:
            logging.error("Could not parse payload: " + e)


def mqtt_publish_settings():


    if current_program is not None and current_mqtt is not None:
        pub_settings = {
            'brightness': int(current_brightness * 255),
            'effect': programs[current_program],
            'state': 'ON' if current_brightness > 0 else 'OFF',
            'effect_list': programNames,
        }

        if programs[current_program] == settings['ext_color_prog'] and current_vars is not None:
            h, s, v = current_vars['hsvPickerColor']
            r, g, b = colorsys.hsv_to_rgb(h, s, v)


            pub_settings['color'] = {
                'r': int(r * 255),
                'g': int(g * 255),
                'b': int(b * 255),
                'h': h * 360.0,
                's': s * 100.0
            }


        current_mqtt.publish(settings['mqtt_topic_prefix'] + 'state', payload=json.dumps(pub_settings))

def mqtt_set_settings(payload):
    try:
        if 'color' in payload:
            r = payload['color']['r']
            g = payload['color']['g']
            b = payload['color']['b']
            print(r,g,b)
            h,s,v = colorsys.rgb_to_hsv(r,g,b)

            print(h,s,v)

            set_solid([h,s,v])
        # else:
        #     set_any(programs[payload['effect']], payload['brightness'])
        if 'state' in payload:
            set_switch(payload['state'])

        if 'brightness' in payload:
            set_brightness(payload['brightness']/255.0)

        if 'effect' in payload:
            set_active_program(programs[payload['effect']])
            
    except Exception as e:
        logging.error("Could not change" + e)


# The callback for when the client receives a CONNACK response from the server.
def on_mqtt_connect(client, userdata, flags, rc):
    global current_mqtt
    logging.info('Connected to MQTT: %s', str(rc))
    current_mqtt = client
    client.subscribe(settings['mqtt_topic_prefix'] + '#')
    set_available()



def on_mqtt_disconnect(client, userdata, rc):
    global current_mqtt
    current_mqtt = None
    logging.info('Disconnected from MQTT: %s', str(rc))


def on_mqtt_message(client, userdata, msg):
    global programs
    if msg.topic.startswith(settings['mqtt_topic_prefix']):
        logging.info('Received message "%s" for topic "%s" from MQTT', msg.payload, msg.topic)

        prop = msg.topic[len(settings['mqtt_topic_prefix']):]
        if prop == 'brightness':
            b = float(msg.payload) / 255.0
            set_brightness(b)
        elif prop == 'toggle':
            set_toggle()
        elif prop == 'switch':
            set_switch(msg.payload.decode("utf8"))
        elif prop == 'effect':
            set_active_program(programs[msg.payload.decode("utf-8")])
        elif prop == 'notify':
            set_notify(msg.payload.decode("utf-8"))
        elif prop == 'notify2':
            set_notify2(msg.payload.decode("utf-8"))
        elif prop == 'notify3':
            set_notify3(msg.payload.decode("utf-8"))
        elif prop == 'solid':
            h, s, v = map(lambda x: float(x.strip()), msg.payload.decode("utf-8").split(','))
            set_solid([h,s,v])
        elif prop == 'vars':
            set_vars(json.loads(msg.payload.decode("utf-8")))
        elif prop == 'set':
            mqtt_set_settings(json.loads(msg.payload.decode("utf-8")))
        elif prop == 'available':
            pass
        elif prop == 'state':
            pass
        else:
            logging.warning('Got unhandled property message: "%s"', prop)
    else:
        logging.warning('Got unhandled topic message: "%s"', msg.topic)


def set_available():
    if current_mqtt is not None:
        current_mqtt.publish(
            settings['mqtt_topic_prefix'] + 'available',
            payload="online",
            qos=1,
            retain=True
        )


current_ws = None
current_mqtt = None

current_program = None
current_brightness = None
current_vars = None

prev_brightness = None
prev_program = None
prev_vars = None
prev_time = time.time()


if __name__ == "__main__":
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.on_disconnect = on_mqtt_disconnect

    mqtt_client.username_pw_set(settings['mqtt_username'], settings['mqtt_password'])
    mqtt_client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pem')

    mqtt_client.will_set(settings['mqtt_topic_prefix'] + 'available', 'offline', 1, retain=True)

    mqtt_client.connect(settings['mqtt_server'], settings.get('mqtt_port', 8883), 60)

    mqtt_client.loop_start()

    while True:
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            settings['pixelblaze_address'],
            on_open=on_open,
            on_close=on_close,
            on_message=on_message,
            on_error=on_error
        )

        ws.run_forever(
            ping_interval=3,
            ping_timeout=2,
        )

        time.sleep(5)
