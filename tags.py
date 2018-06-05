import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import json
"""
Your task is to explore the data a bit more.
Before you process the data and add it into MongoDB, you should
check the "k" value for each "<tag>" and see if they can be valid keys in MongoDB,
as well as see if there are any other potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data model
and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with problematic characters.
Please complete the function 'key_type'.
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#\$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        if re.search(lower, element.attrib['k']):
            keys['lower'] += 1
        elif re.search(lower_colon, element.attrib['k']):
            keys['lower_colon'] += 1
        elif re.search(problemchars, element.attrib['k']):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
                
    return keys
 

   
def key_value(element, data):
    frequent_list = ['highway', 'building', 'name', 'tiger:county', 'tiger:name_base', 
                     'tiger:cfcc', 'tiger:name_type', 'tiger:cfcc', 'tiger:name_type', 
                     'tiger:zip_left', 'tiger:zip_right', 'tiger:reviewed', 'tiger:tlid', 
                     'tiger:source', 'tiger:separated', 'source',
                     'phone', 'contact:phone', 'addr:postcode']
                     
    frequent_list = ['tiger:zip_left', 'tiger:zip_right',]

    key = element.attrib['k']
    value = element.attrib['v']
    
    if key in frequent_list and len(data[key]) < 100:
        data[key].add(value)



def process_map(filename):
    data = defaultdict(set)
    for _, element in ET.iterparse(filename):
        if element.tag == 'node' or 'way':
            for tag in element.iter("tag"):
                key_value(tag, data)

    return data



def test():
    # You can use another testfile 'map.osm' to look at your solution
    # Note that the assertions will be incorrect then.
    data = dict(process_map('san-jose_california.osm'))
    for k in data:
        data[k] = list(data[k])
#    json.dump(data, open('san-jose_california_tag_data.json', 'w'))
    pprint.pprint(data)



if __name__ == "__main__":
    test()