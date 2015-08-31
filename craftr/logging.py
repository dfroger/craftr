# Copyright (C) 2015 Niklas Rosenstein
# All rights reserved.

import os
import sys
import textwrap

try:
  import colorama
except ImportError:
  colorama = None
else:
  colorama.init()


DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

levels = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL',
}

# Terminal styles for the logging output.
styles = {
  DEBUG: ('YELLOW', None, None),
  INFO: ('CYAN', None, None),
  WARNING: ('MAGENTA', None, None),
  ERROR: ('RED', None, None),
  CRITICAL: ('WHITE', 'RED', 'BRIGHT'),
}


def get_level_name(level):
  try:
    return levels[level]
  except KeyError:
    return 'Level {}'.format(level)


def get_level_style(level):
  if not colorama:
    return ('', '')
  try:
    fg, bg, attr = styles[level]
  except KeyError:
    return ('', '')

  prefix = ''
  if fg:
    prefix += getattr(colorama.Fore, fg)
  if bg:
    prefix += getattr(colorama.Back, bg)
  if attr:
    prefix += getattr(colorama.Style, attr)
  return (prefix, colorama.Style.RESET_ALL)


def emit(prefix, message, level, fp=None):
  ''' Emit the *message* with the specified *prefix* to the file-like
  object *fp*. If `fp.isatty()` returns True and if the `colorama`
  module is available, the output will be colorized. The prefix may
  contain a `{levelname}` format string which will automatically be
  substituted. '''

  fp = fp or sys.stdout
  prefix = str(prefix).format(levelname=get_level_name(level))
  if hasattr(fp, 'isatty') and fp.isatty():
    style = get_level_style(level)
  else:
    style = ('', '')

  width = terminal_size()[0] - len(prefix)
  lines = textwrap.wrap(message, width)

  fp.write(style[0])
  fp.write(prefix)
  fp.write(lines[0])
  fp.write('\n')
  for line in lines[1:]:
    fp.write(' ' * len(prefix))
    fp.write(line)
    fp.write('\n')
  fp.write(style[1])


def print_as_str(*objects, sep=' ', end='\n'):
  ''' Takes arguments to the `print()` function and returns a string
  the way it would be printed to the output file. '''

  return sep.join(str(x) for x in objects) + end


def terminal_size():
  ''' Determines the size of the terminal. '''

  if os.name == 'nt':
    # http://code.activestate.com/recipes/440694-determine-size-of-console-window-on-windows/
    import ctypes, struct
    h = ctypes.windll.kernel32.GetStdHandle(-12)
    csbi = ctypes.create_string_buffer(22)
    res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    if res:
      (bufx, bufy, curx, cury, wattr, left, top, right,
       bottom, maxx, maxy) = struct.unpack('hhhhHhhhhhh', csbi.raw)
      sizex = right - left + 1
      sizey = bottom - top + 1
    else:
      sizex, sizey = 80, 25
    return (sizex, sizey)
  else:
    # http://stackoverflow.com/a/3010495/791713
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h


class Logger(object):
  ''' Simple logger class. '''

  def __init__(self, prefix=None, level=0):
    super().__init__()
    self.prefix = prefix or 'craftr: '
    self.level = level

  def emit(self, level, *args, **kwargs):
    if level >= self.level:
      message = print_as_str(*args, **kwargs)
      emit(self.prefix, message, level)

  def debug(self, *args, **kwargs):
    self.emit(DEBUG, *args, **kwargs)

  def info(self, *args, **kwargs):
    self.emit(INFO, *args, **kwargs)

  def warn(self, *args, **kwargs):
    self.emit(WARNING, *args, **kwargs)

  def error(self, *args, **kwargs):
    self.emit(ERROR, *args, **kwargs)

  def critical(self, *args, **kwargs):
    self.emit(CRITICAL, *args, **kwargs)