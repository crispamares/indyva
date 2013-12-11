'''
Created on Oct 12, 2012

@author: crispamares

This module provides access to the configuration of the service.
Deals with the persistence and online changes  
'''
import json
import atexit

CONFIG_FILE = 'conf.json'

''' @var _config: Dict with all the variables '''
_config = None
''' @var _dirty: The file should be updated '''
_dirty = False


def _save_config():
    print 'exit', _dirty
    if _dirty:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(_config, f)
atexit.register(_save_config)

def _load_config():
    config = {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except:
        pass
    return config

def declare_config_variable(name, default):
    ''' if the value is in the config file, the stored value is returned
    otherwise the default value is returned and a new field is created in the 
    config file 
    '''
    global _config, _dirty
    if _config == None:
        _config = _load_config()
    if not _config.has_key(name):
        _config[name] = default
        # A new variable has been declared the cofig 
        # file must be updated at the end of the program
        _dirty = True
    variable = _config[name]
        
    return variable