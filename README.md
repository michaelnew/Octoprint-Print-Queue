# OctoPrint-Material-Settings

This plugin will look for specific heating commands sent to the printer (M104, M109, M190, and M140) and replace them with values that you've set from within Octoprint. This way you can change your bed and print temperatures without ever having to reslice.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/mikenew12/OctoPrint-Material-Settings/archive/master.zip

## Configuration

If you want a "heat the bed" command to be overridden, it should be set to exaclty 50.5 ˚C (i.e. M190 50.5 or M140 50.5). If you want a "heat up the hotend" command to be overriddedn, it should be set to 200.5 ˚C (i.e. M104 S200.5 or M109 S200.5). Any other temp will not be interfered with (trailing zeros are fine though, such as M140 50.50000).

So, for example, if your GCode has this at the beginning:

M140 S50.500
M109 S200.500

And under Settings->Material Settings in Octprint you've set the bed temp to be 62 and the print temp to be 205 (say you're printing PLA), then as those commands are sent to the printer they will become M140 S62 and M109 S205. You could then switch to ABS and change the bed temp to 100 and the print temp to 240 and print the obejct again without ever having to reslice.

Note that this will also work when setting temps in the GCode Scripts from within OctoPrint. So if you want to have an autolevel routine run in your "Before Print Starts" GCode, just put an M190 S50.5 before you autolevel, and your bed will heat up to whatever temp you've set in Material Settings.
