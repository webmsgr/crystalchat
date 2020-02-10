pip3 install pyminifier
pip3 install -r requirements.txt
pip3 install pyinstaller
pyminifier --prepend=LICENSE -o c.py crystalchat.py
pyinstaller --add-data "versions:autoupdate" c.py -i icon.ico --name CrystalChat --onefile
rm c.py
