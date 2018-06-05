"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the 
tag name as the key and number of times this tag can be encountered in 
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict
import operator


def count_tags(filename):
    d = defaultdict(int)
    keys = defaultdict(int)
    osm_file = open(filename, 'r')
    for event, elem in ET.iterparse(osm_file, events = ('start',)):
        d[elem.tag] += 1
        if elem.tag == 'way':
            for tag in elem.iter("tag"):
                keys[tag.attrib['k']] += 1
            
    # produces a sorted-by-decreasing list of tag key-count pairs
    keys = sorted(keys.items(), key=operator.itemgetter(1))[::-1]
                    
    return d, keys


def test():
    
    tags, keys = count_tags('san-jose_california.osm')
    pprint.pprint(tags)
    pprint.pprint(keys)

    

if __name__ == "__main__":
    test()