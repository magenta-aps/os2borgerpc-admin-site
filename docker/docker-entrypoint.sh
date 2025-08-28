#!/bin/bash
# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# NOTE: Be CAREFUL with what you add here. It should be production ready.

set -ex

./manage.py ensure_db_connection --wait 30

if [ "$SKIP_MIGRATIONS" != "yes" ]; then
  ./manage.py migrate
fi

exec "$@"
