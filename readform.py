#!/usr/bin/env python
from PIL import Image
import formbot.bubble as Bubble
import formbot.regmark as rm
import formbot.barcode as bc
import json
import sys
import getopt
import subprocess
import glob
import os


def usage():
  print("Usage:")
  print("readform.py -i <inputfile> -d <formdatafile>")

#def readcode(img):
#  decode = 'java', '-classpath', ':'.join(glob.glob('lib/*.jar')), 'qrdecode'
#  decode = subprocess.Popen(decode, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#  #
#  img.save(decode.stdin, 'PNG')
#  decode.stdin.close()
#  decode.wait()
#  #
#  decoded = decode.stdout.read().strip()
#  return decoded

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
  # Read registration mark data
  rmarks = rm.readform(FORMDATA)
  #
  # Load the image of the filled-out form
  form_img = Image.open(INFILE)
  #
  # Adjust image to fit the prototype
  # TODO: After we try fixing the image once, the registration markers are easier to find.
  # So if we try fixing again, we get closer. This is a little hacky, though. We should make
  # that part of the registration procedure.
  form_img_fixed = rm.fiximage(form_img, rmarks[0], rmarks[1], rmarks[2])
  form_img_fixed = rm.fiximage(form_img_fixed, rmarks[0], rmarks[1], rmarks[2])
  #
  # Read the barcode
  barcodedata = bc.readbarcode(form_img_fixed)
  print("bar code data: %s" % barcodedata)
  #
  # Read form data
  formsets = Bubble.readform(FORMDATA)
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

