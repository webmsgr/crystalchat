@echo off
pip3 install pyminifier
pip3 install -r requirements.txt
mkdir pybuild
rm pybuild/*
cp server.py pybuild/
cp crystalchat.py pybuild/
cp LICENSE pybuild/
cp icon.ico pybuild/
cd pybuild
rm *_obf.py
rm dist/*
pyminifier --prepend=LICENSE -o crystalchat_obf.py crystalchat.py
pyminifier --prepend=LICENSE -o server_obf.py server.py
pyinstaller server_obf.py -i icon.ico --name CrystalChatServer --onefile
pyinstaller crystalchat_obf.py -i icon.ico --name CrystalChat --onefile
cd ..
mkdir dist
rm dist/*
cd pybuild
cp dist/* ../dist/
cd ..