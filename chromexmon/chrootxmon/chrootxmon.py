#!/bin/env python2

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

import os
import syslog
import time
import actmon

POWERMAN_CONF_DIR = "/media/chromeos/var/lib/power_manager/"
CHROME_MONITOR = "powermanconf_monitor.sh"

# Number of seconds after which the user is considered inactive in the
# chroot.
X_INACTIVITY_TRIGGER = 5 * 60

# The values that get written to the powermanager conf files after
# X_INACTIVITY_TRIGGER seconds of inactivity in the chroot. The unit is
# one second.
SCREEN_DIM_DELAY_ON_BATTERY = 90
SCREEN_OFF_DELAY_ON_BATTERY = 180
SUSPEND_DELAY_ON_BATTERY = 600
SCREEN_DIM_DELAY_ON_MAINS = 180
SCREEN_OFF_DELAY_ON_MAINS = 300
SUSPEND_DELAY_ON_MAINS = 1200

ACTIVITY_WAIT_SLEEP = 1

# The value that gets written to avoid spurious power saving when in the chroot
MAX_DIM_TIMEOUT = 99999
MAX_OFF_TIMEOUT = 999999
MAX_SUSPEND_TIMEOUT = 9999999

def fatal(errmsg, errno):
    syslog.openlog(ident="chrootxmon",
                   logoption=syslog.LOG_PERROR,
                   facility=syslog.LOG_USER)
    syslog.syslog(errmsg)
    syslog.closelog()
    exit(errno)


def check_chrome_monitor():
    "Verifies if the program monitoring " + POWERMAN_CONF_DIR + " is running."
    pids= [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            pcmdline = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
            if CHROME_MONITOR in pcmdline:
                return True
        except IOError:
            pass
    return False


def checkenv():
    if not os.access(POWERMAN_CONF_DIR, os.W_OK):
        fatal("The activity monitor could not write to " + POWERMAN_CONF_DIR, 2)
    if not check_chrome_monitor():
        fatal("The activity monitor could not find " + CHROME_MONITOR + " running", 3)


def write_plugged_timeouts(screen_dim, screen_off, computer_suspend):
    """Writes the timeouts (in seconds) for screen dimming, screen off
    and computer suspend when the computer is on mains to the Chrome
    OS power manager configuration files."""
    write_value(os.path.join(POWERMAN_CONF_DIR, "plugged_dim_ms"),
                screen_dim * 1000)
    write_value(os.path.join(POWERMAN_CONF_DIR, "plugged_off_ms"),
                screen_off * 1000)
    write_value(os.path.join(POWERMAN_CONF_DIR, "plugged_suspend_ms"),
                computer_suspend * 1000)


def write_unplugged_timeouts(screen_dim, screen_off, computer_suspend):
    """Writes the timeouts (in seconds) for screen dimming, screen off
    and computer suspend when the computer is on battery to the Chrome
    OS power manager configuration files."""
    write_value(os.path.join(POWERMAN_CONF_DIR, "unplugged_dim_ms"),
                screen_dim * 1000)
    write_value(os.path.join(POWERMAN_CONF_DIR, "unplugged_off_ms"),
                screen_off * 1000)
    write_value(os.path.join(POWERMAN_CONF_DIR, "unplugged_suspend_ms"),
                computer_suspend * 1000)


def write_timeouts(idle):
    if idle:
        write_plugged_timeouts(SCREEN_DIM_DELAY_ON_MAINS,
                               SCREEN_OFF_DELAY_ON_MAINS, 
                               SUSPEND_DELAY_ON_MAINS)
        write_unplugged_timeouts(SCREEN_DIM_DELAY_ON_BATTERY, 
                                 SCREEN_OFF_DELAY_ON_BATTERY, 
                                 SUSPEND_DELAY_ON_BATTERY)
    else:
        write_plugged_timeouts(MAX_DIM_TIMEOUT, 
                               MAX_OFF_TIMEOUT, 
                               MAX_SUSPEND_TIMEOUT)
        write_unplugged_timeouts(MAX_DIM_TIMEOUT, 
                                 MAX_OFF_TIMEOUT, 
                                 MAX_SUSPEND_TIMEOUT)


def write_value(filename, value):
    with open(filename, "w") as f:
        f.write(str(value))


def get_seconds_idle():
    return actmon.get_idle_time() / 1000


def wait_for_idle():
    seconds_idle = get_seconds_idle()
    while seconds_idle < X_INACTIVITY_TRIGGER:
        time.sleep(X_INACTIVITY_TRIGGER - seconds_idle + 1)
        seconds_idle = get_seconds_idle()


def wait_for_activity():
    previous_seconds_idle = 0
    seconds_idle = get_seconds_idle()
    while seconds_idle >= previous_seconds_idle:
        time.sleep(ACTIVITY_WAIT_SLEEP)
        previous_seconds_idle = seconds_idle
        seconds_idle = get_seconds_idle()


def main():
    checkenv()
    while True:
        write_timeouts(idle=False)
        wait_for_idle()
        write_timeouts(idle=True)
        wait_for_activity()


if __name__ == "__main__":
    main()
