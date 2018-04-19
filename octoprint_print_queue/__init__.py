# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from pprint import pprint
from octoprint.server import printer, NO_CONTENT
import flask
import os

class PrintQueuePlugin(octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.BlueprintPlugin,
    octoprint.plugin.EventHandlerPlugin):

    printqueue = 0

# StartupPlugin
    def on_after_startup(self):
        self._print_queue_file_path = os.path.join(self.get_plugin_data_folder(), "print_queue.yaml")
        self._configuration_dict = None
        self._getMaterialsDict()

# BluePrintPlugin (api requests)
    @octoprint.plugin.BlueprintPlugin.route("/scriptget", methods=["GET"])
    def getMaterialsData(self):
        materials = self._getMaterialsDict()
        return flask.jsonify(materials)

    @octoprint.plugin.BlueprintPlugin.route("/scriptset", methods=["POST"])
    def setMaterialsData(self):
        materials = self._getMaterialsDict()
        materials["bed_clear_script"] = flask.request.values["bed_clear_script"];
        self._writeConfigurationFile(materials)
        return flask.make_response("POST successful", 200)

    @octoprint.plugin.BlueprintPlugin.route("/runtest", methods=["POST"])
    def runTest(self):
        self._logger.info("PQ: successfully called test method")
        # octoprint.printer.start_print()
        self._logger.info("PQ: octoprint" + ', '.join(dir(octoprint)))
        self._logger.info("PQ: octoprint.printer " + ', '.join(dir(octoprint.printer)))
        self._logger.info("PQ: self " + ', '.join(dir(self)))
        # self._printer.start_print()
        return flask.make_response("POST successful", 200)

    @octoprint.plugin.BlueprintPlugin.route("/printcontinuously", methods=["POST"])
    def printContinuously(self):
        self._logger.info("PQ: successfully called print continuously method")
        self.printqueue = int(flask.request.values["amount"])
        self._logger.info("PQ: printing copies: " + str(self.printqueue))
        if self.printqueue > 0:
            self._printer.start_print()
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
            js=["js/print_queue.js"]
    )

# Data Persistence
    def _writeConfigurationFile(self, config):
        try:
            import yaml
            from octoprint.util import atomic_write
            with atomic_write(self._print_queue_file_path) as f:
                yaml.safe_dump(config, stream=f, default_flow_style=False, indent="  ", allow_unicode=True)
        except:
            self._logger.info("PQ: error writing configuration file")
        else:
            self._configuration_dict = config

    def _getMaterialsDict(self):
        result_dict = None
        if os.path.exists(self._print_queue_file_path):
            with open(self._print_queue_file_path, "r") as f:
                try:
                    import yaml
                    result_dict = yaml.safe_load(f)
                except:
                    self._logger.info("PQ: error loading configuration file")
                else:
                    if not result_dict:
                        result_dict = dict()
        else: 
            result_dict = dict()
        self._configuration_dict = result_dict
        return result_dict

    def print_completion_script(self, comm, script_type, script_name, *args, **kwargs):
        if script_type == "gcode" and script_name == "afterPrintDone" and self.printqueue > 0:
            prefix = self._configuration_dict["bed_clear_script"]
            postfix = None
            return prefix, postfix
        else:
            return None

    # Event Handling
    def on_event(self, event, payload):
        self._logger.info("on_event fired: " + event)
        if event == "FileSelected":
            self._logger.info(payload)
        if event == "PrinterStateChanged": 
            if self._printer.get_state_string() == "Operational" and self.printqueue > 0:
                self._logger.info("attempting to start print")
                self.printqueue -= 1
                #self._printer.select_file(path="test_scripts/single_move_test_no_extrusion.gcode", sd=True, printAfterSelect=True)
                self._printer.start_print()

__plugin_name__ = "Print Queue"
def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PrintQueuePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.scripts": __plugin_implementation__.print_completion_script,
    }
