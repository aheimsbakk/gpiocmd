#!/usr/bin/env python3
"""
Application for executing arbitrary command when GPIO buttons is pressed on Raspbery PI.
"""

import argparse
import logging

def setup_logging(verbosity, log_format):
    """
    Configure logging module for use in this script.
    """
    verbosity = min(verbosity, 4)
    loglevel = logging.CRITICAL - (verbosity * 10)
    logging.basicConfig(level=loglevel, format=log_format)


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
        help='verbosity level', default=0)
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

# vim: set spell spelllang=en:
