from PIL import Image
import bubble as Bubble
import regmark as rm
import json


SKELETON = "skeletonform01.tiff"
FORMDATA = "formdata01.json"
OUTFILE = "form01.tiff"

# Read the JSON string for the form data from the file
formdatafile = file(FORMDATA, "r")
# Load the form data
formdata = json.load(formdatafile)
formdatafile.close()


form_id = formdata["id"]
sets = formdata["sets"]
regs = formdata["regmarks"]

# Create bubble objects from the form data
formsets = Bubble.readform(FORMDATA)
#formsets = []
#for bsdct in sets:
#  bs = Bubble.BubbleSet()
#  for bubdct in bsdct["bubbles"]:
#    bs.add_bubble(Bubble.Bubble(tuple(bubdct["center"]), bubdct["radius"]))
#  formsets.append(bs)

# Load the skeletal form
form_img = Image.open(SKELETON)

# Draw the bubbles
for bs in formsets.sets:
  bs.draw(form_img)

# Draw the registration markers according to the data
rmarks = rm.readform(FORMDATA)
for mark in rmarks:
  mark.draw(form_img)
# XXX
#r0 = RegMark((50,50,250,250))
#r1 = RegMark((50,950,250,1150))
#r2 = RegMark((550,950,750,1150))
#r0.draw(form_img)
#r1.draw(form_img)
#r2.draw(form_img)

# Save the form
form_img.save(OUTFILE, "TIFF")
