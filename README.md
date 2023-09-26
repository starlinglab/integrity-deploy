# integrity-deploy

This ansible repo deploy the Starling Integrity services on virtual machines created by the integrity-deploy-vm repo.


## Environment setup

Place secret file in `group_vars/all/inventory_secrest.yml`
Place other required files in `files`

For re-deployment you may need to remove old SSH Keys from your known hosts

For Example: `ssh-keygen -f "/home/sysadmin/.ssh/known_hosts" -R "org2.browsertrix.stg.starlinglab.org"`

## Deployment

For production: `ansible-playbook -i inventory-prod.yml deploy.yml`  
For staging: `ansible-playbook -i inventory-stg.yml deploy.yml`  
Single servers can be deployed by adding the  `--limit <servername>` flag  

For Example  
`ansible-playbook -i inventory-stg.yml deploy.yml --limit org2.browsertrix.stg.starlinglab.org`

# Manual Process  

Some services require manual steps to initiate due to the way 3rd party applications interact with it. Below is a list of steps required to be preformed

## Setup dropbox sync

Dropbox sync can be  done via the RCLONE dropbox

### RCLONE


#### Pair with dropbox account
- Port forward 53682 over ssh (Ie `ssh user@server -L 53682:127.0.0.1:53682`)
- run `rclone config create dropbox dropbox`
- Visit url you are told in the message
- move the config file to the docker. IE
    - `mv /root/.config/rclone/rclone.conf /mnt/integrity_store/store/rclone/config/rclone.conf`
    - chown starling.starling /mnt/integrity_store/store/rclone/config/rclone.conf
- stop docker and restart it
    - docker-compose down
    - docker-compose up -d


#### Sync folders for inout

See https://github.com/starlinglab/integrity-preprocessor#folder

## Config

`monitor_job:` Used for monitoring, specify the job name to add to prometheus for this bot. This field is free form. Currently [staging,production,infra]  

### Chat Bot
`integrity_preprocessor_chatbot:` installs chatbot preprocessors from the integrity_preprocessor repo [true|false]

### Signal Bot
`signal_bot`: Configurations for the Signal Bot. Key Value pair, Keys are identification names used for configurations and folders.
`signal_phone_number`: signal number used for this bot
`signal_account_file:`: backed up account information from previous install. If you do not provide one you will need to login to the signal bot.

### Slack Bot
`slack_bot`: Configurations for the Slack Bot. Key Value pair, Keys are identification names used for configurations and folders  
`workspace:` Name of the workspace   
`slack_bot_token:` Slack bot's token for the workspace  
`slack_signing_secret:` Slack bot's signing secret for the workspace  
`slack_port:` Port that the slackbot will run on. Use a differnt port for each bot  

### Telegram Bot
`telegram_bot:` Configurations for the Telegram Bot. Key Value pair, Keys are identification names used for configurations and folders  
`telegram_bot_token:` Token for bot after configuring it with Father Bot


### Nginx and SSL for Slack Bot
`nginx_sites:` Defines Nginx and SSL settings   
`archive-slack-workspace-0.stg.starlinglab.org`: Cosmetic name of instance  
`ssl_provider:` Generates SSL Certificate for this domain should be `letsencrypt`   
`web_hostname:` Domain name to `generatearchive-slack-workspace-0.stg.starlinglab.org`  
`locations:` Definition of Reverse Proxy into slack bot  
`"/":` Defines ROOT   
`proxy_location:` Defines where to forward the domain. `http://127.0.0.1:{{slack_bot['workspace-0'].slack_port}}`  where workspace-0 is the key name of the related slack bot  

## Shared Mount
`nfs_client_mount:` Defines NFS Client  
`"main":` Name of mount - cosmetic  
`source:` `"10.55.0.1:/mnt/{{ nfs_shared_path }}"` Target of the mount  
`target:` `"/mnt/{{ nfs_shared_path }}"` Where to mount it  

# Requirements
`sudo apt install python3-dnspython`  

Ansible collections:  
community.general

Place secret file in `group_vars/all/inventory_secrest.yml`
Place other required files in `files`

For re-deployment you may need to remove old SSH Keys from your known hosts

For Example: `ssh-keygen -f "/home/sysadmin/.ssh/known_hosts" -R "org2.browsertrix.stg.starlinglab.org"`
