
ls /opt/ml/input/data/train/
echo "Starting preload with hsm_restore...."
nohup find /opt/ml/input/data/train/ -type f -print0 | xargs -0 -n 1 lfs hsm_restore
echo "Preload is complete"
