build: clean venv
	venv/bin/python3 setup.py py2app

dev: venv
	venv/bin/python3 setup.py py2app -A

clean:
	rm -rf build/ dist/ venv/

run:
	echo open -n -W --stdin '$$TTY' --stdout '$$TTY' --stderr '$$TTY' dist/Nokoular.app

venv:
	/opt/homebrew/bin/python3.11 -m venv venv
	venv/bin/pip install -r requirements.txt
