@echo off
pip3 install pyminifier
pip3 install pyinstaller
pip3 install -r requirements.txt
mkdir pybuild
del pybuild/*
cp server.py pybuild/
cp crystalchat.py pybuild/
cp LICENSE pybuild/
cp icon.ico pybuild/
cp launcher.py pybuild/
cd pybuild
del *_obf.py
del dist/*
pyminifier --prepend=LICENSE -o crystalchat_obf.py crystalchat.py
pyminifier --prepend=LICENSE -o launcher_obf.py launcher.py
pyminifier --prepend=LICENSE -o server_obf.py server.py
pyinstaller server_obf.py -i icon.ico --name CrystalChatServer --onefile
pyinstaller crystalchat_obf.py -i icon.ico --name CrystalChat --onefile
pyinstaller launhcer_obf.py -i icon.ico --name CrystalChatLauncher --onefile
cd ..
mkdir dist
del dist/*
cd pybuild
cp dist/* ../dist/
cd ..
