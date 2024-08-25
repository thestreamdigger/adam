#!/bin/bash
#
# moOde audio player (C) 2014 Tim Curtis
# http://moodeaudio.org
#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This Program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Allo Piano 2.1 Hi-Fi DAC
DUALMODE=$(awk -F"'" '/Item0/ {print $2; count++; if (count==1) exit}' <(amixer -c 0 sget "Dual Mode"))
SUBWMODE=$(awk -F"'" '/Item0/ {print $2; count++; if (count==1) exit}' <(amixer -c 0 sget "Subwoofer mode"))
SUBWVOL=$(awk -F"[][]" '/%/ {print $2; count++; if (count==1) exit}' <(amixer -c 0 sget "Subwoofer"))
SUBXOVER=$(awk -F"'" '/Item0/ {print $2; count++; if (count==1) exit}' <(amixer -c 0 sget "Lowpass"))
MASTERVOL=$(awk -F"[][]" '/%/ {print $2; count++; if (count==1) exit}' <(amixer -c 0 sget "Master"))

echo "Dual mode: "$DUALMODE
echo "Subw mode: "$SUBWMODE
echo "Sub xover: "$SUBXOVER
echo "Sub level: "$SUBWVOL
echo "Mstr levl: "$MASTERVOL
