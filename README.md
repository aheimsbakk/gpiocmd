# gpiocmd

Run an arbitrary command when a GPIO button is pressed on Rasberry PI. Used and tested with Adafruit 2.8" screen with four buttons.

## Usage

```
usage: gpiocmd.py [-h] [-v] [--log-format FORMAT] [-k] [-c FILE]

Run an arbitrary commands when GPIO buttons is pressed on Rasberry PI. Buttons
can differentiate on multiple actions by how many seconds the button is pressed.
Used and tested with Adafruit 2.8" screen with four buttons.

optional arguments:
  -h, --help              show this help message and exit
  -v, --verbose           verbosity level
  --log-format FORMAT     customize log format, see python logging package for
                          information on the format
  -k, --kill-running      kill running command before running new command
  -c FILE, --config FILE  YAML configuration file

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
```


## Configuration file format

Commands to run defined in a YAML file. Each command is connected to a pin and have a optional time in seconds connected to it. Command will only be run if minimum number of seconds have passed when the button is released. If seconds is not specified it defaults to `0`.

```yml
---
- pin: 17
  seconds: 0
  cmd: bash -c 'echo button 17 pressed'
- pin: 17
  seconds: 1
  cmd: bash -c 'echo button 17 pressed for 1 second'
- pin: 17
  seconds: 2
  cmd: bash -c 'echo button 17 pressed for 2 seconds'
- pin: 22
  seconds: 0
  cmd: bash -c 'echo button 22 pressed'
- pin: 23
  seconds: 0
  cmd: bash -c 'echo button 23 pressed'
- pin: 27
  seconds: 0
  cmd: bash -c 'echo button 27 pressed'
```
<!---
# vim: set spell spelllang=en:
-->
