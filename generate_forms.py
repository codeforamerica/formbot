#!/usr/bin/env python
from PIL import Image
import formbot.bubble as Bubble
import formbot.regmark as rm
import formbot.barcode as bc
import json
import sys
import getopt
import urllib2

API_BASE = 'http://localhost:3000'

# Get survey information from the API
def get_survey(survey_id):
  survey_url = '%s/surveys/%s' % (API_BASE, survey_id)
  data = None
  try:
    print 'Getting survey data from %s' % survey_url
    data = json.loads(urllib2.urlopen(survey_url).read())
  except urllib2.HTTPError, e:
    print 'HTTP error: %d' % e.code
    raise e
  except urllib2.URLError, e:
    print 'Network error: %s' % e.reason.args[1]
    raise e
  return data['survey']

# Post form information to the API
def post_form(survey_id, form_data):
  form_url = '%s/surveys/%s/forms' % (API_BASE, survey_id)
  try:
    data = json.dumps(form_data)
    req = urllib2.Request(form_url, headers={'Content-Type':'application/json'}, data=data)
    resp = json.loads(urllib2.urlopen(req).read())
  except urllib2.HTTPError, e:
    print 'HTTP error: %d' % e.code
    raise e
  except urllib2.URLError, e:
    print 'Network error: %s' % e.reason.args[1]
    raise e
  return resp['forms'][0]

# Get the unprocessed scans
def get_scans(sid):
  #
  # Get the image info
  scans_url = '%s/surveys/%s/scans' % (API_BASE, SURVEY_ID)
  scans = None
  try:
    print 'Getting scanned image data from %s' % scans_url
    data = json.loads(urllib2.urlopen(scans_url).read())
  except urllib2.HTTPError, e:
    print "HTTP error: %d" %e.code
    raise APIError(e)
  except urllib2.URLError, e:
    print "Network error: %s" % e.reason.args[1]
    raise APIError(e)
  return [scan for scan in data['scans'] if 'status' in scan and scan['status'] == 'pending']

def main(argv=None):
  noact = False
  if argv is None:
    argv = sys.argv
  try:
    opts, args = getopt.getopt(argv[1:], 'ni:s:o:', ['noact', 'input', 'skeleton', 'outdir'])
  except getopt.error, e:
    print e.msg
    return 2
  input_filename = None
  skeleton_file = None
  outdir = None
  # process options
  for o, a in opts:
    if o in ('-n', '--noact'):
      noact = True
    elif o in ('-i', '--input'):
      input_filename = a
    elif o in ('-s', '--skeleton'):
      skeleton_file = a
    elif o in ('-o', '--outdir'):
      outdir = a
  if outdir is None or input_filename is None or skeleton_file is None:
    print 'Bad input arguments'
    return 2
  # Load data
  input_file = file(input_filename, "r")
  data = json.load(input_file)
  #
  survey_id = data['survey']
  parcels = data['parcels']
  formsets = Bubble.extract_data(data)
  #
  survey = get_survey(survey_id)
  rmarks = rm.extract_data(survey['paperinfo'])
  #
  # Load the skeletal form
  skeleton_img = Image.open(skeleton_file)
  #
  # Draw the bubbles
  for bs in formsets.sets:
    bs.draw(skeleton_img)
  #
  # Draw the registration marks
  for mark in rmarks:
    mark.draw(skeleton_img)
  #
  # Iterate over parcels and create forms
  form_data = {"forms" : [{"parcels" : [], "type" : "paper", "mapping" : {}, "survey" : survey_id}]}
  for parcel in parcels:
    form_data["forms"][0]["parcels"] = [{"parcel_id" : parcel, "bubblesets" : data["bubblesets"]}]
    if noact:
      form_id = "TEST0001"
    else:
      # Post form data to the API, get an ID back
      ret_data = post_form(survey_id, form_data)
      form_id = ret_data["id"]
    #
    form_img = skeleton_img.copy()
    #
    # Draw the barcode
    bc.drawbarcode_json(form_img, survey['paperinfo'], form_id)
    #
    # Save the form
    outpath = "%s/%s.tif" % (outdir, form_id)
    form_img.save(outpath, "TIFF")
    print "Saved form to %s"  % outpath

if __name__ == '__main__':
  sys.exit(main())

