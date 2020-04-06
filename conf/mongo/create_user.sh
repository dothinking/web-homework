#!/bin/bash
# pay attention to file format: dos v.s. unix
# :set ff=unix
echo "Creating mongo users..."
mongo -u admin -p root << EOF
use app_coordinates
db.createUser({
    user: 'tom', 
    pwd: 'goodboy', 
    roles:[{
        role:'readWrite',
        db:'app_coordinates'}]
})
EOF
echo "Mongo users created."
