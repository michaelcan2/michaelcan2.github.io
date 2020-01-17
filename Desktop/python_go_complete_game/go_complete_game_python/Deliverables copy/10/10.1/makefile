setup:
	sudo apt-get update
	-sudo apt install software-properties-common -y
	-sudo add-apt-repository ppa:deadsnakes/ppa -y
	sudo apt update
	-sudo apt-get install python3.7 # Leading dash allows failure if already installed
	-sudo apt-get install python3-pip
	-sudo apt-get install python3-venv
	-sudo apt-get install -y python3-setuptools
	sudo pip3 install --upgrade pip
	python3 -m venv env
	. env/bin/activate
	sudo pip3 install -r requirements.txt # install dependencies
	pytest -p no:warnings