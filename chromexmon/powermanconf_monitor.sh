#!/bin/env bash

# This file is part of chromexmon.

# chromexmon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# chromexmon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with chromexmon.  If not, see <http://www.gnu.org/licenses/>.

# Author: Alexandre Gravier (al.gravier@gmail.com)

if [ "$(id -u)" != "0" ] ; then
  echo $0 must be run as root.
  exit 1
fi

POWERMAN_CONF_D="/var/lib/power_manager"

MONITORED_FILES="$POWERMAN_CONF_D/{plugged_dim_ms,unplugged_dim_ms,plugged_off_ms,unplugged_off_ms,plugged_suspend_ms,unplugged_suspend_ms}"

# file from which to take the value used to determine if the
# chrootxmon considers the user idle or active
STATUS_FILE="$POWERMAN_CONF_D/unplugged_dim_ms"
STATUS_THRESHOLD=600000 # 10 minutes

CHECK_INTERVAL=10

check() {
  files="$1"
  dt="$2"
  sum1=`eval "ls -la $files" | md5sum | awk '{print $1}'`
  sum2=$sum1
  sleepret=0
  while [[ $sleepret -eq 0 && $sum1 = $sum2 ]]; do
    sleep $dt
    sleepret=$?
    sum2=`eval "ls -la $files" | md5sum | awk '{print $1}'`
  done
  return $sleepret
}

non_zero() {
  if (( $1 > 0 )); then
    return $1
  fi
  return $2
}

get_b() {
  return `backlight-tool -get_brightness`
}

set_b() {
  eval "backlight-tool -set_brightness $1"
}

while eval "ls $MONITORED_FILES" > /dev/null 2>&1; [[ $? -eq 2 ]]; do
  # Waiting for all conf files.
  sleep $CHECK_INTERVAL
done

get_b
latest_brightness=$?

# Conf files are there, now starting the monitoring loop

while check $MONITORED_FILES $CHECK_INTERVAL; do
  get_b
  non_zero $? $latest_brightness
  latest_brightness=$?
  # $latest_brightness is the latest non zero brightness
  initctl restart powerd
  if [[ `cat $STATUS_FILE` -gt $STATUS_THRESHOLD ]]; then
    # when active in the chroot, resteting brightness to
    # $latest_brightness and checking every 10 seconds
    set_b $latest_brightness
    CHECK_INTERVAL=10
  else
    # when inactive, checking for activity every ONE second
    CHECK_INTERVAL=1
  fi
done