#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: jmespadero
'''
import unittest

import json
import sys
from pprint import pprint
from indyva.dataset.schemas import TableSchema, AttributeSchema
from indyva.dataset import RSC_DIR
import pandas as pd
import exceptions

class Test(unittest.TestCase):

    def callback(self, topic, msg):
        print topic, msg
        self.callback_executed = True

    def testInferFromData(self):
		#Default argument 
		filename = RSC_DIR+"/spines.json"
		#if len(sys.argv) >= 2:
		#    filename = sys.argv[1]

		#Read file as independent json lines
		print "Parsing file: ", filename
		data = []
		with open(filename) as f:
		    data = json.load(f)
		    #for line in f:    data.append(json.loads(line))
		    
		#Print some measures of the data
		print "Num Lines =", len(data), "Num Attribs = ", len(data[0])

		#Create a empty tableSchema
                with self.assertRaises(ValueError):
                    tableSchema = TableSchema.infer_from_data(data)

                df = pd.DataFrame(data)
                df['uid'] = df.dendrite_id + '-' + df.spine_id
                tableSchema = TableSchema.infer_from_data(df)
		self.assertIsInstance(tableSchema, TableSchema)
				
		print "\nResult of TableSchema.infer_from_data(data):"
		print "Identified", len(tableSchema._schema['attributes']), "attributes"
		print tableSchema._schema['attributes'].keys()
		
		#Check some values
		self.assertEqual(len(tableSchema._schema['attributes']), df.columns.size)
		self.assertIsInstance(tableSchema._schema['attributes']['angle'], AttributeSchema)
		self.assertIsInstance(tableSchema._schema['attributes']['angle']._schema['key'], bool)
		self.assertEqual(tableSchema._schema['attributes']['angle']._schema['key'], False)
		#self.assertEqual(tableSchema._schema['attributes']['angle']._schema['allEqual'], False)
		self.assertEqual(tableSchema._schema['attributes']['raw_pos']._schema['shape'], pd.np.array([0,0,0]).shape)
				
		#pprint(tableSchema)
		#Print table line by line, which is prettier than using pprint
		for name in tableSchema._schema['attributes']:
		    print name, " -> ", tableSchema._schema['attributes'][name]
		
if __name__ == "__main__":
    unittest.main()
