# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 06:29:20 2023

@author: Pradeep
"""

from flask import Flask
#from generic.generic_controller import generic_blueprint
from store.store_controller import store_blueprint
from price_index.price_index_controller import price_index_blueprint
from kvi.kvi_controller import kvi_blueprint
from config.app_config import config


app = Flask(__name__)

# Register the blueprint with the app
#app.register_blueprint(generic_blueprint, url_prefix="/")
app.register_blueprint(store_blueprint, url_prefix="/")
app.register_blueprint(price_index_blueprint, url_prefix="/")
app.register_blueprint(kvi_blueprint, url_prefix="/")

if __name__ == '__main__':
    app.run(port=config["general"]["port"])
    
# Get a list of all endpoints
endpoints = [rule.rule for rule in app.url_map.iter_rules()]
print(endpoints)
