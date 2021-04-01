# gpiocmd

Run arbitrary commands when GPIO buttons are pressed on Raspberry PI. Buttons can differentiate multiple actions by how many seconds one button is pressed. Actions can be configured to repeat at an interval defined in seconds. Used and tested with Adafruit 2.8" screen with four buttons.

## Installation

Install with the Python package manager. Example below installs version 0.9.0 for the current user.

```bash
pip3 install --user https://github.com/aheimsbakk/gpiocmd/archive/refs/tags/0.9.0.zip
```

## Usage

```
usage: gpiocmd.py [-h] [-v] [--log-format FORMAT] [-k] -c FILE

Run arbitrary commands when GPIO buttons are pressed on Raspberry PI. Buttons
can differentiate multiple actions by how many seconds one button is pressed.
Actions can be configured to repeat at an interval defined in seconds. Used and
tested with Adafruit 2.8" screen with four buttons.

optional arguments:
  -h, --help              show this help message and exit
  -v, --verbose           verbosity level increased with each to WARN, INFO and
                          DEBUG - ERROR and CRITICAL is always visible
  --log-format FORMAT     customize log format, see python logging package for
                          information on the format
  -k, --kill-running      kill running command before running new command

required arguments:
  -c FILE, --config FILE  YAML configuration file

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
      pressed_for: 1
    - run: echo button 1 pressed for 2 seconds
      pressed_for: 2
      repeat_every: 1
22:
  commands:
    - run: echo button 2 pressed
      repeat_every: 3
23:
  commands:
    - run: echo button 3 pressed
      background: true
27:
  commands:
    - run: echo button 4 pressed
      repeat_every: 1
```

<!---
# vim: set spell spelllang=en:
-->
