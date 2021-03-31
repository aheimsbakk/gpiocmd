#!/usr/bin/env python3
"""
Application for executing arbitrary command when GPIO buttons is pressed on Raspbery PI.
"""

import argparse
import logging
import subprocess
import sys
import time
import yaml

CONFIG = []

try:
    import RPi.GPIO as GPIO
except RuntimeError as err:
    print('''Error importing RPi.GPIO!
             This is probably because you need superuser privileges.
             You can achieve this by using 'sudo' to run your script''')

def setup_logging(verbosity, log_format):
    """
    Configure logging module for use in this script.
    """
    verbosity = min(verbosity, 3)
    loglevel = logging.ERROR - (verbosity * 10)
    logging.basicConfig(level=loglevel, format=log_format)

def log_exception(error_msg, exception, level=logging.ERROR):
    """
    Log an exception and exit program.
    """
    logging.log(level, error_msg, str(exception))
    logging.debug('', exc_info=True)
    try:
        sys.exit(exception.errno)
    except AttributeError:
        sys.exit(1)

def channel_fall_rise(channel):
    """
    Check is if a button is pressed. Check for both fall and rise.
    Return milliseconds between falling and rising.
    """

    channel_state = GPIO.input(channel)
    logging.debug("channel %d has value %d", channel, channel_state)

    if channel_state == GPIO.LOW:
        CONFIG[channel]['falling_time_ns'] = time.time_ns()

    if channel_state == GPIO.HIGH:
        rising_time_ns = time.time_ns()
        fall_time_ms = ( rising_time_ns - CONFIG[channel]['falling_time_ns'] ) // 10**6
        logging.info("Channel %d was falling for %d ms", channel, fall_time_ms)

        time_pressed = fall_time_ms // 1000
        commands = sorted(CONFIG[channel]['commands'], key=lambda c: c.get('wait', 0), reverse=True)
        for cmd in commands:
            if cmd.get('wait', 0) <= time_pressed:
                logging.debug('button pressed for %d seconds', time_pressed)

                # kill last command before running a new
                CONFIG.get('running', 0)
                proc = CONFIG.get('running', None)
                if proc is not None:
                    logging.debug("killing process %d", proc.pid)
                    proc.terminate()

                logging.info('will now run command: %s', cmd['run'])
                proc = subprocess.Popen(cmd['run'], shell=True)
                logging.debug('saving pid %d to memory', proc.pid)
                CONFIG['running'] = proc
                break

if __name__ == "__main__":
    DESCRIPTION = """
Run arbitrary commands when GPIO buttons is pressed on Rasberry PI. Buttons
can differentiate on multiple actions by how many seconds the button is pressed.
Used and tested with Adafruit 2.8" screen with four buttons.
"""

    EPILOG = """
Example YAML configuration file used with the -c option. This example only
executes the bash command.

---
- pin: 17
  seconds: 0
  cmd: bash -c 'echo button 17 pressed'
- pin: 17
  seconds: 1
  cmd: bash -c 'echo button 17 pressed for 1 second'
- pin: 27
  cmd: bash -c 'echo button 27 pressed'
"""

    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG,
        formatter_class=lambda prog:
        argparse.RawDescriptionHelpFormatter(prog, max_help_position=40, width=80))
    parser.add_argument('-v', '--verbose', dest='verbosity', action='count',
        help='''verbosity level increased with each to WARN, INFO and DEBUG -
            ERROR and CRITICAL is always visible''', default=0)
    parser.add_argument('--log-format', metavar='FORMAT', dest='log_format', type=str,
        help='customize log format, see python logging package for information on the format',
        default='%(filename)s: %(levelname)s: %(message)s')
    parser.add_argument('-k', '--kill-running', dest='kill', action='store_true',
        help='kill running command before running new command', default=False)

    required = parser.add_argument_group('required arguments')
    required.add_argument('-c', '--config', metavar='FILE', dest='config_file',
        required=True, type=argparse.FileType('r'), help='YAML configuration file')

    args = parser.parse_args()
    setup_logging(args.verbosity, args.log_format)

    try:
        CONFIG = yaml.safe_load(args.config_file.read())
        logging.debug("configuration read: %s", str(CONFIG))
    except yaml.YAMLError as err:
        log_exception("loading config file: %s", err)

    try:
        GPIO.setmode(GPIO.BCM)

        for ch in CONFIG.keys():
            GPIO.setup(ch, GPIO.IN, GPIO.PUD_UP)
            GPIO.add_event_detect(ch, GPIO.BOTH, channel_fall_rise, 75)

        while len(CONFIG.keys()) > 0:
            time.sleep(1)
    except KeyboardInterrupt as err:
        log_exception("keyboard interrupt %s", err, logging.INFO)

    for ch in CONFIG.keys():
        GPIO.cleanup(ch)

# vim: set spell spelllang=en:
