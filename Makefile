build: clean venv
	venv/bin/python3 setup.py py2app

dev: venv
	venv/bin/python3 setup.py py2app -A

clean:
	rm -rf build/ dist/ venv/

run:
	dist/Nokoular.app/Contents/MacOS/Nokoular

venv:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
