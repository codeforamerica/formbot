from PIL import Image
import formbot.bubble as Bubble
import formbot.regmark as rm
import json


FORMDATA = "formdata01.json"

INFILE = "form01_filled02.tiff"

# Read form data
formsets = Bubble.readform(FORMDATA)

# Read registration mark data
rmarks = rm.readform(FORMDATA)

# Load the image of the filled-out form
form_img = Image.open(INFILE)

# Adjust image to fit the prototype
form_img_fixed = rm.fiximage(form_img, rmarks[0], rmarks[1], rmarks[2])

# Check responses to each bubble set
responses = []
for bs in formsets.sets:
  responses.append(bs.get_single_answer(form_img_fixed))

print("Form ID: %s" % formsets.form_id)
for i in range(len(responses)):
  print("Response #%s: %s" % (i, responses[i]))


