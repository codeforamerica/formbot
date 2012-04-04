from PIL import Image
import formbot.bubble as Bubble
import formbot.regmark as rm
import json

rm.DEBUG = True

FORMDATA = "formdata02.json"
INFILE = "form02_filled04.jpg"

# Read form data
formsets = Bubble.readform(FORMDATA)
#
# Read registration mark data
rmarks = rm.readform(FORMDATA)
#
# Load the image of the filled-out form
form_img = Image.open(INFILE)


##########
# Preprocess the image
##########
(w,h) = form_img.size
if w > h:
  form_img = form_img.transpose(Image.ROTATE_270)
  (w,h) = form_img.size
if h*(17.0/22.0) < w:
  # Pad the height
  hnew = int(w*(22.0/17.0))
  wnew = w
elif h*(17.0/22.0) > w:
  # Pad the width
  hnew = h
  wnew = int(h*(17.0/22.0))
tmp = Image.new("L", (wnew,hnew), 255)
tmp.paste(form_img, (0,0))
form_img = tmp.resize((1275, 1650), Image.BICUBIC)

#
# Adjust image to fit the prototype
form_img_fixed = rm.fiximage(form_img, rmarks[0], rmarks[1], rmarks[2])
