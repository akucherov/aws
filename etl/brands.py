import os
import json
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

GTINS = "http://localhost:5984/docs/"
STAGE = "prod"
cache = {}

def fileProcessing(filename):
    with open(filename, "r+") as f: 
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        for line in lines:
            new_line = line
            event = json.loads(line)
            if not 'brand' in event and 'stage' in event and 'participant' in event:
                if 'gtin' in event and event['stage'] == STAGE and not event['participant'] is None:
                    gtin = event['gtin']
                    if gtin in cache:
                        brand = cache[gtin]
                    else:
                        brand = None
                        req = Request(GTINS+gtin)
                        try:
                            response = urlopen(req)
                        except HTTPError as e:
                            print('The server couldn\'t fulfill the request for '+gtin)
                            print('Error code: ', e.code)
                        except URLError as e:
                            print('We failed to reach a server.')
                            print('Reason: ', e.reason)
                        else:
                            data = json.loads(response.read().decode())
                            if 'brand_id' in data:
                                brand = data['brand_id']
                                cache[gtin] = brand
                            else:
                                cache[gtin] = None
                    if not brand is None:
                        event['brand'] = brand
                        new_line = json.dumps(event, separators=(',',':')) + '\n'
            f.write(new_line)

for dirpath, dirs, files in os.walk(os.getcwd()):
    for filename in files:
        path = os.path.join(dirpath, filename)
        print("Processing " + path)
        fileProcessing(path)
        print("Done")