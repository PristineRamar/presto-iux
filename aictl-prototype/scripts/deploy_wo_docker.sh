cd $HOME
# delete previous copy in remote machine
ssh -i .ssh/aictl-vm-key.pem suriya@20.198.90.252 'rm -rf aictl-prototype*'
# zip and copy to remote machine
rm aictl-prototype.zip
echo $PWD
zip -r aictl-prototype.zip aictl-prototype -x "*/env-aictl/*"
scp -r -i .ssh/aictl-vm-key.pem $HOME/aictl-prototype.zip suriya@20.198.90.252:/home/suriya/
# run script in remote
ssh -t -i .ssh/aictl-vm-key.pem suriya@20.198.90.252 "bash -s" < $HOME/aictl-prototype/scripts/remote_exec.sh
