FROM vaporio/python:3.6

RUN apt-get update -qy \
 && apt-get install -y \
      libsasl2-dev \
      graphviz \
      libjpeg-dev \
      libffi-dev \
      libxml2-dev \
      libxslt1-dev \
      libldap2-dev \
      libpq-dev \
      ttf-ubuntu-font-family \
 && rm -rf /var/lib/apt/lists/*

RUN pip install \
# gunicorn is used for launching netbox
      gunicorn \
# napalm is used for gathering information from network devices
      napalm \
# ruamel is used in startup_scripts
      ruamel.yaml \
# pinning django to the version required by netbox
# adding it here, to install the correct version of
# django-rq
      'Django>=2.2,<2.3' \
# django-rq is used for webhooks
      django-rq

ARG BRANCH
ARG ORG=vapor-ware


# Set image metadata (see: http://label-schema.org/rc1/)
ARG BUILD_VERSION
ARG BUILD_DATE
ARG VCS_REF

LABEL maintainer="Vapor IO"\
      org.label-schema.schema-version="1.0" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="vaporio/netbox" \
      org.label-schema.vcs-url="https://github.com/vapor-ware/netbox" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vendor="Vapor IO" \
      org.label-schema.version=$BUILD_VERSION

WORKDIR /tmp

# As the requirements don't change very often,
# and as they take some time to compile,
# we try to cache them very agressively.
ARG REQUIREMENTS_URL=https://raw.githubusercontent.com/$ORG/netbox/$BRANCH/requirements.txt
ADD ${REQUIREMENTS_URL} requirements.txt
RUN pip install -r requirements.txt

# Cache bust when the upstream branch changes:
# ADD will fetch the file and check if it has changed
# If not, Docker will use the existing build cache.
# If yes, Docker will bust the cache and run every build step from here on.
ARG REF_URL=https://api.github.com/repos/$ORG/netbox/contents?ref=$BRANCH
ADD ${REF_URL} version.json

WORKDIR /opt

ARG URL=https://github.com/$ORG/netbox/archive/$BRANCH.tar.gz
RUN wget -q -O - "${URL}" | tar xz \
  && mv netbox* netbox

COPY docker/configuration.docker.py /opt/netbox/netbox/netbox/configuration.py
COPY docker/configuration/gunicorn_config.py /etc/netbox/config/
COPY docker/nginx.conf /etc/netbox-nginx/nginx.conf
COPY docker/docker-entrypoint.sh /opt/netbox/docker-entrypoint.sh
COPY docker/startup_scripts/ /opt/netbox/startup_scripts/
COPY docker/initializers/ /opt/netbox/initializers/
COPY docker/configuration/configuration.py /etc/netbox/config/configuration.py

WORKDIR /opt/netbox/netbox

ENTRYPOINT [ "/opt/netbox/docker-entrypoint.sh" ]

CMD ["gunicorn", "-c /etc/netbox/config/gunicorn_config.py", "netbox.wsgi"]

LABEL SRC_URL="$URL"
