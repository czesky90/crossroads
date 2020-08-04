FROM centos:8
RUN yum -y install dnf-plugins-core
RUN yum config-manager --set-enabled PowerTools
RUN yum -y install python38 git llvm libffi-devel zlib-devel bzip2-devel readline-devel \
  sqlite-devel ncurses-devel openssl-devel xz-devel libyaml-devel \
  redhat-rpm-config xz-devel && yum -y groupinstall 'Development Tools'

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 && source ~/.poetry/env
ENV PATH /root/.poetry/bin:$PATH

# Copy and setup project
ADD ./src /home/root/crossroads
ADD pyproject.toml /home/root/crossroads/pyproject.toml
WORKDIR /home/root/crossroads
RUN poetry install

ENTRYPOINT poetry run crossroads
