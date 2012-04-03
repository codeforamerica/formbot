import math
from PIL import ImageDraw
from PIL import Image
import numpy as np
from numpy import fft
import json


# Create a 2D array from an image
def img2array(im):
  im = im.convert("L")
  x = np.zeros(flip(im.size))
  imseq = im.getdata()
  x.flat = map(lambda a: 255 - a, imseq)
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
    elif im.mode == "L":
      color = 0
    d.ellipse(bbox, outline=color)
    d.ellipse(innerbbox, outline=color, fill=color)
  def find(self, im):
    # Create a 2D array from the image
    im = im.convert("L")
    x = np.zeros(flip(im.size))
    imseq = im.getdata()
    x.flat = map(lambda a: 255 - a, imseq)
    #x = x.transpose()
    #
    # Create a 2D filter array from the registration mark
    regim = Image.new("L", im.size, 255)
    self.drawhelp(self.zbbox, self.zinnerbbox, regim)
    h = np.zeros(flip(regim.size))
    regimseq = regim.getdata()
    # For the signal/filter, a mark is a high value. For the image, a mark is a low value (black)
    h.flat = map(lambda a: 255 - a, regimseq)
    #h = h.transpose()
    #
    # Take FFTs of image and filter
    X = fft.fft2(x)
    H = fft.fft2(h)
    # XXX
    #print(X.shape)
    #print(H.shape)
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
    # XXX
    print("expected_min: (%s, %s)" % expected_min)
    print("expected_max: (%s, %s)" % expected_max)
    maxval = 0
    maxloc = (-1, -1)
    for j in range(expected_min[0], expected_max[0]):
      for i in range(expected_min[1], expected_max[1]):
        if y[i,j] > maxval:
          maxloc = (i,j)
          maxval = y[i,j]
    maxloc = flip(maxloc)
    # XXX
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
  #  XXX Calculate the shift vectors
  #r0shift = np.subtract(r0loc, r0loc_orig)
  #r1shift = np.subtract(r1loc, r1loc_orig)
  #r2shift = np.subtract(r2loc, r2loc_orig)
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
  theta0 = -1j*np.log((z1p - z0p) / (z1 - z0))
  w0 = z0p - z0*np.exp(1j*theta0)
  # 1
  theta1 = -1j*np.log((z2p - z0p) / (z2 - z0))
  w1 = z0p - z0*np.exp(1j*theta1)
  #
  # XXX
  #print("w0: %s, theta0: %s" % (w0, np.real(theta0)))
  #print("w1: %s, theta1: %s" % (w1, np.real(theta1)))
  #
  # Average the calcuated rotation angles and shifts
  wp = (lambda x: (np.real(x), np.imag(x))) (np.average((w0, w1)))
  thetap = np.average((np.real(theta0), np.real(theta1)))
  #
  # Create a fixed version of the input image
  tmp = Image.new("L", ims.size, 255)
  tmp.putdata(map(lambda a: 255-a, ims.getdata()))
  imfix = tmp.transform(ims.size, Image.AFFINE, (np.cos(thetap), -np.sin(thetap), wp[0], np.sin(thetap), np.cos(thetap), wp[1]), Image.BILINEAR)
  tmp = imfix.copy()
  imfix.putdata(map(lambda a: 255-a, tmp.getdata()))
  #
  return imfix


def readform(filename):
  # Read the JSON string for the form data from the file
  formdatafile = file(filename, "r")
  # Load the form data
  formdata = json.load(formdatafile)
  #
  regs = formdata["regmarks"]
  rmarks = []
  for rmdct in regs:
    mark = RegMark(tuple(rmdct["regmark"]["bbox"]))
    rmarks.append(mark)
  return rmarks
