#!/usr/bin/env python3
"""
Application for executing arbitrary command when GPIO buttons is pressed on Raspbery PI.
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import threading
import time
import yaml

# save configuration to a global variable
CONFIG = []

# kill command before running a new one
KILL = False

# RPi.GPIO not found
ERROR = None

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError as err:
    ERROR = err

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

def run_proc(command, repeat, background=False):
    """
    Run process, once or repeat every "repeat" second.
    """

    # run thread as long as no other command is started
    while CONFIG.get('running', False):
        bgstr = " in background" if background else ""
        logging.info('will now run%s command: %s', bgstr, command)
        proc = subprocess.Popen(command, shell=True, start_new_session=True)

        if not background:
            logging.debug('saving pid %d to memory', proc.pid)
            CONFIG['process'] = proc

        if repeat == 0:
            break

        # sleep for repeat seconds, stop if we need to
        sleep_for = repeat
        while CONFIG.get('running', False) and sleep_for > 0:
            time.sleep(0.05)
            sleep_for -= 0.05

def button_pressed(channel):
    """
    Check is if a button is pressed.
    If button was pressed, run corresponding command.
    """

    # fetch the state of the button pressed
    channel_state = GPIO.input(channel)
    logging.debug("channel %d has value %d", channel, channel_state)

    if channel_state == GPIO.LOW:
        # log time button was pressed in nanoseconds
        CONFIG[channel]['falling_time_ns'] = time.time_ns()

    if channel_state == GPIO.HIGH:
        # log time button was released in nanoseconds
        rising_time_ns = time.time_ns()

        # how long was the button pressed in milliseconds
        fall_time_ms = ( rising_time_ns - CONFIG[channel]['falling_time_ns'] ) // 10**6
        logging.info("Channel %d was falling for %d ms", channel, fall_time_ms)

        # how long button was pressed in seconds
        time_pressed = fall_time_ms // 1000

        # sort commands for the button, in reverse order
        commands = sorted(CONFIG[channel]['commands'], key=lambda c: c.get('wait', 0), reverse=True)
        for cmd in commands:

            # if button was pressed equal or longer than the command
            if cmd.get('wait', 0) <= time_pressed:
                logging.debug('button pressed for %d seconds', time_pressed)

                # kill last command before running a new if it's not a background command
                if not cmd.get('background', False):
                    proc = CONFIG.get('process', None)
                    CONFIG['running'] = False

                    if proc is not None and KILL:
                        logging.debug("killing process %d and subprocesses", proc.pid)
                        pgrp = os.getpgid(proc.pid)
                        os.killpg(pgrp, signal.SIGTERM)

                    # wait for last command to finish
                    if "thread" in CONFIG:
                        CONFIG['thread'].join()

                # run command and save it so we can kill it when a new button is pressed
                CONFIG['running'] = True
                thread = threading.Thread(target=run_proc, args=(cmd['run'],
                    cmd.get('repeat', 0), cmd.get('background', False)), daemon=True)
                thread.start()

                # only save thread if it's not a background process, so we can stop it
                if not cmd.get('background', False):
                    CONFIG['thread'] = thread
                break

if __name__ == "__main__":
    DESCRIPTION = """
Run arbitrary commands when GPIO buttons are pressed on Raspberry PI. Buttons
can differentiate multiple actions by how many seconds one button is pressed.
Actions can be configured to repeat at an interval defined in seconds. Used and
tested with Adafruit 2.8" screen with four buttons.
"""

    EPILOG = """
Example YAML configuration file used with the -c option. Configure channels
(GPIO pins in BCM mode) and add commands that will be executed when buttons are
pressed. Add multiple commands for each button. Command runs immediately or
after how many seconds the button was pressed. Repeat the last command every
repeat second until the next command is executed. Background command will not
interrupt the running command, and will not be killed even if -k is specified.
This example only executes echo examples.

---
17:
  commands:
    - run: echo button 1 pressed
    - run: echo button 1 pressed for 1 second
      wait: 1
    - run: echo button 1 pressed for 2 seconds
      wait: 2
      repeat: 1
22:
  commands:
    - run: echo button 2 pressed
      repeat: 3
23:
  commands:
    - run: echo button 3 pressed
      background: true
27:
  commands:
    - run: echo button 4 pressed
      repeat: 1
"""

    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG,
        formatter_class=lambda prog:
        argparse.RawDescriptionHelpFormatter(prog, max_help_position=40, width=80))

    # parse optional command line arguments
    parser.add_argument('-v', '--verbose', dest='verbosity', action='count',
        help='''verbosity level increased with each to WARN, INFO and DEBUG -
            ERROR and CRITICAL is always visible''', default=0)
    parser.add_argument('--log-format', metavar='FORMAT', dest='log_format', type=str,
        help='customize log format, see python logging package for information on the format',
        default='%(filename)s: %(levelname)s: %(message)s')
    parser.add_argument('-k', '--kill-running', dest='kill', action='store_true',
        help='kill running command before running new command', default=False)

    # parse required command line arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument('-c', '--config', metavar='FILE', dest='config_file',
        required=True, type=argparse.FileType('r'), help='YAML configuration file')

    # do the actual parsing
    args = parser.parse_args()
    setup_logging(args.verbosity, args.log_format)

    # If module was not found
    if ERROR is not None:
        log_exception("%s", ERROR)

    # set variable for killing command before running a new one
    KILL = args.kill

    # load the configuration file
    try:
        CONFIG = yaml.safe_load(args.config_file.read())
        logging.debug("configuration read: %s", str(CONFIG))
    except yaml.YAMLError as err:
        log_exception("loading config file: %s", err)

    try:
        # set BCM mode for channels (GPIO pins)
        GPIO.setmode(GPIO.BCM)

        # traverse all channels in configuration file and register events
        # all for channels
        for ch in CONFIG.keys():
            GPIO.setup(ch, GPIO.IN, GPIO.PUD_UP)
            GPIO.add_event_detect(ch, GPIO.BOTH, button_pressed, 75)

        # sleep as long we have at least one channel in configuration file
        while len(CONFIG.keys()) > 0:
            time.sleep(1)
    except KeyboardInterrupt as err:
        log_exception("keyboard interrupt %s", err, logging.INFO)
    finally:
        # do cleanup by resetting GPIO channels
        for ch in CONFIG.keys():
            if isinstance(ch, int):
                GPIO.cleanup(int(ch))

# vim: set spell spelllang=en:
