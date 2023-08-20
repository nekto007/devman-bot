# Dvmn review notifier bot

This telegram bot project notifies you every time you get a code review on [Dvmn](https://dvmn.org/) homework.


## Features
- `Devman long polling` API utilization
- Notifies you instantly on every code review
- Tells you code review results
- Error logging

## Run
1. Clone project
```bash
git clone https://github.com/nekto007/devman-bot.git
cd devman-bot
```

2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install requirements
```bash
pip install -r requirements.txt
```

4. Rename `.env.example` to `.env` and place your secrets in it.  

5. Run telegram bot
```bash
python dvmn_api.py
```
## Run with `Docker`
1. Clone project
```bash
git clone https://github.com/nekto007/devman-bot
cd devman-bot
```

2. Build `Docker` image
```bash
docker build --tag dvmn-bot .
```

3. Rename `.env.example` to `.env` and place your secrets in it.  

4. Run `Docker` container
```bash
docker run -d --name dvmn-bot --env-file ./.env --restart always dvmn-bot
```