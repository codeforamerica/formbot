import json
import urllib2
import os

class API(object):
  def __init__(self, base_url):
    self.base_url = base_url

  # Get survey information from the API
  def get_survey(self, survey_id):
    survey_url = '%s/surveys/%s' % (self.base_url, survey_id)
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
  def post_form(self, survey_id, form_data):
    form_url = '%s/surveys/%s/forms' % (self.base_url, survey_id)
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
  def get_pending_scans(self, sid):
    #
    # Get the image info
    scans_url = '%s/surveys/%s/scans' % (self.base_url, sid)
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
