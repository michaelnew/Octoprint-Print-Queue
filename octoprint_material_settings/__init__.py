# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask
import os

class MaterialSettingsPlugin(octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    # octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.BlueprintPlugin):

# StartupPlugin
    def on_after_startup(self):
        self._materials_file_path = os.path.join(self.get_plugin_data_folder(), "materials.yaml")
        # materials = self._getMaterialsDict()
        # materials["foo"] = "bar"
        # self._writeMaterialsFile(materials)
        # self._logger.info("MSL: materials file: %s" % materials["foo"])

# SimpleApiPlugin
    # def on_api_get(self, request):
    #     self._logger.info("MSL: get request was made")
    #     materials = self._getMaterialsDict()
    #     return flask.jsonify(materials)

    # def get_api_commands(self):
    #     return dict(
    #         command1=[],
    #         command2=["some_parameter"]
    #     )

    # def on_api_command(self, command, data):
    #     import flask
    #     self._logger.info("MSL: set_material called")
    #     if command == "command1":
    #         parameter = "unset"
    #         if "parameter" in data:
    #             parameter = "set"
    #         self._logger.info("command1 called, parameter is {parameter}".format(**locals()))
    #     elif command == "command2":
    #         self._logger.info("command2 called, some_parameter is {some_parameter}".format(**data))


    @octoprint.plugin.BlueprintPlugin.route("/materialget", methods=["GET"])
    def getMaterialsData(self):
        for x in flask.request.values:
            self._logger.info("MSL: get request value: %s" % x)

        materials = self._getMaterialsDict()
        return flask.jsonify(materials)

    @octoprint.plugin.BlueprintPlugin.route("/materialset", methods=["POST"])
    def setMaterialsData(self):
        materials = self._getMaterialsDict()
        materials["bed_temp"] = flask.request.values["bed_temp"];
        materials["print_temp"] = flask.request.values["print_temp"];
        self._writeMaterialsFile(materials)
        
        for x in flask.request.values:
            self._logger.info("MSL: post request value: %s" % x)
        return flask.make_response("POST successful", 200)

# SettingsPlugin
    def get_settings_defaults(self):
        return dict(bed_temp="50",
        	print_temp="200")

# TemplatePlugin
    def get_template_vars(self):
        return dict(
        	bed_temp=self._settings.get(["bed_temp"]),
        	print_temp=self._settings.get(["print_temp"]))

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False),
        ]

# AssetPlugin
    def get_assets(self):
     	return dict(
         	js=["js/material_settings.js"]
    )

# Data Persistence
    def _writeMaterialsFile(self, materials):
        try:
            import yaml
            from octoprint.util import atomic_write
            with atomic_write(self._materials_file_path) as f:
                yaml.safe_dump(materials, stream=f, default_flow_style=False, indent="  ", allow_unicode=True)
        except:
            self._logger.info("MSL: error writing materials file")

    def _getMaterialsDict(self):
        if os.path.exists(self._materials_file_path):
            with open(self._materials_file_path, "r") as f:
                try:
                    import yaml
                    materials_dict = yaml.safe_load(f)
                except:
                    self._logger.info("MSL: error loading materials file")
                else:
                    if not materials_dict:
                        materials_dict = dict()
                    return materials_dict
        return dict()

# Gcode replacement
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