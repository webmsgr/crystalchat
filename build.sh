pip3 install pyminifier
pip3 install -r requirements.txt
pip3 install pyinstaller
mkdir pybuild
rm pybuild/*
cp crystalchat.py pybuild/cchat.py
cp LICENSE pybuild/
cp icon.ico pybuild/
cp launcher.py pybuild/
cd pybuild
pyminifier --prepend=LICENSE -o crystalchat.py cchat.py
pyminifier --prepend=LICENSE -o launcher_obf.py launcher.py
pyinstaller launcher_obf.py -i icon.ico --name CrystalChat --onefile
cd ..
mkdir dist
rm dist/*
cd pybuild
cp dist/* ../dist/
cd ..
