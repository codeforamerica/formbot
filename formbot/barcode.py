from PIL import Image
import subprocess
import glob
import os
import StringIO
import json
import requests
import StringIO


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
  # This code spun off a Java process, which doesn't work on heroku.
  ## decode = 'java', '-cp', 'lib/core.jar:lib/javase.jar', 'com.google.zxing.client.j2se.CommandLineRunner', '-'
  ## decode = subprocess.Popen(decode, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  ## #
  ## img.save(decode.stdin, 'PNG')
  ## decode.stdin.close()
  ## decode.wait()
  ## #
  ## decoded = decode.stdout.read().strip()

  # Make a call to a decoder API
  url = 'http://zxing.org/w/decode'
  f = StringIO.StringIO()
  img.save(f, 'PNG')
  f.seek(0)
  req = requests.post(url, files={'f': f}, data={'full': 'true'})
  # Trim the \n at the end of the result
  decoded = req.text[:-1]
  return decoded
