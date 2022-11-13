# Poodle DDoS

Poodle is a simple DDoS script, where you can create a bot-net and, 
by using built in 'command line' send certain commands to bots in the network.

## Requirements
- Python 3+
- requests

## Installation
1. Clone Repo
2. Set server host and port fields in config.json
3. Find the right POST request and edit poodle.py Stresser class
4. Install Libraries
````commandline
pip install -r requirments.txt
````

## Usage

```commandline
python3 poodle.py --server
           or
python3 poodle.py --bot
``` 
