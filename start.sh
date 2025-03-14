#!bin/bash
echo "Starting Background Process for Doctor Octopus App"
nohup npm start >> doc.log & 2>&1 &
echo "Background Process Started"
