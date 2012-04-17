FORMBOT 2000
============

The name says it all! This is the form-processing robot of the future!

Formbot 2000 processes scanned images of fill-in-the-bubble forms. It's meant to interact with the survey-api server. It will get scanned images using the API and send back the results.

Set the base URL for the API with the `SURVEY_API_BASE` environment variable. For example:

    export SURVEY_API_BASE="http://localhost:3000"

To process all of the scanned forms with status `pending`:

    $ ./process_form.py -s SURVEY_ID

To process one scanned form:

    $ ./process_form.py -s SURVEY_ID ID_OF_SCAN

`readform.py` can be used to process a local image, for testing.

To generate forms for a set of parcels, use `generate_forms.py`:

    $ ./generate_forms.py -i INPUT.json -s SKELETON_FORM -o OUTPUT_DIR

where `OUTPUT_DIR` is where the form images should go, `SKELETON_FORM` is the template image (150 dpi), and `INPUT.json` specifies the details for the forms as in the following example.

    {
      "survey" : "1",
      "bubblesets" :
        [ {"bubbles" :
            [ {"center" : [600, 356], "radius" : 15},
              {"center" : [600, 394], "radius" : 15},
              {"center" : [600, 432], "radius" : 15}
            ],
            "name" : "Q0"
          },
          {"bubbles" :
            [ {"center" : [347, 694], "radius" : 15},
              {"center" : [384, 694], "radius" : 15},
              {"center" : [422, 694], "radius" : 15},
              {"center" : [459, 694], "radius" : 15},
              {"center" : [497, 694], "radius" : 15},
              {"center" : [534, 694], "radius" : 15},
              {"center" : [572, 694], "radius" : 15},
              {"center" : [609, 694], "radius" : 15},
              {"center" : [647, 694], "radius" : 15},
              {"center" : [684, 694], "radius" : 15}
            ],
            "name" : "Q0"
          }
        ],
      "parcels" : ["1", "2", "3", "4", "5", "6"]
    }

