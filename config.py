# Copyright 2012 Hai Thanh Nguyen
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from google.appengine.ext import ndb
from google.appengine.api import memcache

def update_config_cache(name, value):
    memcache.set("config__"+name, value)

def update_config(name, value, visible):
    q = ConfigModel.query(ConfigModel.name==name).get()
    if not q:
        model = ConfigModel(name=name, value=value, visible=visible)
        model.put()
        update_config_cache(name, value)
    else:
        q.value = value
        q.visible = visible
        q.put()
        memcache.add("config__"+name, value)

def get_config(name):
    cache = memcache.get("config__"+name)
    if cache == None:
        q = ndb.gql("SELECT value FROM ConfigModel WHERE name = :1", name).get()
        if q == None:
            raise Exception("The configuration does not exist.")
        update_config_cache(name, q.value)
        return q.value
    else:
        return cache

class ConfigModel(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.StringProperty()
    visible = ndb.BooleanProperty()
