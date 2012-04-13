FORMBOT 2000
============

The name says it all! This is the form-processing robot of the future!

Formbot 2000 processes scanned images of fill-in-the-bubble forms. It's meant to interact with the survey-api server. It will get scanned images using the API and send back the results.

To process all of the scanned forms with status `pending`:

    $ ./process_form.py

To process one scanned form:

    $ ./process_form.py ID_OF_SCAN

`readform.py` can be used to process a local image, for testing.
