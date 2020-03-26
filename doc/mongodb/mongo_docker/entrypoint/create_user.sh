#!/bin/bash
echo "Creating mongo users..."
mongo -u admin -p root << EOF
use first_db
db.createUser({user: 'tom', pwd: 'goodboy', roles:[{role:'readWrite',db:'first_db'}]})
EOF