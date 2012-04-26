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
import os
import time

# API base URL
API_BASE = os.getenv('SURVEY_API_BASE', 'http://localhost:3000')

# The amount of time the server should wait before responding that there are no
# images to be processed
COMET_DELAY = 10000

class APIError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

# Get the unprocessed scans
def get_scans(sid):
  #
  # Get the image info
  scans_url = '%s/surveys/%s/scans?status=pending' % (API_BASE, sid)
  scans = None
  try:
    print 'Getting pending scanned image data from %s' % scans_url
    data = json.loads(urllib2.urlopen(scans_url).read())
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    raise APIError(e)
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    raise APIError(e)
  return data['scans']

# Get all of the surveys
def get_surveys():
  url = '%s/surveys' % API_BASE
  ids = None
  try:
    print 'Getting surveys from %s' % url
    data = json.loads(urllib2.urlopen(url).read())
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    raise APIError(e)
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    raise APIError(e)
  return data['surveys']

# Get a survey
def get_survey(sid):
  url = '%s/surveys/%s' % (API_BASE, sid)
  try:
    print 'Getting survey %s from url %s' % (sid, url)
    data = json.loads(urllib2.urlopen(url).read())
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    raise APIError(e)
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    raise APIError(e)
  return data['survey']

# Update the status of a scan.
def update_status(sid, img_id, status):
  img_info_url = '%s/surveys/%s/scans/%s' % (API_BASE, sid, img_id)
  try:
    print 'Updating scan status: %s' % img_info_url
    data = json.dumps({'scan' : {'status': status}})
    print 'JSON data:\n%s' % data
    headers = { 'Content-Type' : 'application/json', 'X-HTTP-Method-Override' : 'PUT' }
    req = urllib2.Request(img_info_url, headers=headers, data=data)
    api_resp = urllib2.urlopen(req).read()
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    raise APIError(e)
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    raise APIError(e)
  print 'Response from server:'
  print api_resp
  return api_resp

# Get the actual image
def get_image(img_url):
  img_data = None
  try:
    print 'Getting image from %s' % img_url
    img_data = urllib2.urlopen(img_url).read()
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    raise APIError(e)
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    raise APIError(e)
  return img_data

# Check if there are images to process
def check_work():
  url = '%s/work' % API_BASE
  work = False
  try:
    headers = { 'X-Comet-Timeout' : COMET_DELAY }
    req = urllib2.Request(url, headers=headers)
    data = json.loads(urllib2.urlopen(req).read())
    work = data['haswork']
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    raise APIError(e)
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    raise APIError(e)
  return work

