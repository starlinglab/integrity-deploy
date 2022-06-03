# Integrity-deploy

This ansible repo deploy the  Starling Integrity services on virtual machines created by the integrity-deploy-vm repo.

## Environment setup

Place secret file in `group_var/all/inventory_secrest.yml`
Place otehr required files in `files`

For re-deploymet you may need to remove old SSH Keys fomr your known hosts

For Example: `ssh-keygen -f "/home/sysadmin/.ssh/known_hosts" -R "org2.browsertrix.stg.starlinglab.org"`

## Deployment

For production: `ansible-playbook -i inventory-prod.yml deploy.yml`
For staging: `ansible-playbook -i inventory-stg.yml deploy.yml`
Single servers can be deployed by adding the  `--limit <servername>` flag

For Example
`ansible-playbook -i inventory-stg.yml deploy.yml --limit org2.browsertrix.stg.starlinglab.org`

# Manual Proecess

Some services require manual steps to initiate due to the way 3rd party applications interact with it. Below is a list of steps required to be preformed

## Login to dropbox
- Login to drop box account in a browser
- Create a folder as needed ie `integrity-prod-starling-org` (replace this text in instructions below with whatever you created)
- Login to ALL other server running this dropbox as root
  - `cd /root/dropbox`
  - `docker exec -it dropbox /bin/bash`
  - `cd /home/dropbox-user/Dropbox/`
  - `/opt/dropbox/dropbox exclude add integrity-prod-starling-org`
  - `exit`
- On integrity server again
- `cd /root/dropbox`
- `docker-compose logs`
- Get a dropbox shell ready 
    - `docker exec -it dropbox /bin/bash`
- Copy the url from the line "Please Visit https://www.dropbox.com/cli_link_nonce?nonce=xxxxxxxx"
- Paste the url it into a browser where you are logged into dropbox
- Click `Connect`
- On integrity server, in docker shell use this comment
    - repeat this command until you see a list of all the directories, it may take a few seconds and/or tries
        - `cd /home/dropbox-user/Dropbox/ && /opt/dropbox/dropbox exclude add * `
    - Remove folder to sync
        - `/opt/dropbox/dropbox exclude remove integrity-prod-starling-org`
    - Leave dropbox container
        - `exit`

## Mount Dropbox to shared fs
- Create shared folder in dropbox
    - `mkdir /mnt/store/dropbox/Dropbox/integrity-prod-starling-org/shared`
    - `chown starling.starling /mnt/store/dropbox/Dropbox/integrity-prod-starling-org/shared`
- edit /etc/fstab add following line
```
/mnt/integrity_store/starling/shared /mnt/store/dropbox/Dropbox/integrity-prod-starling-org/shared none defaults,bind 0 0
```
- Mount new folder
    - `mount /mnt/store/dropbox/Dropbox/integrity-prod-starling-org/shared`


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

