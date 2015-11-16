# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

class MaterialSettingsPlugin(octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin):

    def get_settings_defaults(self):
        return dict(bed_temp="50",
        	print_temp="200")

    def get_template_vars(self):
        return dict(
        	bed_temp=self._settings.get(["bed_temp"]),
        	print_temp=self._settings.get(["print_temp"]))

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False),
        ]

    # def get_assets(self):
    #  	return dict(
    #      	js=["js/material_settings.js"]
    # )

    def set_bed_temp(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
    	if cmd and cmd[:10] == "M190 S50.5":
            t = self._settings.get(["bed_temp"])
            if t and t != "":
                cmd = "M190 S" + t
                return cmd
    	if cmd and cmd[:10] == "M140 S50.5":
            t = self._settings.get(["bed_temp"])
            if t and t != "":
                cmd = "M140 S" + t
                return cmd
    	if cmd and cmd[:11] == "M104 S200.5":
            t = self._settings.get(["print_temp"])
            if t and t != "":
                cmd = "M104 S" + t
                return cmd
    	if cmd and cmd[:11] == "M109 S200.5":
            t = self._settings.get(["print_temp"])
            if t and t != "":
                cmd = "M109 S" + t
                return cmd

__plugin_name__ = "Material Settings"
def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = MaterialSettingsPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.set_bed_temp,
    }