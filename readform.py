#!/usr/bin/env python
from PIL import Image
import formbot.bubble as Bubble
import formbot.regmark as rm
import json
import sys
import getopt


def usage():
  print("Usage:")
  print("readform.py -i <inputfile> -d <formdatafile>")

def main(argv):
  try:
    opts, args = getopt.getopt(argv, "i:d:")
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  INFILE = None
  FORMDATA = None
  for opt, arg in opts:
    if opt == "-h":
      usage()
      sys.exit()
    elif opt == "-i":
      INFILE = arg
    elif opt == "-d":
      FORMDATA = arg
  if not (INFILE or FORMDATA):
    usage()
    sys.exit(2)
  #
  # TODO: First we should read the registration mark data, which will apply to the whole set of forms
  # for a particular survey project. Second, we fix the scanned image. Third, we read the barcode,
  # so we can look up the bubble set information. Last, we check which bubbles have been filled in.
  #
  # Read form data
  formsets = Bubble.readform(FORMDATA)
  #
  # Read registration mark data
  rmarks = rm.readform(FORMDATA)
  #
  # Load the image of the filled-out form
  form_img = Image.open(INFILE)
  #
  # Adjust image to fit the prototype
  form_img_fixed = rm.fiximage(form_img, rmarks[0], rmarks[1], rmarks[2])
  #
  # Check responses to each bubble set
  responses = []
  for bs in formsets.sets:
    responses.append(bs.get_single_answer(form_img_fixed))
  #
  print("Form ID: %s" % formsets.form_id)
  for i in range(len(responses)):
    print("Response #%s: %s" % (i, responses[i]))


if __name__ == "__main__":
  main(sys.argv[1:])

