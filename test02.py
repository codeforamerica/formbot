import math
from PIL import ImageDraw
from PIL import Image
import numpy as np
#from numpy import fft

from formbot.regmark import *


##
def imgmse(im1, im2):
  if im1.mode != "L":
    im1 = im1.convert("L")
  if im2.mode != "L":
    im2 = im2.convert("L")
  arr1 = img2array(im1)
  arr2 = img2array(im2)
  errarr = np.subtract(arr1, arr2)
  return np.sum(np.multiply(errarr, errarr)) / errarr.size

def make_affine(alpha, theta, w):
  return (alpha*np.cos(theta), -alpha*np.sin(theta), w[0], alpha*np.sin(theta), alpha*np.cos(theta), w[1])

def get_box(center, pad, size):
  return (max(0, center[0] - pad), max(center[1] - pad, 0), min(size[0], center[0] + pad), min(size[1], center[1] + pad))
##

im = Image.open("/Users/prashant/Downloads/dataport_sample_mod01.tiff")
form = Image.new("RGBA", im.size, (255,255,255,255))
r0 = RegMark((50,50,250,250))
r1 = RegMark((50,950,250,1150))
r2 = RegMark((550,950,750,1150))

form2 = form.copy()
r0.draw(form2)
r1.draw(form2)
r2.draw(form2)

# shift the form a little
#form2s = form2.transform(form2.size, Image.AFFINE, (1, 0, 15, 0, 1, 30))
theta = 7*np.pi/180
alpha = .94;
w = 15 + 30j
affine = (alpha*np.cos(theta), -alpha*np.sin(theta), int(np.real(w)), alpha*np.sin(theta), alpha*np.cos(theta), int(np.imag(w)))
tmp = Image.new("RGBA", im.size, (255,255,255,255))
#tmp.putdata(form2.getdata(), -1, 255)
tmp.putdata(map(lambda a: (255-a[0],255-a[1],255-a[2],255), form2.getdata()))
#form2s = tmp.transform(form2.size, Image.AFFINE, (np.cos(theta), -np.sin(theta), 15, np.sin(theta), np.cos(theta), 30), Image.BILINEAR)
form2s = tmp.transform(form2.size, Image.AFFINE, affine, Image.BILINEAR)
tmp = form2s.copy()
form2s.putdata(map(lambda a: (255-a[0],255-a[1],255-a[2],255), tmp.getdata()))

form2p = fiximage(form2s, r0, r1, r2)

mse = imgmse(form2, form2p)
print("mse: %s" % mse)

f2arr = img2array(form2)
f2arrp = img2array(form2p)

## r0loc = r0.find(form2s)
## r0loc_orig = r0.get_center()
## r1loc = r1.find(form2s)
## r1loc_orig = r1.get_center()
## r2loc = r2.find(form2s)
## r2loc_orig = r2.get_center()
## 
## r0shift = np.subtract(r0loc, r0loc_orig)
## r1shift = np.subtract(r1loc, r1loc_orig)
## r2shift = np.subtract(r2loc, r2loc_orig)
## 
## z0 = r0loc_orig[0] + 1j*r0loc_orig[1]
## z0p = r0loc[0] + 1j*r0loc[1]
## z1 = r1loc_orig[0] + 1j*r1loc_orig[1]
## z1p = r1loc[0] + 1j*r1loc[1]
## z2 = r2loc_orig[0] + 1j*r2loc_orig[1]
## z2p = r2loc[0] + 1j*r2loc[1]
## 
## # 0
## theta0 = -1j*np.log((z1p - z0p) / (z1 - z0))
## w0 = z0p - z0*np.exp(1j*theta0)
## # 1
## theta1 = -1j*np.log((z2p - z0p) / (z2 - z0))
## w1 = z0p - z0*np.exp(1j*theta1)
## 
## print("w0: %s, theta0: %s" % (w0, np.real(theta0)))
## print("w1: %s, theta1: %s" % (w1, np.real(theta1)))
## 
## #ymax = max(y.flat)
## 
## #yim = Image.new("L", y.shape, 255)
## #yim.putdata(y.flatten(), 1/ymax)
## 
## wp = (lambda x: (np.real(x), np.imag(x))) (np.average((w0, w1)))
## thetap = np.average((np.real(theta0), np.real(theta1)))
## #
## tmp = Image.new("RGBA", im.size, (255,255,255,255))
## tmp.putdata(map(lambda a: (255-a[0],255-a[1],255-a[2],255), form2s.getdata()))
## form2p = tmp.transform(form2.size, Image.AFFINE, (np.cos(thetap), -np.sin(thetap), wp[0], np.sin(thetap), np.cos(thetap), wp[1]))
## tmp = form2p.copy()
## form2p.putdata(map(lambda a: (255-a[0],255-a[1],255-a[2],255), tmp.getdata()))
