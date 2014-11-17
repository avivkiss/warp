from config import *
from common_tools import *
from blessings import Terminal
import time, threading

SLEEP_TIME = 0.1

class WarpInterface(object):
  def __init__(self):
    self.screen = Screen()

    self.progress_bar = ProgressComponent()
    self.screen.add_component(self.progress_bar, to_bottom=True)

    self.status_line = Line()
    self.files_sent_indicator = CounterComponent(format="Sent {} files. ")
    self.files_processed_indicator = CounterComponent(format="Processed {} files.")
    self.status_line.add_component(self.files_sent_indicator)
    self.status_line.add_component(self.files_processed_indicator)
    self.screen.add_line(self.status_line, to_bottom=True)

  def log_message(self, message):
    self.screen.add_component(Component(message))
    self.redraw()

  def redraw(self):
    self.screen.redraw()

  def exit(self):
    self.screen.exit()


class Screen(object):
  def __init__(self):
    self.term = Terminal()
    self.top_lines = {}
    self.bottom_lines = {}
    self.next_line_top = 0
    self.next_line_bottom = 1

    print self.term.enter_fullscreen()

  def redraw(self):
    print self.term.clear()

    for n, line in self.top_lines.iteritems():
      with self.term.location(0, n):
        for component in line:
          print str(component),

    for n, line in self.bottom_lines.iteritems():
      with self.term.location(0, self.term.height - n):
        for component in line:
          print str(component),

    sys.stdout.flush()

  def add_line(self, line, to_bottom=False):
    if to_bottom is False:
      self.top_lines[self.next_line_top] = line
      self.next_line_top += 1
    else:
      self.bottom_lines[self.next_line_bottom] = line
      self.next_line_bottom += 1

  def add_component(self, component, to_bottom=False):
    if to_bottom is False:
      self.top_lines[self.next_line_top] = Line(comp=component)
      self.next_line_top += 1
    else:
      self.bottom_lines[self.next_line_bottom] = Line(comp=component)
      self.next_line_bottom += 1

  def exit(self):
    print self.term.clear()
    print self.term.exit_fullscreen()


class Line(object):
  def __init__(self, comp=None):
    self.components = []

    if comp is not None:
      self.components.append(comp)

  def add_component(self, component):
    self.components.append(component)

  def __iter__(self):
    for each in self.components:
      yield each


class Component(object):
  def __init__(self, value=""):
    self.value = value
    self.active = True

  def set_label(self, value):
    self.value = value

  def set_update(self, func):
    def update():
      while self.active:
        try:
          self.value = func()
        except:
          break
        time.sleep(SLEEP_TIME)

    thread = threading.Thread(target=update)
    thread.setDaemon(True)
    thread.start()

  def __str__(self):
    return self.value


class CounterComponent(Component):
  def __init__(self, format="{}"):
    self.value = 0
    self.format = format
    self.active = True

  def increment(self):
    self.value += 1

  def __str__(self):
    return self.format.format(self.value)


class ProgressComponent(Component):
  def __init__(self, label="Progress", fill_char='#', empty_char=' ', expected_size=100, progress=0):
    super(ProgressComponent, self).__init__(label)
    self.expected_size = expected_size
    self.fill_char = fill_char
    self.progress = progress
    self.empty_char = empty_char
    self.term = Terminal()
    self.label = label

    self.value = (expected_size, progress, False)

  def __str__(self):
    self.progress = self.value[1]
    self.expected_size = self.value[0]

    if self.value[2] and self.progress == self.expected_size:
      self.fill_char = "V"

    width = self.term.width - len(self.label) - 4
    p = self.progress * width // self.expected_size
    return self.label + ": [" + self.fill_char * p + self.empty_char * (width - p) + "]"
