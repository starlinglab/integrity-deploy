# Integrity-deploy

This ansible repo deploy the Starling Integrity services on several machines. Our Proxmox setup has Virtual machines provisioned by the integrity-deploy-vm repo.

## Environment setup

Place secret file in `group_var/all/invetory_secrets.yml`
Place other required secret files in `files`

### invetory_secrets.yml

This file is used to centralized secret keys in one place and use ansible variables in the inventory. This file is not needed it password are replaced in the invetory YML itself

This file is to be placed in `group_var/all/invetory_secrets.yml`. We hold a copy of it in BitWarden.

```yaml
# Root password to be set on all computers
secret_root_password: "SuperSecretPassword"
# Sysadmin password to be set on all computers
secret_sysadmin_password: "{{ secret_root_password }}"
# Root password for KVM where servers are deployed
secret_KVM_password: "{{ secret_root_password }}"

# Alerting
# Matrix user token used to authenticate with matrixAPI
secret_matrix_user_token: "MD...Cg"
# Password used to secure AlertManager
secret_matrix_alertmanager_secret: "PASSWORD_ALERT_MANAGER"
# Password to access Loki server
secret_loki_password: "PASSWORD_FOR_LOKI"

# Browsertrix Secrets
# Key used to secure browsertrix internal functions
secret_browsertrix: "PASSWORD_FOR_BROWSERTRIX"
# Admin password to browsertrix
secret_browsertrix_admin_password: "password"
# User password for main browsertrix user
secret_browsertrix_user_password: "userpassword"

# Integrity Backend
# JWT Salt
secret_integrity_jwt: "sekret"
# URL for Web3 Storage API
secret_web3_storage_api_token: "GET_FROM_WEB3.STORAGE"

# E-Mail
# Password for e-mail server
secret_outbound_email_password: "smtp_email_password"

# Git hub token for private repos
# Persnal Key to clone repos 
secret_github_token: "ghp_your_own_token"

# Slack 
# Secret Keys
secret_stg_slack_bot_workspace0_token: "xoxb-..sesdocs"
secret_stg_slack_bot_workspace0_secret: "see_docs"
secret_prod_slack_bot_workspace0_token: "xoxb-...seedocs"
secret_prod_slack_bot_workspace0_secret: "see_docs"

# Telegram
secret_stg_telegram_bot_testbot1_token: "see:docs"

# IPFS Swarm Key
secret_ipfs_swarm_key: "xxxxxxxxGENERATED_SWARM_KEYxxxxxxxxxxxxx"

#Numbers API
secret_numbers_api: "Get_From_Numbers"

# iscn wallet
secret_iscn_mnemonic_stg: "Bunch Of Words Here"
secret_iscn_mnemonic_prod: "Bunch Of Words Here"

# authsign access token
secret_authsign_token: "random_password_here"
```

### files Folder

This folder holds non public files that are required for functionality of this system. Many of these files are defined in the inventory files and can be named anything, while others are role based.


### Signal Account
`prod_signal_account.zip`, `stg_signal_account.zip`
This is a zip of signal account folder after initializing signald. This allows skipping the manual process or paring a signal account with the signald service.


`stg_cai_key.pem`, `stg_cai_key.pub`,`prod_cai_key.pem`,`prod_cai_key.pub`
Public Key (`pub`) and private key (`pem`) of claim_tool identity

`claim_tool`
copy of claim_tool for target system 

`prod_profile.tar.gz`,`stg_profile.tar.gz`
Chrome profiles created using Browsertrix to contain logged sessions if media sites.

`prod_preprocessor-browsertrix-collections-hala.json`, `prod_preprocessor-browsertrix-collections-star.json`,`stg_preprocessor-browsertrix-collections-all.json`
JSON file containing collections to be created on Browsertrix 

`prod_preprocessor-folder.json`,`stg_preprocessor-folder.json`
Configuration for folder preprocessor

`prod_preprocessor-chatbot-signal-users.json`, `stg_preprocessor-chatbot-signal-users.json`
User directory for Signal, including the author to be used

`prod_preprocessor-chatbot.json`, `stg_preprocessor-chatbot.json`
Definition of chatbots preprocessor to tie into.

`stg_integrity.config.json`,`prod_integrity.config.json`
configuration for Integrity-Backend


