# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 22:31:52 2015

@author: yunxiao
"""
#==============================================================================
# ******THIS COMMENT SECITON IS ONLY HERE TO REMIND MYSELF OF THE FUNCTIONALITY 
# OF THIS PROGRAM*******
# This code contains code from "tag_keys.py" and "addr.py". But functions from 
# those files are included as 
# methods for the class. This is a OO approach to the problem:D
# 
# This code also has cleaning method that do some simple cleaning and write it 
# to json file.
# NOTE: weirdos are not dealt with yet! This code only has some generic 
# cleaning capability.
# ******THIS COMMENT SECITON IS ONLY HERE TO REMIND MYSELF OF THE FUNCTIONALITY 
# OF THIS PROGRAM*******
#==============================================================================
from collections import defaultdict
import xml.etree.ElementTree as ET
import re
import json

class FileHandler:
    lower = re.compile(r'^([a-z]|_)*$')
    lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
    
    CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
    
    def __init__(self, f):
        self.filename = f
    
    # audit the address tags see if there's anything unusual
    def audit_addr(self):
        filename = self.filename
        city = defaultdict(int)
        postcode = defaultdict(int)
        state = defaultdict(int)
        country = defaultdict(int)
        for event, elem in ET.iterparse(filename, events=("start",)):
            if elem.tag == 'node' or elem.tag == 'way':
                for tag in elem.iter('tag'):
                    k = tag.attrib['k']
                    v = tag.attrib['v']
                    if k == 'addr:city':
                        city[v] += 1
                    elif k == 'addr:postcode':
                        postcode[v] += 1
                    elif k == 'addr:state':
                        state[v] += 1
                    elif k == 'addr:country':
                        country[v] += 1
        return (city, postcode, state, country)
    
    # After running audit_addr, I found some inconsistencies in postcodes
    # and a city in Pa rather than Va.
    # This code was run to look at the unusual documents in the dataset.
    def find_weirdo(self):
        filename = self.filename
        for event, elem in ET.iterparse(filename, events=('start',)):
            if elem.tag == 'node' or elem.tag == 'way':
                for tag in elem.iter('tag'):
                    k = tag.attrib['k']
                    v = tag.attrib['v']
                    if k == 'addr:postcode' and v[:2] != '23':
                        print 'Document with strange postcode:'
                        print elem.tag, elem.attrib
                        for i, t in enumerate(elem.iter()):
                            if i == 0: continue
                            print '\t', t.tag, t.attrib
                    elif k == 'addr:state' and v == 'Pa':
                        print 'Document with strange state:'
                        print elem.tag, elem.attrib
                        for i, t in enumerate(elem.iter()):
                            if i == 0: continue
                            print "\t", t.tag, t.attrib
                            
    # Just to audit what keys tags within nodes and ways have in attributes.                    
    def tag_keys(self):
        filename = self.filename
        node_tag_keys = defaultdict(int)
        addr_tags = defaultdict(int)
        way_tag_keys = defaultdict(int)
        for event, elem in ET.iterparse(filename, events=("start",)):
            if elem.tag == "node" or elem.tag == 'way':
                for tag in elem.iter("tag"):
                    if elem.tag == 'node':
                        node_tag_keys[tag.attrib['k']] += 1                    
                    else:
                        way_tag_keys[tag.attrib['k']] += 1
                    if tag.attrib['k'].find('addr:') != -1:
                        addr_tags[tag.attrib['k']] += 1
        return (node_tag_keys, way_tag_keys, addr_tags)
    
    # Pretty much the same shape_element from exercise in lesson 6
    # to put dataset in json for more cleaing.
    def shape_element(self, element):
        node = {}
        CREATED = self.CREATED
        problemchars = self.problemchars
        lower_colon = self.lower_colon
        lower = self.lower
        if element.tag == "node" or element.tag == "way":
            node['type'] = element.tag
            node['created'] = {}
            if 'lat' in element.attrib and 'lon' in element.attrib:
                node['pos'] = [0, 0]
            for attrib, value in element.attrib.iteritems():
                if attrib in CREATED:
                    node['created'][attrib] = value
                elif attrib == 'lat':
                    node['pos'][0] = float(value)
                elif attrib == 'lon':
                    node['pos'][1] = float(value)
                else:
                    node[attrib] = value
            for i, subtag in enumerate(element.iter()):
                if i == 0: continue
                if element.tag == 'way' and subtag.tag == 'nd':
                    node['node_refs'] = node.get('node_refs', [])
                    node['node_refs'].append(subtag.attrib['ref'])
                    continue  
                k = subtag.attrib['k']
                v = subtag.attrib['v']
                if problemchars.search(k):
                    continue
                if lower_colon.search(k):
                    if k.find('addr:') == 0:
                        node['address'] = node.get('address', {})
                        node['address'][k[5:]] = v
                    else:
                        node[k] = v
                elif lower.search(k):
                    if k == "type":
                        node[element.tag + '_type'] = v
                    else:
                        node[k] = v
            return node
        else:
            return None
            
    def process_map(self):
        # You do not need to change this file
        file_out = "{0}_{1}.json".format(self.filename[:-4], "0")
        with open(file_out, "w") as fo:
            for _, element in ET.iterparse(self.filename, events=("start",)):
                el = self.shape_element(element)
                if el:
                    fo.write(json.dumps(el) + "\n")
 
# The other methods were already run for auditing before entering the dataset 
# into a json file with process_map().       
osm = FileHandler("richmond_virginia.osm")
osm.process_map()






