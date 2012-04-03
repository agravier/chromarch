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

import setuptools
from setuptools import setup
from setuptools.command.install import install as _install
import os

_conf_monitor_dir = "chrome_conf_files_monitor"
_conf_monitor_filename = "powermanconf_monitor.sh"

_message="""\
 - - - - - -

Now, you need to:

1) copy the file
   """ + \
os.path.join(setuptools.distutils.core.sys.prefix, _conf_monitor_dir, _conf_monitor_filename) + \
"""
   to the /usr/local/bin directory of Chrome OS.

2) add the following call to your .xinitrc in the chroot:

   chrootxmon &

 - - - - - -"""

class install(_install):
    def run(self):
        _install.run(self)
        print _message

setup(
    cmdclass={'install': install},
    name = 'chrootxmon',
    version = '0.1',
    description = 'Modifies Chrome OS power manager conf files according to user activity in chroot.',
    long_description = """
    This script is the "activity monitoring" half of a pair of scripts
    used to adjust the power saving policies of Chrome OS to the user
    activity in a X11 server running in a chroot. The overall program
    is split in two components communicating indirectly by modifying
    chrome OS power manager configuration directory. This script is
    the part that monitors user activity in X11 in the chroot. It
    modifies the Chrome OS power manager configuration files. While
    the user is active in the chrooted X11, the X11 program increases
    the "dimming", "off" and "suspend" timeouts to (configurable) high
    values to prevent the screen to dim or turn off and the computer
    to suspend. When the user has been inactive in the chroot X11 for
    a configurable duration, the X11 watchdog restores the power
    manager configuration files to values that allow screen
    dimming/off and computer suspend.
    
    To work properly, this script requires: 

    1) write access to the (configurable) directory of the host Chrome
    OS where the power manager reads screen dimming values.

    2) the second half of the program to be running (Chrome OS script
    that monitors configuration changes and restarts the power manager).

    """,
    author = 'Alexandre Gravier',
    author_email = 'al.gravier@gmail.com',
    url = 'http://github.com/agravier/chromarch/',
    license = 'GNU General Public License (GPL) v3 and later',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: X11 Applications',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Monitoring'],

    platforms = ['X11'],
    packages = ['chrootxmon'],
    include_package_data=True,
    data_files = [
        (_conf_monitor_dir, [_conf_monitor_filename])],
    entry_points = {
        "console_scripts" : [
            "chrootxmon = chrootxmon.chrootxmon:main",],},
    install_requires=['actmon'],
    )