### Re-deployment
For re-deploymet you may need to remove old SSH Keys from your known hosts

For Example: `ssh-keygen -f "/home/sysadmin/.ssh/known_hosts" -R "org2.browsertrix.stg.starlinglab.org"`

## Deployment

For production: `ansible-playbook -i inventory-prod.yml deploy.yml`
For staging: `ansible-playbook -i inventory-stg.yml deploy.yml`
Single servers can be deployed by adding the  `--limit <servername>` flag
To only update confings add the `--tags config` flag

For Example
`ansible-playbook -i inventory-stg.yml deploy.yml --limit org2.browsertrix.stg.starlinglab.org --tags config`

# Manual Proecess

Some services require manual steps to initiate due to the way 3rd party applications interact with it. Below is a list of steps required to be preformed

## Login to dropbox
- Login to drop box account in a browser
- Create a folder as needed ie `integrity-prod-starling-org` (replace this text in instructions below with whatever you created)
- Login to ALL other server running this dropbox account as root
- Exclude the newly created folder on all other servers
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
- Back on integrity server, in docker shell
    - repeat this command until you see a list of all the directories, it may take a few seconds and/or tries
        - `cd /home/dropbox-user/Dropbox/ && /opt/dropbox/dropbox exclude add * `
    - Remove folder to sync
        - `/opt/dropbox/dropbox exclude remove integrity-prod-starling-org`
    - Leave dropbox container
        - `exit`

## Mount Dropbox to shared fs
- Create shared folder in dropbox
    - `mkdir /mnt/integrity_store/store/dropbox/Dropbox/integrity-prod-starling-org/shared`
    - `chown starling.starling /mnt/integrity_store/store/dropbox/Dropbox/integrity-prod-starling-org/shared`
- Edit /etc/fstab add following line
```
/mnt/integrity_store/starling/shared /mnt/integrity_store/store/dropbox/Dropbox/integrity-prod-starling-org/shared none defaults,bind 0 0
```
- Mount new folder
    - `mount /mnt/integrity_store/store/dropbox/Dropbox/integrity-prod-starling-org/shared`

# Interesting Variables

`monitor_job:` Used for monitoring, specify the job name to add to prometheus for this bot. This field is free form. Currently [staging,production,infra]  

`integrity_preprocessor_chatbot:` Installs chatbot preprocessors from the integrity_preprocessor repo [true|false]

## Signal Bot
`signal_bot`: Configurations for the Signal Bot. This is a Dict, Keys are identification names used for configurations and folders.
`signal_phone_number`: signal number used for this bot
`signal_account_file:`: Backed up account information from previous install. If you do not provide one you will need to login to the signal bot.

## Slack Bot
`slack_bot`: Configurations for the Slack Bot. This is a Dict, Keys are identification names used for configurations and folders
`workspace:` Name of the workspace 
`slack_bot_token:` Slack bot's token for the workspace
`slack_signing_secret:` Slack bot's signing secret for the workspace
`slack_port:` Port that the slackbot will run on. Use a differnt port for each bot

## Telegram Bot
`telegram_bot:` Configurations for the Telegram Bot. This is a Dict, Keys are identification names used for configurations and folders
`telegram_bot_token:` Token for bot after configuring it with Father Bot

## Nginx and SSL for Slack Bot
`nginx_sites:` Defines Nginx and SSL settings 
`archive-slack-workspace-0.stg.starlinglab.org`: Cosmetic name of instance
`ssl_provider:` Generates SSL Certificate for this domain should be `letsencrypt` 
`web_hostname:` Domain name to generate `archive-slack-workspace-0.stg.starlinglab.org`
`locations:` Definition of reverse proxy into slack bot
`"/":` Defines ROOT 
`proxy_location:` Defines where to forward the domain. `http://127.0.0.1:{{slack_bot['workspace-0'].slack_port}}`  where workspace-0 is the key name of the related slack bot

# Shared Mount
`nfs_client_mount:` Defines NFS Client
`"main":` Name of mount - cosmetic
`source:` `"10.55.0.1:/mnt/{{ nfs_shared_path }}"` Target of the mount
`target:` `"/mnt/{{ nfs_shared_path }}"` Where to mount it

# Requiremnets
`sudo apt install python3-dnspython`


