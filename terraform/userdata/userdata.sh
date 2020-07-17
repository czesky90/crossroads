#!/bin/bash
yum install -y git
amazon-linux-extras install -y docker
curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
PATH=$PATH:/usr/local/bin/

service docker start
# TODO maybe there is an option to not hardcoe region
$(aws ecr get-login --no-include-email --region eu-central-1)

# cat <<EOF > /usr/share/nginx/html/index.html
# <!DOCTYPE html>
# <html lang="en">
# <head>
#   <title>Crossroad</title>
#   <meta charset="utf-8">
#   <meta name="viewport" content="width=device-width, initial-scale=1">
#   <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
#   <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
#   <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
# </head>
# <body>
#
# <div class="jumbotron text-center">
#   <h1>Crossroad company inc...</h1>
#   <h2>..sends...</h2>
#     <h3>...best wishes...</h3>
#     <h4>...to...</h4>
# </div>
#
# <div class="container">
#   <div class="jumbotron text-center">
#       <h3>Henio!!!!!</h3>
#       <img src="https://godanbialystok.pl/15510-thickbox_default/dekoracja-tortowa-happy-birthday-14-x-18-cm.jpg" alt="Happy">
#       <p>Dużo zdrówka przesyłają papa Czesky i wujek Szyna :)</p>
#   </div>
# </div>
#
# </body>
# </html>
#
# EOF
#
# nginx



git clone https://github.com/przypieczony/crossroads.git; cd crossroads
git checkout flask

# Download credentials and source them
aws s3 cp s3://crossroad-api-keys/api_keys api_keys
source api_keys
rm -f api_keys

# Run app
cd docker
docker-compose up
