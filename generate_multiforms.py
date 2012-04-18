#!/usr/bin/env python

# Generate forms that cover multiple parcels

from PIL import Image
import formbot.bubble as Bubble
import formbot.regmark as rm
import formbot.barcode as bc
import formbot.surveyapi as survey_api
import json
import sys
import getopt
import urllib2
import os

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

  # Set up API access
  api = survey_api.API(os.getenv('SURVEY_API_BASE', 'http://localhost:3000'))

  # Load data
  input_file = file(input_filename, "r")
  data = json.load(input_file)
  #
  survey_id = data['template']['survey']
  parcelsets = data['parcelsets']

  # Get the global survey information
  survey = api.get_survey(survey_id)

  # Interpret the registration mark information
  paperinfo = survey['paperinfo']
  rmarks = rm.extract_data(paperinfo)

  # Load the skeletal form
  skeleton_img = Image.open(skeleton_file)

  # Interpret the bubble information
  form_bubble_sets = []
  for parcel_info in data['template']['parcels']:
    form_bubble_sets.append(Bubble.extract_data(parcel_info))

  # Draw the bubbles
  for parcel_bubble_set in form_bubble_sets:
    for bs in parcel_bubble_set.sets:
      bs.draw(skeleton_img)

  # Draw the registration marks
  for mark in rmarks:
    mark.draw(skeleton_img)

  # The template doesn't specify the type and mapping fields, so we need to add
  # them.
  form_data = data['template']
  form_data['type'] = 'paper'
  form_data['mapping'] = {}

  # Iterate over parcel sets and create forms
  for parcelset in parcelsets:
    for i in range(len(parcelset)):
      form_data['parcels'][i]['parcel_id'] = parcelset[i]
    if noact:
      form_id = 'TEST0001'
    else:
      # Post form data to the API get an ID back
      ret_data = api.post_form(survey_id, {'forms' : [form_data]})
      form_id = ret_data['id']

    form_img = skeleton_img.copy()

    # Draw the barcode
    bc.drawbarcode_json(form_img, paperinfo, form_id)

    # Save the form
    # TODO: Use PNG or JPEG instead of TIFF
    outpath = '%s/%s.tif' % (outdir, form_id)
    form_img.save(outpath, 'TIFF')
    print 'Saved form to %s' % outpath


if __name__ == '__main__':
  sys.exit(main())

