
#!/bin/sh

chmod -R 777 ./
git fetch --all
git reset --hard origin/master
./venv/bin/python -m pip install -r requirements.txt
sudo systemctl restart alice
