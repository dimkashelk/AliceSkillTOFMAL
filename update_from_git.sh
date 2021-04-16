
#!/bin/sh

git fetch --all
git reset --hard origin/master
./venv/bin/python -m pip install -r requirements.txt
chmod -R 777 ./
sudo systemctl restart alice
