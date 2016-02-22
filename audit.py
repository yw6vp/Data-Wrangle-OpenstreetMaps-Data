import xml.etree.ElementTree as ET
from collections import defaultdict
import pprint
# audit the tags used in the dataset
def count_tags(filename):
    tags = defaultdict(int)
    for event, elem in ET.iterparse(filename):
        tags[elem.tag] += 1
    return tags
# audit the existing types, this is added after cleaning the data as I 
# described in the report    
def audit_type(filename):
    types = set()
    for _, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for i, subtag in enumerate(elem.iter()):
                if i == 0: continue
                if 'k' not in subtag.attrib: continue
                k = subtag.attrib['k']
                v = subtag.attrib['v']
                if k == "type":
                    print elem.tag, v
                    types.add(v)
    return types
# tags = count_tags("richmond_virginia.osm")
# pprint.pprint(tags)
types = audit_type("richmond_virginia.osm")
print types

