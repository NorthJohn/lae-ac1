# lae-ac1-utils

## Purpose
A simple command line utilty to read and write the registers on an LAE AC1-27 heating/cooling controller over a modbus, asynchronous, serial, RS-485 connection.

## Dependencies
```
pip install minimalmodbus
```

## Usage
```
LAE-AC1-utils version 1.5
usage: lae-ac1-utils.py [-h] [-a] [--set SETVALUE] [--device DEVICE] [--map MODBUSMAP] [-f] [-n LOOP] [-t TIMEOUT] [-u UNIT] [--lock]
                        [--log LOG]
                        [register ...]

LAE AC1 register utilities

positional arguments:
  register              read multiple registers e.g. 1SP 2SP or addresses e.g. 203 213. When using --set to write, specify single register
                        only

options:
  -h, --help            show this help message and exit
  -a, --all             read ALL registers
  --set SETVALUE        set register to SETVALUE
  --device DEVICE       serial interface, default is /dev/ttyUSB0
  --map MODBUSMAP       CSV filename containinig map of register mnemonics and addresses, default is lae-ac1-27.csv
  -f                    force access to addresses not in the CSV file
  -n LOOP, --repeat LOOP
                        repeat LOOP times (only 1 write permitted). Sleeps 100ms between repeats
  -t TIMEOUT            serial port transaction timeout and sleep following an exception, default is 0.5 secs
  -u UNIT, --unit UNIT  AC1 modbus address, default is 1
  --lock                lock port to give exclusive access, default is False
  --log LOG             Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL), default is WARNING. Level DEBUG shows MinimalModbus
                        messages including ASCII PDUs
```

Example of register reads
```
$ python3 lae-ac1-utils.py   1sp 2sp
LAE-AC1-utils version 1.5
18:23:51 INFO: 1.203 Effective temp. set point channel 1           1SP    2.6  °C or °F
18:23:52 INFO: 1.213 Effective temp. set point channel 2           2SP   16.0  °C or °F
```
Example of register write.  Writes are verified with a subsequent read.
```
$ python3 lae-ac1-utils.py   1sp --set 3.0
LAE-AC1-utils version 1.5
18:24:39 INFO: 1.203 Effective temp. set point channel 1           1SP => 3.0  °C or °F
18:24:39 INFO: 1.203 Effective temp. set point channel 1           1SP    3.0  °C or °F  ✅
```
Example of register read with log level set to debug
```
$ python3 lae-ac1-utils.py   1sp 2sp  --log DEBUG
LAE-AC1-utils version 1.5
18:26:11 DEBUG: Serial<id=0x7fe6400ba160, open=True>(port='/dev/ttyUSB0', baudrate=9600, bytesize=7, parity='E', stopbits=1, timeout=0.5, xonxoff=False, rtscts=False, dsrdtr=False)
18:26:11 DEBUG: minimalmodbus.Instrument<id=0x7fe6400bad90, address=1, mode=ascii, close_port_after_each_call=False, precalculate_read_size=True, clear_buffers_before_each_transaction=True, handle_local_echo=False, debug=True, serial=Serial<id=0x7fe6400ba160, open=True>(port='/dev/ttyUSB0', baudrate=9600, bytesize=7, parity='E', stopbits=1, timeout=0.5, xonxoff=False, rtscts=False, dsrdtr=False)>
MinimalModbus debug mode. Will write to instrument (expecting 15 bytes back): 3A 30 31 30 33 30 30 43 42 30 30 30 31 33 30 0D 0A (17 bytes)
MinimalModbus debug mode. Clearing serial buffers for port /dev/ttyUSB0
MinimalModbus debug mode. No sleep required before write. Time since previous read: 1819708238.58 ms, minimum silent period: 4.01 ms.
MinimalModbus debug mode. Response from instrument: 3A 30 31 30 33 30 32 30 30 31 45 44 43 0D 0A (15 bytes), roundtrip time: 0.2 ms. Timeout for reading: 500.0 ms.

18:26:11 INFO: 1.203 Effective temp. set point channel 1           1SP    3.0  °C or °F
MinimalModbus debug mode. Will write to instrument (expecting 15 bytes back): 3A 30 31 30 33 30 30 44 35 30 30 30 31 32 36 0D 0A (17 bytes)
MinimalModbus debug mode. Clearing serial buffers for port /dev/ttyUSB0
MinimalModbus debug mode. Sleeping 2.26 ms before sending. Minimum silent period: 4.01 ms, time since read: 1.75 ms.
MinimalModbus debug mode. Response from instrument: 3A 30 31 30 33 30 32 30 30 41 30 35 41 0D 0A (15 bytes), roundtrip time: 0.2 ms. Timeout for reading: 500.0 ms.

18:26:11 INFO: 1.213 Effective temp. set point channel 2           2SP   16.0  °C or °F
```

