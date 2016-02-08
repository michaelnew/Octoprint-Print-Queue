/*
 * View model for OctoPrint-Material-Settings
 *
 * Author: Michael New
 * License: AGPLv3
 */
$(function() {
    function Material_settingsViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[0];

        self.bedTemp = ko.observable();
        self.printTemp = ko.observable();

        self.setBedTemp = function() {
            // self.bedTemp(self.newBedTemp());
            // self.settings.settings.plugins.material_settings.bed_temp(self.bedTemp);
            var payload = {
                "bed_temp": self.bedTemp(),
            };
            OctoPrint.tab_plugin_material_settings.saveConfig(payload)
                .done(self.fromResponse);
        };


        self.setPrintTemp = function() {
            // self.settings.settings.plugins.material_settings.print_temp(self.printTemp);
            self.printTemp("100");
        };

        self.onBeforeBinding = function() {
            // self.bedTemp(self.settings.settings.plugins.material_settings.bed_temp());
            // self.printTemp(self.settings.settings.plugins.material_settings.print_temp());
            self.bedTemp();
            self.printTemp();
        };

        self.fromResponse = function(response) {
            var config = response.config;
            if (config === undefined) return;
        };

        self.requestData = function() {
            OctoPrint.tab_plugin_material_settings.get()
                .done(self.fromResponse);
        };

        self.onStartup = function() {
            self.requestData();
        };
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        Material_settingsViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        ["settingsViewModel"],

        // e.g. #settings_plugin_material_settings, #tab_plugin_material_settings, ...
        // [ "#tab_plugin_material_settings", "#settings_plugin_material_settings" ]
        ["#tab_plugin_material_settings"]
    ]);
});
