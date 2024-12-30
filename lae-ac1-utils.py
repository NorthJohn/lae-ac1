#
# uses a serial port
# using the GPIO on a rapberry pi requires extra setup which is not included
#
# TODO
# add polling/scanning function


NAME='LAE-AC1-utils'
VERSION=1.5

import minimalmodbus
import serial
import time
import csv
import logging
import argparse
import re
import sys


def readWrite(n, row, doWrite, value, timeout):

  mnemonic = row['Mnem.']
  descript = row['Description'] if row['Description'] else ""
  address = int(row['Address'])
  units =  row['Unit/Value'] if row['Unit/Value'] else ""
  defaultValue = row['Default value']
  scale = row['Scale']
  preamble = f'loop {n:2}, ' if n != None else ""
  logText = f'{preamble}{instr.address}.{address:3} {descript:45} {mnemonic}'

  try :
    if doWrite:  # write operation
      sval = value*10  if scale == 1 else value
      abc = instr.write_register(address, sval, 0, 6, False)
      #if n == None or (n % 10 == 0) :
      logging.info(f'{logText} =>{value:4}  {units}')

    else:             # read operation
      sval = instr.read_register(address, number_of_decimals=0, functioncode=3)
      rvalue = sval/10  if scale == 1 else sval
      #if n == None or (n % 10 == 0) :
      success = ''
      if value :
        success = 'OK' if rvalue == value else 'FAIL'
      logging.info(f'{logText} {value:6}  {units}  {success}')


  except Exception as ex :
    #if n == None or (n % 10 == 0) :
    logging.warning(f'{logText} {ex}')
    time.sleep(timeout)



if __name__ == "__main__":

  print(f"{NAME} version {VERSION}")

  usage = ["%prog <register1> <register2> ..."]
  parser = argparse.ArgumentParser(description='LAE AC1 register utilities')
  parser.add_argument("register", nargs='*', type=str, help='read multiple registers e.g. 1SP 2SP or addresses e.g. 203 213. When using --set to write, specify single register only ')
  parser.add_argument("-a", "--all", dest="all", action='store_true' , default=False, help="read ALL registers")
  parser.add_argument("--set", dest="setValue", type=float, help ='set register to SETVALUE')
  parser.add_argument("--device", dest="device", default='/dev/ttyUSB0', help="serial interface, default is %(default)s")

  parser.add_argument("--map", dest="modbusMap", default='lae-ac1-27.csv', help="CSV filename containinig map of register mnemonics and addresses, default is %(default)s")
  parser.add_argument("-f",          dest="force", action='store_true', default=False, help="force access to addresses not in the CSV file")

  parser.add_argument("-n", "--repeat", dest="loop", help="repeat LOOP times (only 1 write permitted). Sleeps 100ms between repeats", type=int, default=None)
  parser.add_argument("-t", dest="timeout", help="serial port transaction timeout and sleep following an exception, default is %(default).1f secs", type=float, default=0.5)
  parser.add_argument("-u", "--unit", default=1, help="AC1 modbus address, default is %(default)i", type=int)
  parser.add_argument("--lock", action='store_true', default=False, help="lock port to give exclusive access, default is False")
  parser.add_argument('--log', default='WARNING', help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL), default is %(default)s. Level DEBUG shows MinimalModbus messages including ASCII PDUs")

  args = parser.parse_args()

  # Configure the logging level based on the parsed argument
  logging.basicConfig(level=args.log.upper(), format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')

  rows= []

  ac1blankEntry = {
    'Reg.':'',
    'Address':'',
    'Mnem.':'???',
    'Description':'unmapped',
    'Range':'',
    'Unit/Value':'',
    'Default value':'',
    'Scale' : 0
  }
  with open(args.modbusMap, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = [row for row in reader]

#  rows = [(row) =>  for row in rows]
  for row in rows:
    m = re.search("\.[\d]+$",f"{row['Default value']}")
    row['Scale'] = 1 if m else 0


  # AC1-27 only responds to 7 bit even.
  # timeout need to set to hundreds of milliseconds or 1 sec
  # or don't set it all

  try :
    with serial.Serial(args.device, 9600, parity=serial.PARITY_EVEN, \
    bytesize=7, timeout=args.timeout, exclusive=args.lock, stopbits=1) as serial0:

      logging.debug(serial0)

      # LAE say:

        # The protocol used for communication is a subset of MODICON MODBUS 1 (MB1),
        # only functions 03 and 06 are supported. Data are exchanged in ASCII mode
        # with the following serial communication parameters:
        # Baudrate: 9600
        # Data bit: 7
        # Stop bit: 1
        # Parity: even


      instr=minimalmodbus.Instrument(serial0, args.unit, \
      mode=minimalmodbus.MODE_ASCII, \
      debug=logging.getLevelName(logging.getLogger().getEffectiveLevel())=='DEBUG')

      logging.debug(instr)

      writeCredits = 1 # hard code restrict number of writes to 1

      if args.all :
        args.register = [row['Mnem.'] for row in rows]

      #logging.debug(f'reading {",".join(args.register)}, set value to {args.setValue}')

      for n in range(0, args.loop if args.loop else 1):

        loopNum = n if args.loop else None
        if n :
          time.sleep(0.1)  # very arbitrary

        for address in args.register:
          logging.debug(row)

          rowFound = None
          for row in rows:
            if address == row['Address']   \
            or address.upper() == row['Mnem.']:
              rowFound = row
              break
            # no match for name or address
          if not rowFound:
            if not args.force:
              logging.warning(f'Unmapped address: {address}')
            else:
              logging.info(f'Reading unmapped adddress {args.register}')
              rowFound = ac1blankEntry
              rowFound['Address'] = address

          if rowFound:
            if args.setValue :
              if len(args.register) != 1:
                logging.warning('Can only write to one register at a time')
                break
              if writeCredits :
                readWrite(loopNum, rowFound, True, args.setValue, args.timeout)
                writeCredits -= 1
              else :
                logging.error('No write credits')
            readWrite(loopNum, rowFound, False, args.setValue, args.timeout)    # delay in call above

      # not a registered address
  except serial.serialutil.SerialException as ex :
    logging.warning(str(ex))
  except KeyboardInterrupt:
    sys.exit(0)


