
prepare: fetch diff

status:
	git status

push:
	git push origin master

pull:
	git pull origin master

fetch:
	git fetch origin

merge:
	git merge origin/master

diff:
	git diff master origin/master

fulltest:
	pytest

test:
	pytest --picked

testcoverage:
	pytest --cov=suapp --cov-report=html

testannotate:
	pytest --annotate-output=htmlcov/annotate.json

testmonkey:
	pytest --monkeytype-output=./monkeytype.sqlite3

webtargets:
	suapp/targets/.only/generate.sh
