sudo cp motionsensor.service /etc/systemd/system/motionsensor.service
sudo cp monitor.service /etc/systemd/system/monitor.service
sudo systemctl daemon-reload
sudo systemctl enable motionsensor
sudo systemctl enable monitor