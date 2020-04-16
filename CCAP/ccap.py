#!/usr/bin/env python

import argparse
import re
import logging
import requests
import codecs
import sys
import time

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

def sleep(duration):
    for i in range(duration, 0, -1):
        sys.stdout.write('\r{:02d} secondes'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    print('')
    
def fill_form(name, firstname, email, day, month, year, hour, minute):
    # construct the POST request
    logging.info('Request for {}:{}:{}:{}:{}:{}:{}:{} ...'.format(name, firstname, email, day, month, year, hour, minute))
    request_ok = True
    
    with requests.session() as s: # Use a Session object.
        sleep(30)
        logging.info('Get the form_build_id')
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
            sleep(30)
            logging.info('Send the filled form  ')
            res = s.post(save, data=form_data)
            logging.info(res.status_code)
            if res.status_code not in [200]:
                logging.error(res.headers)
                file_dest = open('output.html', 'w')
                file_dest.write(u'Datas of the form: {}\n\n'.format(form_data))
                file_dest.write(res.text.encode('utf8'))
                file_dest.close()
                request_ok = False
    print('\n')
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
    {'name': 'MIKANDA', 'firstname': 'Marie-Louise', 'email': 'mikanda_marielouise@yahoo.fr'},
]
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
parser = argparse.ArgumentParser(description="")
parser.add_argument("--input",
                    required=True,
                    action='store',
                    )
args = parser.parse_args()

file_src = open(args.input)
for line in file_src:
    for person in dict_names:

        line = line.strip().replace('\t', ';').replace(' ', ';')
        array = line.split(';')
        (day, month, year) = array[0].split('/')
        (hour, minute) = array[1].split(':')
        hour = str(int(hour))
        day = str(int(day))
        month = str(int(month))
        counter = 0
        while counter < 10:
            request_ok = fill_form(person['name'], person['firstname'], person['email'], day, month, year, hour, minute)
            if request_ok:
                break
            counter += 1        
file_src.close()