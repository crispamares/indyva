# -*- coding: utf-8 -*-
'''
Created on 06/09/2013

@author: jmorales
'''

import pymongo 
from indyva.dataset.table import Table
from indyva.dataset.schemas import TableSchema, AttributeSchema

def create_spines_schema():
    # TODO: MultiKey is not yet implemented
    #schema = TableSchema({},index=['spine_id', 'dendrite_id'])
    schema = TableSchema({},index='spine_id')
    schema.add_attribute('spine_id', 
                         dict(attribute_type= 'CATEGORICAL',
                              key=True))
    schema.add_attribute('dendrite_id','CATEGORICAL')
    schema.add_attribute('dendrite_type','CATEGORICAL')
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

def create_spines_table():
    client = pymongo.MongoClient()
    db = client['spinesIP']
    table = Table(name='spines', schema=create_spines_schema())
    for d in db['spines'].find({},{'_id':False}):
        d['spine_id'] = '{0}-{1}'.format(d['dendrite_id'], d['spine_id']) 
        table.insert(d)
    return table
    
def create_dendrites_table(spines_table):
    column = 'dendrite_id'
    tv= spines_table.aggregate([{'$group' : 
                             {'_id': '$'+column, 
                              'dendrite_type': {'$first':'$dendrite_type'} }},
                            {'$project' : {column: '$_id',
                                           'dendrite_type':'$dendrite_type',
                                           '_id':False}}
                            ])

    table = Table(name='dendrites', schema=dict(index='dendrite_id',
        attributes=dict(dendrite_id='CATEGORICAL', 
                        dendrite_type='CATEGORICAL')))
    table.data(tv.get_data())
    return table
    
if __name__ == '__main__':
    import time
    
    t0 = time.clock()
    table = create_spines_table()
    t1 = time.clock()
    print table.row_count(), 'rows'
    print 'Done in ', t1-t0, 'seconds'
    
    t0 = time.clock()
    dendrites_table = create_dendrites_table(table)
    t1 = time.clock()
    print dendrites_table.row_count(), 'rows'
    print 'Done in ', t1-t0, 'seconds'
    
    
        