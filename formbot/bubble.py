import math
from PIL import ImageDraw
import json

SQRT2 = math.sqrt(2)

TYPE_SINGLE = 1 # This is the default. The most-filled-in bubble is the one answer.
TYPE_MULTICHOICE = 2 # Multiple bubbles can be filled in.

class Bubble:
  def __init__(self, center, radius, answer=None):
    self.center = center
    self.radius = radius
    self.answer = answer
  def get_center(self): return self.center
  def set_center(self, center): self.center = center
  def get_radius(self): return self.radius
  def set_radius(self, radius): self.radius = radius
  # Draw this bubble on the image im.
  def draw(self, im):
    color = None
    if im.mode == "L":
      color = 0
    elif im.mode == "RGBA":
      color = (0,0,0,255)
    elif im.mode == "RGB":
      color = (0,0,0)
    draw = ImageDraw.Draw(im)
    draw.ellipse((self.center[0] - self.radius, self.center[1] - self.radius, self.center[0] + self.radius, self.center[1] + self.radius), outline=color)
  def fill(self, im):
    if im.mode == "L":
      color = 0
    elif im.mode == "RGBA":
      color = (0,0,0,255)
    elif im.mode == "RGB":
      color = (0,0,0)
    draw = ImageDraw.Draw(im)
    draw.ellipse((self.center[0] - self.radius, self.center[1] - self.radius, self.center[0] + self.radius, self.center[1] + self.radius), outline=color, fill=color)
  def get_average_fill(self, im):
    x = int(math.floor(self.radius / SQRT2))
    # XXX
    #print("x is %s" % x)
    box = (self.center[0] - x, self.center[1] - x, self.center[0] + x, self.center[1] + x)
    # XXX
    #print("box is %s %s %s %s" % (box[0], box[1], box[2], box[3]))
    temp = im.crop(box)
    # XXX
    #temp.show()
    val = 0
    coloradder = None
    if im.mode == "RGBA":
      coloradder = lambda p: p[3]*(p[0] * 299.0/1000 + p[1] * 587.0/1000 + p[2] * 114.0/1000)/255
    elif im.mode == "RGB":
      coloradder = lambda p: p[0] * 299.0/1000 + p[1] * 587.0/1000 + p[2] * 114.0/1000
    elif im.mode == "L":
      coloradder = lambda p: p
    for pixel in temp.getdata():
      val += coloradder(pixel)
    val = val / (temp.size[0] * temp.size[1])
    # XXX
    #print("val is %s" % val)
    # Marks are dark. Make black the high value.
    val = 255 - val
    return val

# Collection of bubbles, all of which correspond to one question
class BubbleSet:
  count = 0
  def __init__(self, bubbles=None, type=TYPE_SINGLE):
    if bubbles is None:
      self.bubbles = []
    else:
      self.bubbles = bubbles
    self.uid = "bubbleset%s" % BubbleSet.count
    self.name = None
    self.type = type # Check the type of the bubble set
  def get_bubbles(self): return self.bubbles
  def add_bubble(self, bubble): self.bubbles.append(bubble)
  def get_uid(self): return self.uid
  def draw(self, im):
    for b in self.bubbles:
      b.draw(im)

  def read_bubbles(self, im):
    if self.type == TYPE_MULTICHOICE:
      return self.get_multi_answers(im)
    return self.get_single_answer(im)

  # Check the bubble locations in image im. Determine which ones have been filled in.
  def get_multi_answers(self, im):
    threshold = 191 # 75% filled in
    filled = []
    for i in range(len(self.bubbles)):
      val = self.bubbles[i].get_average_fill(im)
      if (val > threshold):
        answer = self.bubbles[i].answer
        if (answer is not None):
          filled.append(answer)
        else:
          filled.append(i)
    return filled

  # Check the bubble locations in image im. Determine which bubble was filled in.
  def get_single_answer(self, im):
    maxfill = -1
    maxindex = -1
    for i in range(len(self.bubbles)):
      val = self.bubbles[i].get_average_fill(im)
      if (val > maxfill):
        maxfill = val
        maxindex = i
    assert(maxindex > -1)
    answer = self.bubbles[maxindex].answer
    if answer is not None:
      return answer
    return maxindex

class FormSets:
  def __init__(self, form_id, sets):
    self.form_id = form_id
    self.sets = sets

def readforms(s):
  return extract_data(json.loads(s))

def readform(filename):
  # Read the JSON string for the form data from the file
  formdatafile = file(filename, "r")
  # Load the form data
  formdata = json.load(formdatafile)
  return extract_data(formdata)

def extract_data(formdata, form_id=None):
  if form_id is None:
    if "id" in formdata:
      form_id = formdata["id"]
  sets = formdata["bubblesets"]
  #
  # Create objects from the form data
  formsets = []
  for bsdct in sets:
    bs = BubbleSet()
    for bubdct in bsdct["bubbles"]:
      if "answer" in bubdct:
        bs.add_bubble(Bubble(tuple(bubdct["center"]), bubdct["radius"], bubdct["answer"]))
      else:
        bs.add_bubble(Bubble(tuple(bubdct["center"]), bubdct["radius"]))
    if "name" in bsdct:
      bs.name = bsdct["name"]
    bstype = bsdct.get("type", None)
    if bstype is not None:
      bs.type = bstype
    formsets.append(bs)
  #
  return FormSets(form_id, formsets)

