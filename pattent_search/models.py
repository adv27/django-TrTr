from datetime import datetime
from mongoengine import *



class Patent(Document):

    filename    = StringField()
    created_at  = DateTimeField(default=datetime.utcnow)

    title       = StringField()
    abstract    = StringField()
    content     = StringField()

    meta = {'indexes': [
        {
            'fields': ['$title', "$content",'$abstract'],
            'default_language': 'english',
        }
    ]}
