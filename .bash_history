ls
sudo -u bp15ru /home/bp15ru/venv/bin/gunicorn --version
source .venv/bin/activate
sudo -u bp15ru /home/bp15ru/venv/bin/gunicorn --version
sudo -u bp15ru /home/bp15ru/.venv/bin/gunicorn --version
sudo grep -rn "/home/bp15" /home/bp15ru   --exclude-dir=venv --exclude-dir=.git --exclude-dir=staticfiles
sudo nano /etc/systemd/system/gunicorn-website.service
sudo systemctl daemon-reload
sudo systemctl start gunicorn-website
sudo systemctl enable gunicorn-website
sudo systemctl status gunicorn-website
sudo nano /etc/nginx/sites-available/website
sudo nginx -t
sudo systemctl reload nginx
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d bp15.ru -d www.bp15.ru
sudo ufw allow 'Nginx Full'
sudo systemctl restart gunicorn-website
sudo systemctl reload nginx
curl -I https://bp15.ru
curl -I http://bp15.ru
ls -la /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/website /etc/nginx/sites-enabled/website
sudo nginx -T 2>/dev/null | grep -nE "server_name|listen|root|server \{|# configuration file"
sudo systemctl reload nginx
nginx -t~
nginx -t
sudo systemctl status nginx --no-pager
sudo nano /etc/nginx/sites-available/website
nginx -t
sudo nginx -t
sudo systemctl status nginx --no-pager
sudo systemctl reload nginx
sudo systemctl status nginx --no-pager
sudo systemctl status gunicorn-website --no-pager
sudo journalctl -u gunicorn-website -n 80 --no-pager
nano /etc/systemd/system/gunicorn-website.service
sudo nano /etc/systemd/system/gunicorn-website.service
sudo systemctl restart gunicorn-website
'systemctl daemon-reload
systemctl daemon-reload
sudo systemctl restart gunicorn-website
sudo systemctl status gunicorn-website
(.venv) bp15ru@bp15:~$ sudo systemctl status gunicorn-website
● gunicorn-website.service - Gunicorn daemon for Django project website (user bp15ru)
Nov 05 09:52:16 bp15.ru systemd[1]: gunicorn-website.service: Failed with result 'exit-code'.
Nov 05 09:52:20 bp15.ru systemd[1]: gunicorn-website.service: Scheduled restart job, restart counter is at 1.
Nov 05 09:52:20 bp15.ru systemd[1]: Started gunicorn-website.service - Gunicorn daemon for Django project website (user bp15ru).
Nov 05 09:52:20 bp15.ru gunicorn[8509]: [2026-11-05 09:52:20 +0000] [8509] [INFO] Starting gunicorn 25.3.0
Nov 05 09:52:20 bp15.ru gunicorn[8509]: [2026-11-05 09:52:20 +0000] [8509] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:52:21 bp15.ru gunicorn[8509]: [2026-11-05 09:52:21 +0000] [8509] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
sudo nano /etc/systemd/system/gunicorn-website.service
sudo systemctl restart gunicorn-website
systemctl daemon-reload
sudo systemctl restart gunicorn-website
sudo systemctl status gunicorn-website
(.venv) bp15ru@bp15:~$ sudo systemctl status gunicorn-website
● gunicorn-website.service - Gunicorn daemon for Django project website (user bp15ru)
sudo journalctl -u gunicorn-website -n 50 --no-pager
bp15ru@bp15:~$ sudo journalctl -u gunicorn-website -n 50 --no-pager
Nov 05 09:56:24 bp15.ru gunicorn[8774]: [2026-11-05 09:56:24 +0000] [8774] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:25 bp15.ru gunicorn[8774]: [2026-11-05 09:56:25 +0000] [8774] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:26 bp15.ru gunicorn[8774]: [2026-11-05 09:56:26 +0000] [8774] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:27 bp15.ru gunicorn[8774]: [2026-11-05 09:56:27 +0000] [8774] [ERROR] Can't connect to /run/gunicorn-website.sock
Nov 05 09:56:28 bp15.ru systemd[1]: gunicorn-website.service: Main process exited, code=exited, status=1/FAILURE
Nov 05 09:56:28 bp15.ru systemd[1]: gunicorn-website.service: Failed with result 'exit-code'.
Nov 05 09:56:31 bp15.ru systemd[1]: gunicorn-website.service: Scheduled restart job, restart counter is at 5.
Nov 05 09:56:31 bp15.ru systemd[1]: Started gunicorn-website.service - Gunicorn daemon for Django project website (user bp15ru).
Nov 05 09:56:31 bp15.ru gunicorn[8778]: [2026-11-05 09:56:31 +0000] [8778] [INFO] Starting gunicorn 25.3.0
Nov 05 09:56:31 bp15.ru gunicorn[8778]: [2026-11-05 09:56:31 +0000] [8778] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:32 bp15.ru gunicorn[8778]: [2026-11-05 09:56:32 +0000] [8778] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:33 bp15.ru gunicorn[8778]: [2026-11-05 09:56:33 +0000] [8778] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:34 bp15.ru gunicorn[8778]: [2026-11-05 09:56:34 +0000] [8778] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:35 bp15.ru gunicorn[8778]: [2026-11-05 09:56:35 +0000] [8778] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:36 bp15.ru gunicorn[8778]: [2026-11-05 09:56:36 +0000] [8778] [ERROR] Can't connect to /run/gunicorn-website.sock
Nov 05 09:56:36 bp15.ru systemd[1]: gunicorn-website.service: Main process exited, code=exited, status=1/FAILURE
Nov 05 09:56:36 bp15.ru systemd[1]: gunicorn-website.service: Failed with result 'exit-code'.
Nov 05 09:56:39 bp15.ru systemd[1]: gunicorn-website.service: Scheduled restart job, restart counter is at 6.
Nov 05 09:56:39 bp15.ru systemd[1]: Started gunicorn-website.service - Gunicorn daemon for Django project website (user bp15ru).
Nov 05 09:56:39 bp15.ru gunicorn[8782]: [2026-11-05 09:56:39 +0000] [8782] [INFO] Starting gunicorn 25.3.0
Nov 05 09:56:39 bp15.ru gunicorn[8782]: [2026-11-05 09:56:39 +0000] [8782] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:40 bp15.ru gunicorn[8782]: [2026-11-05 09:56:40 +0000] [8782] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:41 bp15.ru gunicorn[8782]: [2026-11-05 09:56:41 +0000] [8782] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:42 bp15.ru gunicorn[8782]: [2026-11-05 09:56:42 +0000] [8782] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:43 bp15.ru gunicorn[8782]: [2026-11-05 09:56:43 +0000] [8782] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:44 bp15.ru gunicorn[8782]: [2026-11-05 09:56:44 +0000] [8782] [ERROR] Can't connect to /run/gunicorn-website.sock
Nov 05 09:56:44 bp15.ru systemd[1]: gunicorn-website.service: Main process exited, code=exited, status=1/FAILURE
Nov 05 09:56:44 bp15.ru systemd[1]: gunicorn-website.service: Failed with result 'exit-code'.
Nov 05 09:56:47 bp15.ru systemd[1]: gunicorn-website.service: Scheduled restart job, restart counter is at 7.
Nov 05 09:56:47 bp15.ru systemd[1]: Started gunicorn-website.service - Gunicorn daemon for Django project website (user bp15ru).
Nov 05 09:56:47 bp15.ru gunicorn[8787]: [2026-11-05 09:56:47 +0000] [8787] [INFO] Starting gunicorn 25.3.0
Nov 05 09:56:47 bp15.ru gunicorn[8787]: [2026-11-05 09:56:47 +0000] [8787] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:48 bp15.ru gunicorn[8787]: [2026-11-05 09:56:48 +0000] [8787] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:49 bp15.ru gunicorn[8787]: [2026-11-05 09:56:49 +0000] [8787] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:50 bp15.ru gunicorn[8787]: [2026-11-05 09:56:50 +0000] [8787] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:51 bp15.ru gunicorn[8787]: [2026-11-05 09:56:51 +0000] [8787] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:52 bp15.ru gunicorn[8787]: [2026-11-05 09:56:52 +0000] [8787] [ERROR] Can't connect to /run/gunicorn-website.sock
Nov 05 09:56:52 bp15.ru systemd[1]: gunicorn-website.service: Main process exited, code=exited, status=1/FAILURE
Nov 05 09:56:52 bp15.ru systemd[1]: gunicorn-website.service: Failed with result 'exit-code'.
Nov 05 09:56:55 bp15.ru systemd[1]: gunicorn-website.service: Scheduled restart job, restart counter is at 8.
Nov 05 09:56:55 bp15.ru systemd[1]: Started gunicorn-website.service - Gunicorn daemon for Django project website (user bp15ru).
Nov 05 09:56:56 bp15.ru gunicorn[8789]: [2026-11-05 09:56:56 +0000] [8789] [INFO] Starting gunicorn 25.3.0
Nov 05 09:56:56 bp15.ru gunicorn[8789]: [2026-11-05 09:56:56 +0000] [8789] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:57 bp15.ru gunicorn[8789]: [2026-11-05 09:56:57 +0000] [8789] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:58 bp15.ru gunicorn[8789]: [2026-11-05 09:56:58 +0000] [8789] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:56:59 bp15.ru gunicorn[8789]: [2026-11-05 09:56:59 +0000] [8789] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:57:00 bp15.ru gunicorn[8789]: [2026-11-05 09:57:00 +0000] [8789] [ERROR] connection to /run/gunicorn-website.sock failed: [Errno 13] Permission denied
Nov 05 09:57:01 bp15.ru gunicorn[8789]: [2026-11-05 09:57:01 +0000] [8789] [ERROR] Can't connect to /run/gunicorn-website.sock
Nov 05 09:57:01 bp15.ru systemd[1]: gunicorn-website.service: Main process exited, code=exited, status=1/FAILURE
Nov 05 09:57:01 bp15.ru systemd[1]: gunicorn-website.service: Failed with result 'exit-code'.




