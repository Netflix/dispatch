# Install

Create a new pyenv with python 3.7:

Create a new .env file:

Start a postgres database (if developing locally) install

Install backend
pip install -e .

Run
dispatch db init

Run api
dispatch server run --debug

Install frontend

Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash

check node version
nvm ls
-> v12.7.0
system
default -> node (-> v12.7.0)
node -> stable (-> v12.7.0) (default)
stable -> 12.7 (-> v12.7.0) (default)
Install frontend

npm install

install yarn
https://yarnpkg.com/lang/en/docs/install/#mac-stable

Run frontend
yarn run serve
