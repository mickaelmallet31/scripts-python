#!/usr/bin/env python

import argparse
import re
import logging
import requests
import codecs
import sys
import time

streamWriter = codecs.lookup('utf-8')[-1]
sys.stdout = streamWriter(sys.stdout)

# https://stackoverflow.com/questions/43438323/python-requests-form-filling
save = "https://framaforms.org/plainte-suite-a-une-nuisance-aerienne-1577527816"

"""
submitted[new_1577527837019]=MALLET
submitted[new_1577527870341]=Mickael
submitted[new_1577527975503]=manou_mickael@yahoo.fr
submitted[new_1584610292989]=1
submitted[new_1577528015363][day]=19
submitted[new_1577528015363][month]=3
submitted[new_1577528015363][year]=2020
submitted[new_1577528048696][hour]=8
submitted[new_1577528048696][minute]=21
details[page_num]=1
details[page_count]=1
details[finished]=0
form_build_id=form-wmXBCNSmnDdFb1KnObkD1hLUTboM53lWoMeJcns0nRY
form_id=webform_client_form_163161
op=J'envoie ma plainte
"""

def fill_form(name, firstname, email, day, month, year, hour, minute):
    # construct the POST request
    logging.info('Request for {}:{}:{}:{}:{}:{}:{}:{} ...'.format(name, firstname, email, day, month, year, hour, minute))
    request_ok = True
    return

    with requests.session() as s: # Use a Session object.
        time.sleep(120)
        r = s.get(save)
        if r.status_code in [200]:
            form_build_id = ""
            # <input type="hidden" name="form_build_id" value="form-281y-PZJw2R36bc-E_a1DQYLfZJbt2y0tQxY2xHlz-s" />
            html_code = r.text.split('\n')
            for line in html_code:
                # Form_buil_id
                res = re.search(r'"form_build_id" value="(.+)"', line)
                if res:
                    form_build_id = res.group(1)
                    break
                                        
            if form_build_id == "":
                logging.error('Did not get find the form_build_id')
                exit(1)
            else:
                form_data = {
                    'submitted[new_1577527837019]': name,
                    'submitted[new_1577527870341]': firstname,
                    'submitted[new_1577527975503]': email,
                    'submitted[new_1584610292989]': '1',
                    'submitted[new_1577528015363][day]': day,
                    'submitted[new_1577528015363][month]': month,
                    'submitted[new_1577528015363][year]': year,
                    'submitted[new_1577528048696][hour]': hour,
                    'submitted[new_1577528048696][minute]': month,
                    'details[page_num]': '1',
                    'details[page_count]': '1',
                    'details[finished]': '0',
                    'form_build_id': form_build_id,
                    'form_id': 'webform_client_form_163161',
                    'op': "J'envoie ma plainte",
                }

            # Prepare the data
            time.sleep(30)
            res = s.post(save, data=form_data)
            logging.info(res.status_code)
            if res.status_code not in [200]:
                logging.error(res.headers)
                file_dest = open('output.html', 'w')
                file_dest.write(u'Datas of the form: {}\n\n'.format(form_data))
                file_dest.write(res.text.encode('utf8'))
                file_dest.close()
                request_ok = False

    return request_ok

#
# Main function
#
month = 3
year = '2020'

dict_names = [
    {'name': 'MALLET', 'firstname': 'Mickael', 'email': 'manou_mickael@yahoo.fr'},
    {'name': 'MALLET', 'firstname': 'Touan', 'email': 'touan.mallet@gmail.com'},
    {'name': 'MALLET', 'firstname': 'Pablo', 'email': 'mallet.pablo@gmail.com'},
]
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
parser = argparse.ArgumentParser(description="")
parser.add_argument("--input",
                    required=True,
                    action='store',
                    )
args = parser.parse_args()

for person in dict_names:
    file_src = open(args.input)
    for line in file_src:
        line = line.strip().replace('\t', ';').replace(' ', ';')
        array = line.split(';')
        day = array[1]
        (hour, minute) = array[4].split(':')
        hour = str(int(hour))
        request_ok = fill_form(person['name'], person['firstname'], person['email'], day, month, year, hour, minute)
        if not request_ok:
            request_ok = fill_form(person['name'], person['firstname'], person['email'], day, month, year, hour, minute)
    file_src.close()