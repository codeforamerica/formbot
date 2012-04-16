from PIL import Image
import subprocess
import glob
import os
import StringIO
import json


def drawbarcode(img, filename):
  # Read the JSON string for the form data from the file
  formdatafile = file(filename, "r")
  # Load the form data
  formdata = json.load(formdatafile)
  data = formdata["barcode"]["data"]
  drawbarcode_json(img, formdata, data)

def drawbarcode_json(img, formdata, data):
  #
  bbox = tuple(formdata["barcode"]["bbox"])
  #
  width = bbox[2] - bbox[0]
  height = bbox[3] - bbox[1]
  #
  encode = 'java', '-cp', 'lib/core.jar:lib/javase.jar', 'com.google.zxing.client.j2se.CommandLineEncoder', '--width=%s' % width, '--height=%s' % height, '--output=-', data
  encode = subprocess.Popen(encode, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  (outdata, errdata) = encode.communicate()
  imagestring = StringIO.StringIO(outdata)
  tmp = Image.open(imagestring)
  img.paste(tmp, bbox)

def readbarcode(img):
  decode = 'java', '-cp', 'lib/core.jar:lib/javase.jar', 'com.google.zxing.client.j2se.CommandLineRunner', '-'
  decode = subprocess.Popen(decode, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  #
  img.save(decode.stdin, 'PNG')
  decode.stdin.close()
  decode.wait()
  #
  decoded = decode.stdout.read().strip()
  return decoded
