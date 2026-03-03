# Copyright (C) 2021 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# NOTE: Be CAREFUL with what you add here. It should be production ready.

FROM node:22-alpine AS frontend

WORKDIR /code/nodejs

COPY nodejs .
RUN npm ci \
  && npm run build
CMD npm run watch-sass


FROM python:3.12-slim AS os2borgerpc

LABEL org.opencontainers.image.title="OS2borgerPC" \
  org.opencontainers.image.vendor="Magenta ApS" \
  org.opencontainers.image.licenses="GPL" \
  org.opencontainers.image.url="https://www.magenta.dk/loesninger/os2borgerpc/"\
  org.opencontainers.image.source="https://github.com/magenta-aps/os2borgerpc-admin-site"

ENV PYTHONUNBUFFERED=1 \
  BPC_USER_CONFIG_PATH=/user-settings.ini \
  PYTHONPATH=/code/admin_site/:$PYTHONPATH \
  DJANGO_SETTINGS_MODULE=os2borgerpc_admin.settings \
  USER_ID="75030" \
  USER_NAME="bpc" \
  GROUP_ID="75030" \
  GROUP_NAME="bpc"

WORKDIR /code/
COPY admin_site/sys-requirements.txt sys-requirements.txt

# hadolint ignore=SC2046,DL3008
RUN set -ex \
  # Add our non-root group and user. Note: this is a system user/group, but have
  # UID/GID above the normal SYS_UID_MAX/SYS_GID_MAX of 999, but also above the
  # automatic ranges of UID_MAX/GID_MAX used by useradd/groupadd. See
  # `/etc/login.defs`. Hopefully there will be no conflicts with users of the
  # host system or users of other docker containers.
  && groupadd --gid $GROUP_ID --system $GROUP_NAME \
  && useradd --uid $USER_ID --no-log-init --system --gid $GROUP_NAME $USER_NAME \
  # Install system dependencies from file.
  && apt-get --assume-yes update \
  && apt-get --assume-yes install --no-install-recommends $(grep --only-matching '^[^#][[:alnum:].-]*' sys-requirements.txt) \
  # clean up after apt-get and man-pages
  && apt-get clean \
  && rm -rf "/var/lib/apt/lists/*"  "/tmp/*"  "/var/tmp/*"  "/usr/share/man/??"  "/usr/share/man/??_*" \
  # create folders at easily mountable paths for output from django
  && install --owner $USER_NAME --group $GROUP_NAME --directory /log /media

VOLUME /log
VOLUME /media

COPY VERSION /code/VERSION

# Install requirements.
COPY admin_site/requirements.txt /code/admin_site/requirements.txt
RUN pip3 install --no-cache-dir -r  admin_site/requirements.txt

# Install supercronic
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.25/supercronic-linux-amd64 \
  SUPERCRONIC=supercronic-linux-amd64 \
  SUPERCRONIC_SHA1SUM=642f4f5a2b67f3400b5ea71ff24f18c0a7d77d49

# hadolint ignore=DL4006
RUN curl -fsSLO "$SUPERCRONIC_URL" \
  && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
  && chmod +x "$SUPERCRONIC" \
  && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
  && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

# Copy backend code.
COPY README.md .
COPY LICENSE .
COPY docker ./docker
COPY admin_site ./admin_site

# Copy crontab-file
COPY crontab /crontab

WORKDIR /code/admin_site

# Copy frontend static files.
COPY --from=frontend \
  /code/nodejs/node_modules/material-symbols/material-symbols-outlined.woff2 \
  /frontend/fonts/
COPY --from=frontend \
  /code/nodejs/dist/css/bootstrap.* \
  /code/nodejs/node_modules/bootstrap-table/dist/bootstrap-table.min.css \
  /code/nodejs/node_modules/@highlightjs/cdn-assets/styles/foundation.min.css \
  /frontend/css/
COPY --from=frontend \
  /code/nodejs/node_modules/@highlightjs/cdn-assets/highlight.min.js \
  /code/nodejs/node_modules/htmx.org/dist/htmx.min.js \
  /code/nodejs/node_modules/sortablejs/Sortable.min.js \
  /code/nodejs/node_modules/bootstrap/dist/js/bootstrap.bundle.min.js* \
  /code/nodejs/node_modules/jquery/dist/jquery.min.js \
  /code/nodejs/node_modules/qrcodejs/qrcode.min.js \
  /code/nodejs/node_modules/bootstrap-table/dist/bootstrap-table.min.js \
  /code/nodejs/node_modules/bootstrap-table/dist/locale/bootstrap-table-da-DK.min.js \
  /frontend/js/

# Unfortunately, `collectstatic` requires all settings to be set. We include a
# set of insecure setting here for only this purpose. We make sure to delete it
# afterward. If `insecure-settings.ini` is found in any production image,
# consider it a bug. See `insecure-settings.ini` for a detailed explanation.
RUN set -ex \
  && BPC_USER_CONFIG_PATH=/code/docker/insecure-settings.ini python ./manage.py collectstatic --no-input --clear \
  && BPC_USER_CONFIG_PATH=/code/docker/insecure-settings.ini python ./manage.py compilemessages \
  && rm /code/docker/insecure-settings.ini

# Run the server as our non-root user on port 9999
USER $USER_NAME:$GROUP_NAME
EXPOSE 9999
ENTRYPOINT ["/code/docker/docker-entrypoint.sh"]
CMD ["gunicorn", \
  "--config", "/code/docker/gunicorn-settings.py", \
  "os2borgerpc_admin.wsgi"]
