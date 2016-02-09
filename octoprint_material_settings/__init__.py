# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask
import os

class MaterialSettingsPlugin(octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.BlueprintPlugin):

# StartupPlugin
    def on_after_startup(self):
        self._materials_file_path = os.path.join(self.get_plugin_data_folder(), "materials.yaml")
        self._materials_dict = None

# BluePrintPlugin (api requests)
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
        else:
            self._materials_dict = materials
            self.logMaterials()

    def _getMaterialsDict(self):
        result_dict = None
        if os.path.exists(self._materials_file_path):
            with open(self._materials_file_path, "r") as f:
                try:
                    import yaml
                    result_dict = yaml.safe_load(f)
                except:
                    self._logger.info("MSL: error loading materials file")
                else:
                    if not result_dict:
                        result_dict = dict()
        else: 
            result_dict = dict()
        self._materials_dict = result_dict
        self.logMaterials()
        return result_dict

    def logMaterials(self): 
        bTemp = self._materials_dict["bed_temp"]
        pTemp = self._materials_dict["print_temp"]
        self._logger.info("MSL: current print temp setting: %s" % pTemp)
        self._logger.info("MSL: current bed temp setting: %s" % bTemp)

# Gcode replacement
    def set_bed_temp(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        pTempKey = self._settings.get(["bed_temp"])
        bTempKey = self._settings.get(["print_temp"])

    	if cmd and cmd[:10] == "M190 S" + bTempKey:
            t = self._materials_dict.get(["bed_temp"])
            if t and t != "":
                cmd = "M190 S" + t
                return cmd
    	if cmd and cmd[:10] == "M140 S" + bTempKey:
            t = self._materials_dict.get(["bed_temp"])
            if t and t != "":
                cmd = "M140 S" + t
                return cmd
    	if cmd and cmd[:11] == "M104 S" + pTempKey:
            t = self._materials_dict.get(["print_temp"])
            if t and t != "":
                cmd = "M104 S" + t
                return cmd
    	if cmd and cmd[:11] == "M109 S" + pTempKey:
            t = self._materials_dict.get(["print_temp"])
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