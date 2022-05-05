# Manual Proecess

- [ ] Login to drop box
- [ ] Exclude and include
- [ ] Mount dropbox to share

/etc/fstab:
```
/mnt/integrity_store/starling/shared /mnt/store/dropbox/Dropbox/integrity-stg-starlinglab-org/shared /source /destination none defaults,bind 0 0
```

`monitor_job:` Used for monitoring, specify the job name to add to prometheus for this bot. This field is free form. Currently [staging,production,infra]  

`integrity_preprocessor_chatbot:` installs chatbot preprocessors from the integrity_preprocessor repo [true|false]

## Signal Bot
`signal_bot`: Configurations for the Signal Bot. Key Value pair, Keys are identification names used for configurations and folders.
`signal_phone_number`: signal number used for this bot
`signal_account_file:`: backed up account information from previous install. If you do not provide one you will need to login to the signal bot.

## slack Bot
`slack_bot`: Configurations for the Slack Bot. Key Value pair, Keys are identification names used for configurations and folders
`workspace:` Name of the workspace 
`slack_bot_token:` Slack bot's token for the workspace
`slack_signing_secret:` Slack bot's signing secret for the workspace
`slack_port:` Port that the slackbot will run on. Use a differnt port for each bot

## Telegram Bot
`telegram_bot:` Configurations for the Telegram Bot. Key Value pair, Keys are identification names used for configurations and folders
`telegram_bot_token:` Token for bot after configuring it with Father Bot


## Nginx and SSL for Slack Bot
`nginx_sites:` Defines Nginx and SSL settings 
`archive-slack-workspace-0.stg.starlinglab.org`: Cosmetic name of instance
`ssl_provider:` Generates SSL Certificate for this domain should be `letsencrypt` 
`web_hostname:` Domain name to `generatearchive-slack-workspace-0.stg.starlinglab.org`
`locations:` Definition of Reverse Proxy into slack bot
`"/":` Defines ROOT 
`proxy_location:` Defines where to forward the domain. `http://127.0.0.1:{{slack_bot['workspace-0'].slack_port}}`  where workspace-0 is the key name of the related slack bot

# Shared Mount
`nfs_client_mount:` Defines NFS Client
`"main":` Name of mount - cosmetic
`source:` `"10.55.0.1:/mnt/{{ nfs_shared_path }}"` Target of the mount
`target:` `"/mnt/{{ nfs_shared_path }}"` Where to mount it

# Requiremnets
`sudo apt install python3-dnspython`

Ansible collections:
community.general

