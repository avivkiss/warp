from config import *
from common_tools import *
from blessings import Terminal
import time


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
    self.screen.add_component(Component(label=message))
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
          # print "n: " + str(self.term.height -n)
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
  def __init__(self, label=""):
    self.label = label

  def set_label(self, label):
    self.label = label

  def __str__(self):
    return self.label

class CounterComponent(Component):
  def __init__(self, format="{}"):
    self.count = 0
    self.format = format

  def increment(self):
    self.count += 1

  def update(self, count):
    self.count = count

  def __str__(self):
    return self.format.format(self.count)

class ProgressComponent(Component):
  def __init__(self, label="Progress", fill_char='#', empty_char =' ', expected_size=100, width=32, progress=0):
    super(ProgressComponent, self).__init__(label)
    self.expected_size = expected_size
    self.fill_char = fill_char
    self.progress = progress
    self.empty_char = empty_char
    self.width = width

  def update(self, progress):
    self.progress = progress

  def __str__(self):
    p = self.progress * self.width // self.expected_size
    return self.label + ": [" + self.fill_char * p + self.empty_char * (self.width - p) + "]"

def main():
  s = WarpInterface()

  s.redraw()
  time.sleep(4)

  s.exit()




  # print s.bottom_lines

if __name__ == '__main__':
  main()