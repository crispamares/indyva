# -*- coding: utf-8 -*-
'''
Created on 06/09/2013

@author: jmorales
'''

import pymongo 
from dataset.table import Table
from dataset.schemas import TableSchema, AttributeSchema

def create_schema():
    # TODO: MultiKey is not yet implemented
    #schema = TableSchema({},index=['spine_id', 'dendrite_id'])
    schema = TableSchema({},index='spine_id')
    schema.add_attribute('spine_id', 
                         dict(attribute_type= 'CATEGORICAL',
                              key=True))
    schema.add_attribute('dendrite_id','CATEGORICAL')
    schema.add_attribute('size', 'QUANTITATIVE')
    schema.add_attribute('length', 'QUANTITATIVE')
    schema.add_attribute('angle', 'QUANTITATIVE')
    VECTOR3D = AttributeSchema('QUANTITATIVE', shape = (3,) )
    schema.add_attribute('raw_pos', VECTOR3D)
    schema.add_attribute('straight_pos', VECTOR3D)
    schema.add_attribute('unroll_pos', VECTOR3D)
    schema.add_attribute('joint_raw_pos', VECTOR3D)
    schema.add_attribute('joint_straight_pos', VECTOR3D)
    schema.add_attribute('joint_unroll_pos', VECTOR3D)
    schema.add_attribute('section', 'ORDINAL')

    return schema

def create_table():
    client = pymongo.MongoClient()
    db = client['spinesIP']
    table = Table(name='spines', schema=create_schema())
    for d in db['spines'].find({},{'_id':False}):
        d['spine_id'] = '{0}-{1}'.format(d['dendrite_id'], d['spine_id']) 
        table.insert(d)
    return table
    
    
    
    
if __name__ == '__main__':
    import time
    
    t0 = time.clock()
    table = create_table()
    t1 = time.clock()
    print table.row_count(), 'rows'
    print 'Done in ', t1-t0, 'seconds'
    
    
        