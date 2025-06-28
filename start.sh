#!bin/bash
echo "Starting Background Process for Doctor Octopus App"
nohup npm run start >> logs/doc.log & 2>&1 &
nohup npm run notification >> logs/notification.log & 2>&1 &
nohup npm run fixme >> logs/fixme.log & 2>&1 &
echo "Background Process Started"
