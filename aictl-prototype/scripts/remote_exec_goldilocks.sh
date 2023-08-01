# stop aictl and ngin
# sudo systemctl stop aictl
unzip aictl-prototype.zip
cd aictl-prototype/
# source env-aictl/bin/activate
python3.10 -m pip install -r requirements.txt
# init database
cd aictl/scripts/
python3.10 init_db.py
# restart aictl daemon
sudo systemctl restart goldilocks
# restart nginx
sudo systemctl restart nginx