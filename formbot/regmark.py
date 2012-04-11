import math
from PIL import ImageDraw
from PIL import Image
import numpy as np
from numpy import fft
import json

DEBUG = False

# Create a 2D array from an image
def img2array(im):
  im = im.convert("L")
  x = np.empty(flip(im.size))
  x.flat = im.getdata()
  x = 255 - x
  return x

def array2img(x):
  xim = Image.new("L", x.shape, 255)
  xim.putdata(x.transpose().flatten())
  return xim

def flip(pair):
  return (pair[1], pair[0])

class RegMark:
  def __init__(self, bbox):
    self.bbox = bbox
    x = bbox[2] - bbox[0]
    y = bbox[3] - bbox[1]
    self.zbbox = (0, 0, x, y)
    self.zinnerbbox = map(lambda a: math.floor(a), (x/4, x/4, 3*x/4, 3*x/4))
    self.innerbbox = (bbox[0] + self.zinnerbbox[0],
        bbox[1] + self.zinnerbbox[1],
        bbox[0] + self.zinnerbbox[2],
        bbox[1] + self.zinnerbbox[3])
  def get_center(self):
    width = self.bbox[2] - self.bbox[0]
    height = self.bbox[3] - self.bbox[1]
    return (self.bbox[0] + int(width/2), self.bbox[1] + int(height/2))
  def draw(self, im=None):
    if im is None:
      im = Image.new("RGBA", (self.zbbox[2], self.zbbox[3]), (255,255,255,255))
      bbox = self.zbbox;
      innerbbox = self.zinnerbbox
    else:
      bbox = self.bbox;
      innerbbox = self.innerbbox
    self.drawhelp(bbox, innerbbox, im)
    #d.ellipse(bbox, outline=(0,0,0,255))
    #d.ellipse(innerbbox, outline=(0,0,0,255), fill=(0,0,0,255))
    return im
  def drawhelp(self, bbox, innerbbox, im):
    d = ImageDraw.Draw(im)
    color = None
    if im.mode == "RGBA":
      color = (0,0,0,255)
    elif im.mode == "RGB":
      color = (0,0,0)
    elif im.mode == "L":
      color = 0
    d.ellipse(bbox, outline=color)
    d.ellipse(innerbbox, outline=color, fill=color)
  def find(self, im):
    # Create a 2D array from the image
    if im.mode != "L":
      im = im.convert("L")
    x = np.empty(flip(im.size))
    # For the signal/filter, a mark is a high value. For the image file, a mark is a low value (black)
    x.flat = im.getdata()
    x = 255 - x
    #
    # Create a 2D filter array from the registration mark
    regim = Image.new("L", im.size, 255)
    self.drawhelp(self.zbbox, self.zinnerbbox, regim)
    h = np.empty(flip(regim.size))
    # For the signal/filter, a mark is a high value. For the image file, a mark is a low value (black)
    h.flat = regim.getdata()
    h = 255 - h
    #
    # Take FFTs of image and filter
    X = fft.fft2(x)
    H = fft.fft2(h)
    #
    # Find the inverse FFT of the product
    Y = np.multiply(X, H)
    y = np.real(fft.ifft2(Y))
    #
    # Shift to account for the filter
    width = self.bbox[2] - self.bbox[0]
    height = self.bbox[3] - self.bbox[1]
    y = np.roll(np.roll(y, -int(width/2), 0), -int(height/2), 1)
    #
    # Find the maxima. Look near the expected location.
    search_buffer = 100
    expected_min = (max(self.bbox[0] - search_buffer, 0), max(self.bbox[1] - search_buffer, 0))
    expected_max = (min(self.bbox[2] + search_buffer, y.shape[1]), min(self.bbox[3] + search_buffer, y.shape[0]))
    if DEBUG:
      print("expected_min: (%s, %s)" % expected_min)
      print("expected_max: (%s, %s)" % expected_max)
    maxval = 0
    maxloc = (-1, -1)
    # TODO: Use numpy array operations to make this more efficient
    for j in range(expected_min[0], expected_max[0]):
      for i in range(expected_min[1], expected_max[1]):
        if y[i,j] > maxval:
          maxloc = (i,j)
          maxval = y[i,j]
    maxloc = flip(maxloc)
    if DEBUG:
      print("maxloc: (%s, %s)" % maxloc)
      print("maxval: %s" % maxval)
    return maxloc

# TODO: work with a list of registration marks. Two is probably enough, three can be optional.
def fiximage(ims, r0, r1, r2):
  ims = ims.convert("L")
  # Find the registration mark locations in the shifted image
  r0loc = r0.find(ims)
  r1loc = r1.find(ims)
  r2loc = r2.find(ims)
  # Get the original registration mark locations
  r0loc_orig = r0.get_center()
  r1loc_orig = r1.get_center()
  r2loc_orig = r2.get_center()
  #
  # Turn the points into complex numbers to make the math simpler
  z0 = r0loc_orig[0] + 1j*r0loc_orig[1]
  z0p = r0loc[0] + 1j*r0loc[1]
  z1 = r1loc_orig[0] + 1j*r1loc_orig[1]
  z1p = r1loc[0] + 1j*r1loc[1]
  z2 = r2loc_orig[0] + 1j*r2loc_orig[1]
  z2p = r2loc[0] + 1j*r2loc[1]
  #
  # 0
  tmp = (z1p - z0p) / (z1 - z0)
  theta0 = np.angle(tmp)
  alpha0 = np.abs(tmp)
  w0 = z0p - alpha0*z0*np.exp(1j*theta0)
  if DEBUG: print("alpha0: %s\ttheta0: %s\tw0: %s" % (alpha0, theta0, w0))
  # 1
  tmp = (z2p - z0p) / (z2 - z0)
  theta1 = np.angle(tmp)
  alpha1 = np.abs(tmp)
  w1 = z0p - alpha1*z0*np.exp(1j*theta1)
  if DEBUG: print("alpha1: %s\ttheta1: %s\tw1: %s" % (alpha1, theta1, w1))
  #
  # Average the calcuated rotation angles and shifts
  wp = (lambda x: (np.real(x), np.imag(x))) (np.average((w0, w1)))
  thetap = np.average((np.real(theta0), np.real(theta1)))
  alphap = (alpha0 + alpha1)/2
  if DEBUG: print("alphap: %s\tthetap: %s\twp: %s" % (alphap, thetap, wp))
  #
  # Create a fixed version of the input image
  tmp = Image.new("L", ims.size, 255)
  tmp.putdata(ims.getdata(), -1, 255)
  affine = (alphap*np.cos(thetap), -alphap*np.sin(thetap), wp[0], alphap*np.sin(thetap), alphap*np.cos(thetap), wp[1])
  imfix = tmp.transform(ims.size, Image.AFFINE, affine, Image.BILINEAR)
  tmp = imfix.copy()
  imfix.putdata(tmp.getdata(), -1, 255)
  #
  return imfix


def readforms(s):
  return extract_data(json.loads(s))

def readform(filename):
  # Read the JSON string for the form data from the file
  formdatafile = file(filename, "r")
  # Load the form data
  formdata = json.load(formdatafile)
  return extract_data(formdata)

def extract_data(formdata):
  #
  regs = formdata["regmarks"]
  rmarks = []
  for rmdct in regs:
    mark = RegMark(tuple(rmdct["bbox"]))
    rmarks.append(mark)
  return rmarks
