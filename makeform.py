#!/usr/bin/env python
from PIL import Image
import formbot.bubble as Bubble
import formbot.regmark as rm
import json
import sys
import getopt

def usage():
  print("Usage:")
  print("makeform.py -i <skeletonfile> -d <formdatafile> -o <outputfile>")

def main(argv):
  try:
    opts, args = getopt.getopt(argv, "i:d:o:")
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  SKELETON = None
  FORMDATA = None
  OUTFILE = None
  for opt, arg in opts:
    if opt == "-h":
      usage()
      sys.exit()
    elif opt == "-i":
      SKELETON = arg
    elif opt == "-d":
      FORMDATA = arg
    elif opt == "-o":
      OUTFILE = arg
  if not (SKELETON or FORMDATA or OUTFILE):
    usage()
    sys.exit(2)
  # Read the JSON string for the form data from the file
  formdatafile = file(FORMDATA, "r")
  # Load the form data
  formdata = json.load(formdatafile)
  formdatafile.close()
  #
  # TODO: add a barcode to indicate the form id
  #form_id = formdata["id"]
  #
  # Create bubble objects from the form data
  formsets = Bubble.readform(FORMDATA)
  #
  # Load the skeletal form
  form_img = Image.open(SKELETON)
  #
  # Draw the bubbles
  for bs in formsets.sets:
    bs.draw(form_img)
  #
  # Draw the registration markers according to the data
  rmarks = rm.readform(FORMDATA)
  for mark in rmarks:
    mark.draw(form_img)
  #
  # Save the form
  form_img.save(OUTFILE, "TIFF")

if __name__ == "__main__":
  main(sys.argv[1:])