# Process a form image and record the results to the database
def record_form(survey_id, img_id, noact=False, paperinfo=None):
  #
  # Get the basic structural information from the survey data
  # TODO: refactor so that we don't do this for every iteration
  survey_url = '%s/surveys/%s' % (API_BASE, survey_id)
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
  #
  # Right now we just pass the whole form image to the barcode reader, so we
  # don't need the barcode bounding box
  #barcode_bbox = survey['paperinfo']['barcode']['bbox'];
  #
  # Get the image info
  img_info_url = '%s/surveys/%s/scans/%s' % (API_BASE, survey_id, img_id)
  img_info = None
  try:
    print 'Getting image info from %s' % img_info_url
    img_info = json.loads(urllib2.urlopen(img_info_url).read())
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    return 2
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    return 2
  #
  # Confirm that there is work to be done
  status = img_info['scan']['status']
  if status == "complete":
    print "WARNING: We already processed this image"
    return
  if status == "working":
    print "DOUBLE WARNING: Someone is currently processing this image. Don't run two processing tasks at the same time until the API supports it."
    return
  print "Got status %s. It's OK to proceed." % status
  #
  # Get the actual image
  try:
    img_data = get_image(img_info['scan']['url'])
  except APIError, e:
    return 2
  #
  # Update status to 'working'
  if not noact:
    try:
      update_status(survey_id, img_id, 'working')
    except APIError, e:
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
  # Crop out an area around the barcode, to make life easier on the decoder.
  # XXX
  print 'paperinfo: %s' % json.dumps(paperinfo)
  bc_bbox = paperinfo['barcode']['bbox']
  dpi = paperinfo['dpi']
  paper_size = (int(8.5*dpi), int(11.0*dpi))
  crop_bbox = (max(bc_bbox[0] - 50, 0), max(bc_bbox[1] - 50, 0),
               min(bc_bbox[2] + 50, paper_size[0]), min(bc_bbox[3] + 50, paper_size[1]))
  # XXX
  form_img_fixed.save('/tmp/debug_fixed.tif', 'TIFF')
  #form_id = bc.readbarcode(form_img_fixed.crop(crop_bbox))
  # XXX
  form_id = bc.readbarcode(form_img_fixed)
  #
  # Grab the form data
  formdata_url = '%s/surveys/%s/forms/%s' % (API_BASE, survey_id, form_id)
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
  print 'Survey ID: %s' % survey_id
  print 'Form ID: %s' % form_id
  print json.dumps(responses)
  #
  # Record the data through the API
  if noact:
    return
  response_url = '%s/surveys/%s/responses' % (API_BASE, survey_id)
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
  #
  # Update status to 'complete'
  try:
    update_status(survey_id, img_id, 'complete')
  except APIError, e:
    return 2

def main(argv=None):
  noact = False
  survey_id = None
  if argv is None:
    argv = sys.argv

  try:
    opts, args = getopt.getopt(argv[1:], 'ns:', ['noact', 'survey'])
  except getopt.error, e:
    print e.msg
    return 2

  # process options
  for o, a in opts:
    if o in ('-n', '--noact'):
      noact = True
    elif o in ('-s', '--survey'):
      survey_id = a

  # If we got a survey ID and a scan ID on the command line, process that
  # image.
  if len(args) > 0:
    # process arguments
    img_id = args[0]
    return record_form(survey_id, img_id, noact)
  elif survey_id is not None:
    # If we got a survey ID, get the pending images for that survey and process
    # each of them.
    survey = get_survey(survey_id)
    scans = get_scans(survey_id)
    for scan in scans:
      ret = record_form(survey_id, scan['id'], noact, paperinfo=survey['paperinfo'])
      if (ret is not None) and (ret != 0):
        return ret
  else:
    ret = 0
    # Loop over surveys. Process all of the pending scans.
    surveys = get_surveys()
    for survey in surveys:
      survey_id = survey['id']
      print
      print 'Processing survey %s' % survey_id
      print
      scans = get_scans(survey_id)
      for scan in scans:
        tmp_ret = record_form(survey_id, scan['id'], noact, paperinfo=survey['paperinfo'])
        if tmp_ret is not None and tmp_ret != 0:
          ret = tmp_ret
    return ret

  # The following code lets us wait until work is available, so that the tool
  # can run as a worker process. But running workers is problematic right now,
  # so one-off use is more appropriate.
  if False:
    # Keep looping. check_work will wait on the server response, so this will
    # not be a super tight loop.
    while True:
      # Check if there's work
      print 'Checking for work every %s ms' % COMET_DELAY
      work = False
      try:
        work = check_work()
      except APIError, e:
        # The API is not ready. Wait a little before trying again.
        print 'API Error: %s' % e
        time.sleep(5)
      if work:
        # Iterate over all of the surveys.
        surveys = get_surveys()
        for survey in surveys:
          survey_id = survey['id']
          print
          print 'Processing survey %s' % survey_id
          print
          scans = get_scans(survey_id)
          for scan in scans:
            ret = record_form(survey_id, scan['id'], noact, paperinfo=survey['paperinfo'])
            if (ret is not None) and (ret != 0):
              return ret

if __name__ == '__main__':
  sys.exit(main())

