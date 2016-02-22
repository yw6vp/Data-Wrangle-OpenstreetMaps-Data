# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 23:16:57 2015

@author: yunxiao
"""
# MORE CLEANING WORK
import json
from collections import defaultdict
import re

class Cleaner:
    
    def __init__(self, filename):
        self.filename = filename
    
    # Get a new name to write the new dataset to.
    def get_new_name(self):
        underscore_index = self.filename.rfind('_')
        pre = self.filename[:underscore_index]
        version = 'temp'
        try:
            version = str(int(self.filename[underscore_index+1:-5]) + 1)
        except ValueError:
            print 'Check the existing filename.'
        return pre + '_' + version + '.json'
    
    # audit address tags    
    def audit_addr_tags(self):
        addr_tags = defaultdict(int)
        with open(self.filename, 'r') as fr:
            for jsonline in fr:
                line = json.loads(jsonline)
                if 'address' in line:
                    for key in line['address']:
                        addr_tags[key] += 1
        return addr_tags
    
    # Clean the unusual documents found when running clean.py    
    def clear_weirdo_postcodes(self):
        postcode_r = re.compile(r'[0-9]{5}')
        fw_name = self.get_new_name()
        fw = open(fw_name, 'w')
        with open(self.filename, 'r') as fr:
            for jsonline in fr:
                line = json.loads(jsonline)
                # I have already found the exact ids of the documents with
                # wrong post codes
                if 'created' in line and 'id' in line['created']:
                    if line['created']['id'] == '229722624':
                        line['address']['postcode'] = "23284"
                    elif line['created']['id'] == '229722628':
                        line['address']['psotcode'] = "23298"
                # Use "Richmond" instead of "Richmond City", don't write
                # "Downingtown" to the new file
                if 'address' in line:
                    if 'city' in line['address'] and line['address']['city'] == 'Richmond City':
                        line['address']['city'] = 'Richmond'
                    elif 'city' in line['address'] and line['address']['city'].find('Downingtown') != -1:
                        continue
                # Use only the first five digits of post codes
                    if 'postcode' in line['address']:
                        result = str(postcode_r.match(line['address']['postcode']).group(0))
                        if not result:
                            print 'Something wrong with cleaning the postcode: the original post code is:'
                            print line['address']['postcode']
                        else:
                            line['address']['postcode'] = result
                fw.write(json.dumps(line) + '\n')
        fw.close()
        
    # audit street names, find unexpected street names 
    def audit_street(self):
        street_types = defaultdict(set)
        street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
        # The list has been updated from running the code to include
        # all street types
        expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Alley", "Loop", "Way", "Turnpike", "Circle", "Highway", "West"]
        with open(self.filename, 'r') as fr:
            for jsonline in fr:
                line = json.loads(jsonline)
                if 'address' in line and 'street' in line['address']:
                    street_name = line['address']['street']
                    m = street_type_re.search(street_name)
                    if m:
                        street_type = m.group(0)
                        if street_type not in expected:
                            street_types[street_type].add(street_name)
        return street_types
    
    # clean street names    
    def clean_street_names(self):
        mapping = {'Pky': 'Parkway',
                   'Pkwy': 'Parkway',
                   'Rd': 'Road',
                   'street': 'Street',
                   'Ave': 'Avenue',
                   'St': 'Street',
                   'Ct': 'Court',
                   'E': 'East',
                   'S': 'South',
                   'W': 'West',
                   'N': 'North',
                   'NE': 'Northeast',
                   'SE': 'Southeast',
                   'SW': 'Southwest',
                   'NW': 'Northwest'}
        bad_names = re.compile(r'Pky\b\.?|Pkwy\b\.?|Rd\b\.?|street\b\.?|Ave\b\.?|St\b\.?|Ct\b\.?|E\b\.?|S\b\.?|W\b\.?|N\b\.?|NE\b\.?|SE\b\.?|SW\b\.?|NW\b\.?')
        
        fw_name = self.get_new_name()
        fw = open(fw_name, 'w')
        with open(self.filename, 'r') as fr:
            for jsonline in fr:
                line = json.loads(jsonline)
                if 'address' in line and 'street' in line['address']:
                    street = line['address']['street']
                    # first make sure every word in street starts with capital letter
                    street_list = street.split(' ')
                    street_list = [word.capitalize() for word in street_list]
                    street = ' '.join(street_list)
                    m = bad_names.search(street)
                    while m:
                        start = m.start(0)
                        end = m.end(0)
                        bad = m.group()
                        good = mapping[bad[:-1] if bad[-1] == '.' else bad]
                        street = street[:start] + good + street[end:]
                        m = bad_names.search(street)
                    line['address']['street'] = street
                fw.write(json.dumps(line) + '\n')
        fw.close()        
        
    # audit the keys that are supposed to have well expected values
    def audit_expected(self):
        expected_types = ["node", "way"]
        types = defaultdict(int)
        with open(self.filename, 'r') as fr:
            for jsonline in fr:
                line = json.loads(jsonline)
                # Everyone gets a type
                if "type" not in line:
                    print 'doesn\'t have type:'
                    print line
                # type has to be either node or way    
                elif line['type'] not in expected_types:
                    types[line['type']] += 1
                # pos has two nubmers(float or int)
                if 'pos' in line:
                    pos_valid = [type(num) in [type(1.), type(0)] for num in line['pos']]
                    if not (len(pos_valid) == 2 and pos_valid[0] and pos_valid[1]):
                        print 'invalid pos:'
                        print line
                # see if everyone has "created"
                if not line['created']:
                    print 'created is empty:'
                    print line
        print types
                        
osm_cleaner = Cleaner('richmond_virginia_0.json')
#print osm_cleaner.get_new_name()
#addr_tags = osm_cleaner.audit_addr_tags()
#print addr_tags
osm_cleaner.clear_weirdo_postcodes()
osm_cleaner = Cleaner('richmond_virginia_1.json')
osm_cleaner.clean_street_names()
osm_cleaner = Cleaner('richmond_virginia_2.json')
street_types = osm_cleaner.audit_street()
print "strange street types:"
print street_types
osm_cleaner.audit_expected()
