import scipy as sp
#import scipy.misc as misc
import numpy as np
#import matplotlib.pyplot as plt
from PIL import Image

import bubble

#im = plt.imread("/Users/prashant/Downloads/dataport_sample.tiff")

#plt.imshow(im)

#x = array([ [ [1,2,3], [4,5,6], [7,8,9] ], [[10,11,12], [13,14,15], [16,17,18]]])

#x = im[...,...,0]


im = Image.open("/Users/prashant/Downloads/dataport_sample_mod01.tiff")

#minval = 255
#val = 255
#for i in range(im.size[0]):
#  for j in range(im.size[1]):
#    val = min(im.getpixel((i,j)))
#    if val < minval:
#      minval = val


im2 = im.crop((120,200,420,250))
im2.load()
im2a = im2.crop((0,0,59,50))
im2b = im2.crop((60,0,119,50))
im2c = im2.crop((120,0,179,50))
im2d = im2.crop((180,0,239,50))
im2e = im2.crop((240,0,299,50))


bs1 = bubble.BubbleSet()
bs1.add_bubble(bubble.Bubble((150, 225), 15))
bs1.add_bubble(bubble.Bubble((210, 225), 15))
bs1.add_bubble(bubble.Bubble((270, 225), 15))
bs1.add_bubble(bubble.Bubble((330, 225), 15))
bs1.add_bubble(bubble.Bubble((390, 225), 15))

bs2 = bubble.BubbleSet()
bs2.add_bubble(bubble.Bubble((150, 260), 15))
bs2.add_bubble(bubble.Bubble((210, 260), 15))
bs2.add_bubble(bubble.Bubble((270, 260), 15))
bs2.add_bubble(bubble.Bubble((330, 260), 15))
bs2.add_bubble(bubble.Bubble((390, 260), 15))

print("Answer 1: %s" % bs1.get_single_answer(im))
print("Answer 2: %s" % bs2.get_single_answer(im))

form = Image.new("RGBA", im.size, (255,255,255,255))

bs1.draw(form)
bs2.draw(form)

form_filled = form.copy()
bs1.bubbles[3].fill(form_filled)
bs2.bubbles[1].fill(form_filled)

print("Answer 1: %s" % bs1.get_single_answer(form_filled))
print("Answer 2: %s" % bs2.get_single_answer(form_filled))


form_filled02 = Image.open("/Users/prashant/tmp/form_filled02.tiff")
print("Answer 1: %s" % bs1.get_single_answer(form_filled02))
print("Answer 2: %s" % bs2.get_single_answer(form_filled02))
