# About

Simple service that forwards APRS messages from a source UDP connection on localhost to a
specified HTTP webserver.

# System Dependencies

this application spawns the following subprocess:

```
nc -l -u -p <udp_port> \
| sox -t raw -esigned-integer -b 16 -r 48000 - -esigned-integer -b 16 -r 22050 -t raw - \
| multimon-ng --timestamp -t raw -a AFSK1200 -A -
```

and thus requires `netcat`, `sox`, and `multimon-ng` to be installed on the base system

# Python Dependencies
