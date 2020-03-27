#!/bin/bash
# pay attention to file format: dos v.s. unix
# :set ff=unix
echo "Creating mongo users..."
mongo -u admin -p root << EOF
use first_db
db.createUser({
    user: 'tom', 
    pwd: 'goodboy', 
    roles:[{
        role:'readWrite',
        db:'first_db'}]
})
EOF
echo "Mongo users created."