sudo grep -nE "RuntimeDirectory|UMask|--bind" /etc/systemd/system/gunicorn-website.service
(.venv) bp15ru@bp15:~$ sudo grep -nE "RuntimeDirectory|UMask|--bind" /etc/systemd/system/gunicorn-website.service
9:RuntimeDirectory=gunicorn-website
10:RuntimeDirectoryMode=0750
11:UMask=0007
16:          --bind unix:/run/gunicorn-website.sock \
sudo sed -i 's|unix:/run/gunicorn-website.sock|unix:/run/gunicorn-website/gunicorn.sock|' /etc/systemd/system/gunicorn-website.service
sudo systemctl restart gunicorn-website
systemctl daemon-reload
sudo systemctl restart gunicorn-website
sudo systemctl status gunicorn-website
sudo systemctl restart nginx.service 
sudo systemctl status gunicorn-website --no-pager
sudo ls -l /run/gunicorn-website/ 2>/dev/null
sudo grep -n "proxy_pass" /etc/nginx/sites-available/website
sudo tail -n 30 /var/log/nginx/error.log
sudo journalctl -u gunicorn-website -n 30 --no-pager
sudo sed -i 's|unix:/run/gunicorn-website.sock|unix:/run/gunicorn-website/gunicorn.sock|' /etc/nginx/sites-available/website
sudo grep -n "proxy_pass" /etc/nginx/sites-available/website
sudo systemctl restart nginx.service 
sudo systemctl restart gunicorn-website
sudo nano /etc/systemd/system/gunicorn-website.service
sudo nano /etc/nginx/sites-available/website
sudo systemctl restart gunicorn-website
sudo systemctl restart nginx.service 
ls
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-production.txt 
sudo -u bp15ru /home/bp15ru/venv/bin/gunicorn --version
sudo usermod -aG sudo bp15ru
su
