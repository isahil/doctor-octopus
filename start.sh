#!bin/bash
echo "Starting Background Process for Doctor Octopus App"
nohup npm run start-dev >> logs/doc.log & 2>&1 &
echo "Background Process Started"
