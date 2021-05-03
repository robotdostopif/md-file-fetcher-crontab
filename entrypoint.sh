#!/bin/bash
printenv | sed 's/^\(.*\)$/export \1/g' >> /etc/profile.d/rails_env.sh
cron -f