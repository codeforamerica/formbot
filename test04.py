from PIL import Image
import formbot.bubble as Bubble
import formbot.regmark as rm
import formbot.barcode as barcode
import json
import subprocess
import glob
import os

rm.DEBUG = True

FORMDATA = "formdata02.json"
INFILE = "form02.tif"
#QRFILE = "qrcodetest01.png"

form = Image.open(INFILE)
#tmp = Image.open(QRFILE)
#form.paste(tmp, (975,50))
barcode.drawbarcode(form, FORMDATA)
data = barcode.readbarcode(form)

print "Decoded data: %s" % data

# #decode = 'java', '-classpath', ':'.join(glob.glob(os.path.dirname(__file__) + '/lib/*.jar')), 'qrdecode'
# decode = 'java', '-classpath', ':'.join(glob.glob('lib/*.jar')), 'qrdecode'
# decode = subprocess.Popen(decode, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
# 
# form.save(decode.stdin, 'PNG')
# decode.stdin.close()
# decode.wait()
# 
# decoded = decode.stdout.read().strip()
# print decoded

