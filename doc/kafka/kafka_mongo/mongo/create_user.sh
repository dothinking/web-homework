#!/bin/bash
# pay attention to file format: dos v.s. unix
# :set ff=unix
echo "Creating mongo users..."
mongo -u admin -p root << EOF
use test
db.createUser({
    user: 'tom', 
    pwd: 'goodboy', 
    roles:[{
        role:'readWrite',
        db:'test'}]
})
EOF
echo "Mongo users created."
