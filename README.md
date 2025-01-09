# IPTIP_bot
![GitHub Release](https://img.shields.io/github/v/release/Rudolf31/IPTIP_bot) ![License](https://img.shields.io/badge/license-MIT-blue) ![Codacy Badge](https://app.codacy.com/project/badge/Grade/837c62cd09bb45ca836c470f67f953ca) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Rudolf31/IPTIP_bot/total) 

A corporate Telegram bot which serves birthday reminders to your employees or coworkers. 

# Roadmap
- [x] Automatic birthday reminders
- [x] Extra birthday reminders (manually requested)
- [ ] Omitting reminders of your own birthday
- [ ] Admin features (maintaining the employee list)
- [ ] Spreadsheet parsing
- [ ] Metrics
- [ ] Localization

# Deployment

Deployment instructions will be available here later

## Prerequisites

In order to function properly, the application will need:
- a Telegram bot token (available from [@BotFather](https://t.me/BotFather));
- an internet connection with or without public IP (Telegram bots do not rely on incoming connections unless webhooks are used to receive updates);
- a containerization system (e.g. Docker or Podman). We recommend an orchestrator (e.g. Docker Compose);

### Deploying with Docker Compose

#### Initial installation

```bash
# Create a directory for the project where you wish
mkdir tg_bot
cd tg_bot

# Clone the repository inside the directory
git clone https://github.com/Rudolf31/IPTIP_bot.git

# Create your docker-compose.yml file
touch docker-compose.yml
```

Edit the `docker-compose.yml` file with your favorite text editor. We recommend this setup:

```yml
services:
  bot:
    build:
      dockerfile: Dockerfile
      context: ./IPTIP_bot/
    restart: unless-stopped
    environment:
      - BOT_TOKEN=12345:ABCdefGhIJKlMnoPqrs-tuVWYz  # Place your token here
      - ADMINS=1234,5678  # Specify IDs of admins' telegram accounts 
    volumes:
      - "./database.db:/app/database.db"
```
The volume configuration will allow to have a sqlite database file directly in the root of the project, which will make it easier for you to access.
It may also be useful to have administrator accounts for maintenance capabilities. The ID of any Telegram account can be easily found through means like the @userinfobot.

When your `docker-compose.yml` file is done, you can build and run the project with docker compose like so:

```bash
sudo docker compose up -d --build
```

#### Updating

In order to update the project it is sufficient to pull the changes and rebuild the docker compose project:

```bash
# Enter the project directory
cd tg_bot

# Pull the changes from Git
(cd IPTIP_bot && git pull origin main)

# Stop all containers and rebuild
sudo docker compose stop && sudo docker compose up -d --build
```