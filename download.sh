
# bootstrap
mkdir -p targets/localweb/css/bootstrap/3.3.5
cd targets/localweb/css/bootstrap/3.3.5/
wget http://netdna.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css
cd ../../../../../

# html5shiv
mkdir -p targets/localweb/js/html5shiv/3.7.0
cd targets/localweb/js/html5shiv/3.7.0
wget https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js
cd ../../../../../

# respond.js
mkdir -p targets/localweb/js/respond.js/1.3.0
cd targets/localweb/js/respond.js/1.3.0
wget https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js
cd ../../../../../

# jquery 2.1.4 - actively used version
mkdir -p targets/localweb/js/jquery/2.1.4
cd targets/localweb/js/jquery/2.1.4/
wget https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js
cd ../../../../../

# jquery 3.1.1 - latest version (unused)
mkdir -p targets/localweb/js/jquery/3.1.1
cd targets/localweb/js/jquery/3.1.1
wget https://code.jquery.com/jquery-3.1.1.min.js
mv jquery-3.1.1.min.js jquery.min.js
cd ../../../../../

