# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from pprint import pprint
from octoprint.server import printer, NO_CONTENT
import flask, json
import os

class PrintQueuePlugin(octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.BlueprintPlugin,
    octoprint.plugin.EventHandlerPlugin):

    printqueue = []
    selected_file = ""
    uploads_dir = "/home/pi/.octoprint/uploads/"

# StartupPlugin
    def on_after_startup(self):
        self._print_queue_file_path = os.path.join(self.get_plugin_data_folder(), "print_queue.yaml")
        self._configuration_dict = None
        self._getConfigurationFile()

# BluePrintPlugin (api requests)
    @octoprint.plugin.BlueprintPlugin.route("/scriptget", methods=["GET"])
    def getMaterialsData(self):
        return flask.jsonify(self._getConfigurationFile())

    @octoprint.plugin.BlueprintPlugin.route("/scriptset", methods=["POST"])
    def setMaterialsData(self):
        config = self._getConfigurationFile()
        config["bed_clear_script"] = flask.request.values["bed_clear_script"];
        self._writeConfigurationFile(config)
        return flask.make_response("POST successful", 200)

    @octoprint.plugin.BlueprintPlugin.route("/addselectedfile", methods=["GET"])
    def addSelectedFile(self):
        self._logger.info("PQ: adding selected file: " + self.selected_file)
        self._printer.unselect_file()
        f = self.selected_file
        self.selected_file = ""
        return flask.jsonify(filename=f)

    @octoprint.plugin.BlueprintPlugin.route("/clearselectedfile", methods=["POST"])
    def clearSelectedFile(self):
        self._logger.info("PQ: clearing selected file")
        self._printer.unselect_file()
        self.selected_file = ""
        return flask.make_response("POST successful", 200)

    @octoprint.plugin.BlueprintPlugin.route("/printcontinuously", methods=["POST"])
    def printContinuously(self):
        self.printqueue = []
        for v in flask.request.form:
            j = json.loads(v)
            for p in j:
                self.printqueue += [p]

        f = self.uploads_dir + self.printqueue[0]
        self._logger.info("PQ: attempting to select and print file: " + f)
        self._printer.select_file(f, False, True)
        self.printqueue.pop(0)
        return flask.make_response("POST successful", 200)

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

    def _getConfigurationFile(self):
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
        if script_type == "gcode" and script_name == "afterPrintDone" and len(self.printqueue) > 0:
            prefix = self._configuration_dict["bed_clear_script"]
            postfix = None
            return prefix, postfix
        else:
            return None

    # Event Handling
    def on_event(self, event, payload):
        self._logger.info("on_event fired: " + event)
        if event == "FileSelected":
            self._plugin_manager.send_plugin_message(self._identifier, dict(message="file_selected",file=payload["path"]))
            self._logger.info(payload)
            self.selected_file = payload["path"]
        if event == "PrinterStateChanged":
            state = self._printer.get_state_id()
            self._logger.info("printer state: " + state)
            if state  == "OPERATIONAL" and len(self.printqueue) > 0:
                self._printer.select_file(self.uploads_dir + self.printqueue[0], False, True)
                self.printqueue.pop(0)
            if state == "OFFLINE" or state == "CANCELLING" or state == "CLOSED" or state == "ERROR" or state == "CLOSED_WITH_ERROR":
                self._logger.info("deleting print queue")
                self.printqueue = []

        return

__plugin_name__ = "Print Queue"
def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PrintQueuePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.scripts": __plugin_implementation__.print_completion_script,
    }
