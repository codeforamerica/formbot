#!/usr/bin/env python

import urllib2
import urllib
import StringIO
import formbot.bubble as Bubble
import formbot.regmark as rm
import formbot.barcode as bc
from PIL import Image
import json
import sys
import getopt

# Survey ID
SURVEY_ID = '1'

# API base URL
API_BASE = 'http://localhost:3000'

# Image storage base URL
IMG_BASE = 'http://localhost/~prashant/formbot_images/%s'

# Process a form image and record the results to the database
def record_form(img_id, noact=False):
  # Get the basic structural information from the survey data
  survey_url = '%s/surveys/%s' % (API_BASE, SURVEY_ID)
  try:
    print 'Getting survey information from %s' % survey_url
    survey_json = urllib2.urlopen(survey_url).read()
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    return 2
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    return 2
  print 'Processing registration mark information'
  survey = json.loads(survey_json)['survey']
  rmarks = rm.extract_data(survey['paperinfo'])
  # Right now we just pass the whole form image to the barcode reader
  #barcode_bbox = survey['paperinfo']['barcode']['bbox'];
  #
  # Get the image
  img_url = IMG_BASE % img_id
  img_data = None
  try:
    print 'Getting image from %s' % img_url
    img_data = urllib2.urlopen(img_url).read()
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    return 2
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    return 2
  #
  # Load the image of the filled-out form
  imagestring = StringIO.StringIO(img_data)
  form_img = Image.open(imagestring)
  #
  # Adjust image to fit the prototype
  # TODO: After we try fixing the image once, the registration markers are easier to find.
  # So if we try fixing again, we get closer. This is a little hacky, though. We should make
  # that part of the registration procedure.
  print 'Fixing image'
  form_img_fixed = rm.fiximage(form_img, rmarks[0], rmarks[1], rmarks[2])
  form_img_fixed = rm.fiximage(form_img_fixed, rmarks[0], rmarks[1], rmarks[2])
  #
  # Read the barcode
  print 'Reading barcode'
  form_id = bc.readbarcode(form_img_fixed)
  # XXX print("bar code data: %s" % barcodedata)
  #
  # Grab the form data
  # XXX formdataurl = "http://localhost/~prashant/formbot_data/%s.json" % barcodedata
  formdata_url = '%s/surveys/%s/forms/%s' % (API_BASE, SURVEY_ID, form_id)
  try:
    print 'Getting form data from %s' % formdata_url
    form_json = urllib2.urlopen(formdata_url).read()
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    return 2
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    return 2
  #
  print 'Processing answers'
  #
  # Read form data
  form_data = json.loads(form_json)['form']
  #
  # Iterate over each parcel on the form
  responses = []
  for parcel_piece in form_data['parcels']:
    # A form set contains the bubble sets for each parcel
    formset = Bubble.extract_data(parcel_piece, form_id)
    # Check responses to each bubble set
    answers = {}
    for bs in formset.sets:
      answers[bs.name] = bs.get_single_answer(form_img_fixed)
    responses.append({'parcel_id' : parcel_piece['parcel_id'], 'responses' : answers})
  #
  # Print the data that we got
  print 'Survey ID: %s' % SURVEY_ID
  print 'Form ID: %s' % form_id
  print json.dumps(responses)
  #
  # Record the data through the API
  if noact:
    return 0
  response_url = '%s/surveys/%s/responses' % (API_BASE, SURVEY_ID)
  try:
    print 'Posting responses to %s' % survey_url
    data = json.dumps({'responses' : responses})
    print 'JSON data:\n%s' % data
    req = urllib2.Request(response_url, headers={'Content-Type':'application/json'}, data=data)
    api_resp = urllib2.urlopen(req).read()
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    return 2
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    return 2
  print 'Response from server:'
  print api_resp

def main(argv=None):
  noact = False
  if argv is None:
    argv = sys.argv
  try:
    opts, args = getopt.getopt(argv[1:], 'n', ['noact'])
  except:
    print msg
    return 2
  # process options
  for o, a in opts:
    if o in ('-n', '--noact'):
      noact = True
  # process arguments
  img_id = args[0]
  return record_form(img_id, noact)

if __name__ == '__main__':
  sys.exit(main())

