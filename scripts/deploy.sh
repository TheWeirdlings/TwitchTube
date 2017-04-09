ssh thehollidayinn@104.236.106.190 << EOF
  rm -rf twitchtubebackup
  cp -R twitchtube-env/TwitchTube/ twitchtubebackup
  rm -rf twitchtube-env/TwitchTube/
EOF

scp -r ../../TwitchTube/ thehollidayinn@104.236.106.190:

ssh thehollidayinn@104.236.106.190 << EOF
  mv TwitchTube/ twitchtube-env/
  pm2 restart 0
EOF