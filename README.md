# Pixelblaze-MQTT Bridge

Small service that connects a [pixelblaze](https://www.bhencke.com/pixelblaze) to MQTT.

Mainly written to work well with a [Home Assistant MQTT Light (json schema)](https://www.home-assistant.io/integrations/light.mqtt/#default-schema), but other MQTT-speaking things also work obviously.


## Settings
```yaml
---
mqtt_server: ...
mqtt_username: ...
mqtt_password: ...
# The bridge will subscribe to $mqtt_topic_prefix + '#' and publish to $mqtt_topic_prefix + 'available'
mqtt_topic_prefix: lights/pixelblaze/
# Websocket url of the pixelblaze instance. Yes, only a single instance is supported for now
pixelblaze_address: ws://...:81/
ext_color_prog: Solid
```

## ext_color_prog
Set to Solid. Changes light strip to a solid color using R,G,B to work with Home Assistant

## Home Assistant
Example configuration for a [Home Assistant MQTT Light](https://www.home-assistant.io/integrations/light.mqtt/)

```yaml
light:
  - platform: mqtt
    schema: json
    name: "TV Lights"
    state_topic: "lights/pixelblaze/state"
    command_topic: "lights/pixelblaze/set"
    availability_topic: "lights/pixelblaze/available"
    brightness: true
    effect: true
    rgb: true
    effect_list:
      - opposites
      - spin cycle
      - rainbow fonts
      - modes and waveforms
      - green ripple reflections
      - marching rainbow
      - color twinkles
      - firework dust
      - block reflections
      - color bands
      - color hues
      - glitch bands
      - sparks
      - rainbow melt
      - NaturalLightSync
      - notify
      - Sunset
      - Solid
```

## MQTT


### MQTT status
```lights/pixelblaze/state``` returns a json object containing:
```

state: ON or OFF
brightness: 0-255
effect_list: [an array of the effects availabe in Pixelblaze] -- Unfortunately I have not found a way to have HA update the effect_list given this list
effect: Name of current pattern
```

### MQTT set (json)
```lights/pixelblaze/set``` json formatted
example:
```
{
  "state": "ON",
  "effect": "Solid",
  "color": {
    "r": 255,
    "g": 255,
    "b": 255
  },
  "brightness": 255
}
```

### MQTT brightness
```lights/pixelblaze/brightness 0-255```

### MQTT effect
```lights/pixelblaze/effect NameOfPattern```

### MQTT toggle
```lights/pixelblaze/toggle``` Toggles lights on/off

### MQTT switch
```lights/pixelblaze/switch ON or OFF``` switches to ON or OFF

### MQTT vars
```lights\pixelblaze\vars {"ext_h":20}``` set the variables for a pattern, in json format

### MQTT notify
These are mostly for me. I use nodered to send these glimmers when I get specific notifications on my phone (Someone specific messages me)
They are still a work in progress

```lights\pixelblaze\notify h,s,v``` a little 2sec glimmer for an alert using HSV values
```lights\pixelblaze\notify2 h,s,v,h,s,v``` 2sec glimmer with 2 colors using HSV values
```lights\pixelblaze\notify3 h,s,v``` 2 flashes with HSV color


## Pixelblaze Pattern Codes
[This folder](pixelblaze_patterns/) has some of the patterns I use in this script (Solid, NaturalLightSync, notify, Sunset)