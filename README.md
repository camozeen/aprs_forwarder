# About

A simple service that forwards APRS messages from a source UDP connection on localhost to a
specified HTTP webserver. Given that this is APRS, the data from the source is _audio_. the
audio has the following specifications:

* channels: 1 (left)
* sample rate: 48 kHz
* sample format: 16 bit signed, little endian

This application will work with GQRX with no modification and the gnuradio-companion udp sink (see `.grc` flow for details).

# Usage

Running with no arguments:

```
python main.py
```

will listen for UDP on port 7355 and send a HTTP POST (for each message received) to the following uri:

```
http://127.0.0.1:5000/
```

with the following body (content-type: json):

```js
{
  // APRS message with type string
  // e.g. "APRS: TEST>WORLD:Hello, APRS"
  "data": "...",

  // python style epoch with type float
  // e.g. 1696160551.3251953
  "ts": 0000000000.0000000
}
```

the destination uri can be adjusted by launching the app with various flags (run `python main.py -h` for details).

# System Dependencies

this application spawns the following subprocess:

```sh
nc -l -u -p <udp_port> \
| sox -t raw -esigned-integer -b 16 -r 48000 - -esigned-integer -b 16 -r 22050 -t raw - \
| multimon-ng --timestamp -t raw -a AFSK1200 -A -
```

and thus requires `netcat`, `sox`, and `multimon-ng` to be installed on the base system

# Python Dependencies

* python3
* conda (optional)
* flask (optional - needed to run integration scripts in `test`)
* gnuradio (optional - needed to run integration scripts in `test`)

# Testing

Note: the python dependencies above.

Open gnuradio-companion and set the file path in the `File Source` block to point to `integration_test_data.bin` in the test directory.

start the example webserver in a new terminal.

```
cd test
FLASK_APP=integration_test_server.py FLASK_ENV=development flask run
```

start the service

```
python main.py
```

run the grc flowgraph




