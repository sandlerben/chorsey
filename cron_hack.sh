#!/bin/bash

# This is a total hack based on the limitations of the heroku scheduler.
# See https://stackoverflow.com/questions/9835095/how-can-i-schedule-a-weekly-job-on-heroku/18565294#18565294
if [ "$(date +%u)" = 6 ]; then python cron.py; fi
