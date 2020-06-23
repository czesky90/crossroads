#!/bin/bash
yum -y update

amazon-linux-extras install -y nginx1.12

# Install all pyenv dependencies
yum -y install git llvm libffi-devel zlib-devel bzip2-devel readline-devel \
  sqlite-devel ncurses-devel openssl-devel lzma-sdk-devel libyaml-devel \
  redhat-rpm-config xz-devel
yum -y groupinstall 'Development Tools'


# Install pyenv
curl https://pyenv.run | bash
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.8.3

# Install poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
source ~/.poetry/env

# Download and setup project
git clone https://github.com/przypieczony/crossroads.git; cd crossroads
poetry install
poetry run crossroads




cat <<EOF > /usr/share/nginx/html/index.html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Crossroad</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</head>
<body>

<div class="jumbotron text-center">
  <h1>Crossroad company inc...</h1>
  <h2>..sends...</h2>
    <h3>...best wishes...</h3>
    <h4>...to...</h4>
</div>

<div class="container">
  <div class="jumbotron text-center">
      <h3>Henio!!!!!</h3>
      <img src="https://godanbialystok.pl/15510-thickbox_default/dekoracja-tortowa-happy-birthday-14-x-18-cm.jpg" alt="Happy">
      <p>Dużo zdrówka przesyłają papa Czesky i wujek Szyna :)</p>
  </div>
</div>

</body>
</html>

EOF

nginx
