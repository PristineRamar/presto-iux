unzip aictl-prototype.zip
cd aictl-prototype/
# source env-aictl/bin/activate
python3.10 -m pip install -r requirements.txt
# restart aictl daemon
sudo systemctl restart aictl
# restart nginx
sudo systemctl restart nginx