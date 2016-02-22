# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 23:45:14 2015

@author: yunxiao
"""
import json
from pymongo import MongoClient

client = MongoClient("localhost:27017")
db = client.osm

num = db.richmond.find().count()
print "num:", num

with open("richmond_virginia_2.json", 'r') as f:
    for jsonline in f:
        line = json.loads(jsonline)
        db.richmond.insert(line)

num = db.richmond.find().count()
print "num:", num
print db.richmond.find_one()