echo 'starting ve'
virtualenv ve
source ve/bin/activate
echo 'Starting webserver..'
pserve development.ini --reload &
sass --watch springboard/static/sass:springboard/static/css --style compressed 
kill %1
echo 'done'