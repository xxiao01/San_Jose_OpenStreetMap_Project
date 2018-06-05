#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import phonenumbers
from collections import defaultdict

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
tow_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$') 
address_start = re.compile(r'^addr:')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

ZIPCODE_TAGS = ['tiger:zip', 'tiger:zip_left', 'tiger:zip_left_1', 'tiger:zip_left_2',
    'tiger:zip_left_3', 'tiger:zip_left_4', 'tiger:zip_left_5', 'tiger:zip_right', 'tiger:zip_right_1',
    'tiger:zip_right_2', 'tiger:zip_right_3', 'tiger:zip_right_4']
    
PHONE_TAGS = ['phone', 'contact:phone']

# clean street 
St_mapping = { "St": "Street",
            "Blvd": "Street",
            "Ave": "Avenue",
            "ave": "Avenue",
            "Cir": "Road",
            "Rd": "Road",
            "Ct": "Court",
            "Dr": "Drive",
            "Hwy": "Highway",
            "Ln": "Lane",
            "Sq": "Square",            
            }
            
confuse_list = ['address', 'type']



def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :

        zipcodes = set()        
        node['type'] = element.tag
        node['created'] = {}
        node['pos'] = []
        if 'lat' in element.attrib: node['pos'].append(float(element.attrib['lat']))
        if 'lon' in element.attrib: node['pos'].append(float(element.attrib['lon']))
        
        for i in element.attrib:
            if i in CREATED: node['created'][i] = element.attrib[i]
            elif i == 'lon' or i == 'lat': continue
            else: node[i] = element.attrib[i]
                
        for tag in element.iter("tag"):
            key = tag.attrib['k']
            val = tag.attrib['v']
            
            if re.search(problemchars, key) or re.search(tow_colon, key): continue
            
            # don't use direct address tag, which is quite few, only about 1 in 'node' and 3 in 'way'
            if key in confuse_list: continue
    
            if re.search(address_start, key):
                if 'address' not in node:
                    node['address'] = {}
                    
                # update street name
                if key == "addr:street":
                    m = street_type_re.search(val)
                    if m:
                        street_type = m.group()
                        if street_type in St_mapping:
                            node['address']['street'] = val.replace(street_type, St_mapping[street_type])
                        else:
                            node['address']['street'] = val

                            
                # update postal code in node
                elif key == "addr:postcode":
                    node['address']['postcode'] = process_postcode(val)

                else:
                    node['address'][key.split(':')[1]] = val

                    
            # extract any zip codes in way
            elif key in ZIPCODE_TAGS:
                for zipcode in process_zipcode(val):
                    zipcodes.add(zipcode)
                    
            # update phone number in node
            elif key in PHONE_TAGS:
                node['phone'] = process_phone(val)
             
            else:
                node[key] = val
                    
            
        for nd in element.iter('nd'):
            if "node_refs" not in node:
                node["node_refs"] = []
            node["node_refs"].append(nd.attrib['ref'])         
        
        # add zipcode for way        
        if len(zipcodes) > 0:        
            node['zipcodes'] = list(zipcodes)    
            
        return node
    else:
        return None
        

# fix and standardize phone numbers using phonenumbers module and list comprehensions
# however, the phone format like '+ 408 980 6400' need to be fixed before useing phonenumbers module
def process_phone(string):
    if re.match(r'^\+ \d{3} \d{3} \d{4}$', string):
        string = string[1:]
        
    phone_number_matches = [m.number for m in phonenumbers.PhoneNumberMatcher(string, "US")]
    string = ';'.join([phonenumbers.format_number(phone_number_match,
        phonenumbers.PhoneNumberFormat.NATIONAL)
        for phone_number_match in phone_number_matches])
                
    return string


def process_postcode(postcode):
    standard = re.compile(r'^\d{5}$')
    standard_full = re.compile(r'^\d{5}-\d{4}$')
    state_standard = re.compile(r'^CA \d{5}$')
    state_standard_full = re.compile(r'^CA \d{5}-\d{4}$')
    
    if re.search(standard, postcode):
        return postcode
    elif re.search(standard_full, postcode):
        return postcode.split('-')[0]
    elif re.search(state_standard, postcode):
        return postcode.split(' ')[1]
    elif re.search(state_standard_full, postcode):
        return postcode.split(' ')[1].split('-')[0]
    else:
        return postcode
        

def process_zipcode(string):
    result = []
    groups = [group.strip() for group in string.split(';')]
    for group in groups:
        if re.match(r'\d{5}\:\d{5}', group):
            group_range = map(int, group.split(':'))
            result += list(map(str, range(group_range[0], group_range[1]+1)))
        elif re.match(r'\d{5}', group):
            result.append(group)
    return result
    

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.


    data = process_map('san-jose_california.osm', False)
    pprint.pprint(data[500])
    
#    with open('san-jose_california.osm.json') as data_file:    
#        data = json.load(data_file)
#        
#    print 'finish loading file'
    
    d = defaultdict(set)
    
    for point in data:
        for k in point:
            if k == 'zipcodes' and len(d[k]) < 100:
                for s in point[k]:
                    d[k].add(s)
            if k == 'phone' and len(d[k]) < 100:
                d[k].add(point.get(k))
            if k == 'address' and point[k].get('postcode') and len(d['postcode']) < 100:
                d['postcode'].add(point[k].get('postcode'))
                
        if len(d['zipcodes']) > 99 and len(d['phone']) > 99 and len(d['postcode']) > 99:
            break
                
    data = dict(d)
    for k in data:
        data[k] = list(data[k])
    pprint.pprint(data)

    
#    correct_first_elem = {
#        "id": "261114295", 
#        "visible": "true", 
#        "type": "node", 
#        "pos": [41.9730791, -87.6866303], 
#        "created": {
#            "changeset": "11129782", 
#            "user": "bbmiller", 
#            "version": "7", 
#            "uid": "451048", 
#            "timestamp": "2012-03-28T18:31:23Z"
#        }
#    }
#    assert data[0] == correct_first_elem
#    assert data[-1]["address"] == {
#                                    "street": "West Lexington St.", 
#                                    "housenumber": "1412"
#                                      }
#    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
#                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()


#    print process_postcode('95037')
#    print process_postcode('95037-4209')
#    print process_postcode('CA 94035')
#    print process_postcode('CA 94088-3453')

#    print process_phone('+1 408-782-8201')
#    print process_phone('+1 (408) 376-3516')
#    print process_phone('+1 408 739 7717')
#    print process_phone('+ 408 980 6400')
#    print process_phone('4084507990')
#    print process_phone('+1.408.559.6900')
#    print process_phone('(408) 277-4625')
#    print process_phone(u'+1 408-500-3000 \u200e')