'''
Created on 22/01/2014

@author: crispamares
'''

class IDefined(object):
    '''
    An IDefined has a grammar that represents its configuration and state 
    '''

    @property
    def grammar(self):
        raise NotImplementedError('The grammar property has to be implemented')
    
    
if __name__ == '__main__':
    class Defined(IDefined):
        @property
        def grammar(self):
            return {1:1}
            
    d = Defined()
    print Defined.grammar.fget(d)