# Simple Chat
A simple instant messaging application using Vue, Shadcn UI, TailwindCSS, Flask, and SQLAlchemy. 

## Installation 
Git, Python, and NPM are required to install the server. 
Download the project from github
``` bash
git clone https://github.com/jforseth210/SimpleChat
cd SimpleChat
```

Build the vue project
```bash
cd web
npm install
npm run build
cd ..
```

Install python dependencies and run the server
```bash
python -m venv venv
pip install -r requirements.txt
flask run
```

## Usage
Open http://localhost:5000 in your browser

Create an account (any username and password will do)

Have whoever you want to chat with create one to

Click the plus at the top of the conversation list 
and enter your friend's username. 

Click the text box on the bottom right and send a message!

