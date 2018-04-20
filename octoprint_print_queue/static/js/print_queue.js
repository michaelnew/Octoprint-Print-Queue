/*
 * View model for OctoPrint-Print-Queue
 *
 * Author: Michael New
 * License: AGPLv3
 */
$(function() {
    function PrintQueueViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.bedClearScript = ko.observable();
        self.fileName = ko.observable();
	self.queuedPrints = ko.observableArray([]);

        self.printContinuously = function() {
            if (parseInt(self.printNumber()) > 0) {
                $.ajax({
                    url: "plugin/print_queue/printcontinuously",
                    type: "POST",
                    dataType: "json",
                    headers: {
                        "X-Api-Key":UI_API_KEY,
                    },
                    data: {
			prints: self.queuedPrints,
                    },
                    success: self.postResponse
                });
            }
        }

        self.changePrintNumber = function(data) {
	    console.log(data);
        }

        self.addSelectedFile = function() {
	    $.ajax({
	        url: "plugin/print_queue/addselectedfile",
	        type: "GET",
	        dataType: "json",
	        headers: {
		    "X-Api-Key":UI_API_KEY,
	        },
		success: self.addFileResponse
	    });
        }

        self.addFileResponse = function(data) {
            console.log('PQ: add file success');
            console.log(data);
	    let f = data["filename"]
	    if (f) {
                self.queuedPrints.push({fileName: f, printNumber: 1})
	    }
        };

        self.requestData = function() {
            $.ajax({
                url: "plugin/print_queue/scriptget",
                type: "GET",
                dataType: "json",
                success: self.fromResponse
            });
        };

        self.postData = function(bScript) 
        {
            $.ajax({
                url: "plugin/print_queue/scriptset",
                type: "POST",
                dataType: "json",
                headers: {
                    "X-Api-Key":UI_API_KEY,
                },
                data: {
                        bed_clear_script: bScript
                    },
                success: self.postResponse
            });
        }

        self.postResponse = function() {
            console.log('MSL: post success');
        };

        self.fromResponse = function(data) {
            self.bedClearScript(data["bed_clear_script"])
            console.log('Callback - data: ' + data["bed_clear_script"]);
        };

        self.update = function() {
            console.log('posting bed clear script: ' + self.bedClearScript());
            self.postData(self.bedClearScript());
        }


        self.onBeforeBinding = function() {
            // self.newUrl(self.settings.settings.plugins.helloworld.url());
            // self.goToUrl();
            self.requestData();
            // self.testBedTemp = ko.observable(self.settings.settings.plugins.material_settings.bed_temp());
        }
    }

    // This is how our plugin registers itself with the application, by adding some configuration
    // information to the global variable OCTOPRINT_VIEWMODELS
    OCTOPRINT_VIEWMODELS.push([
        // This is the constructor to call for instantiating the plugin
        PrintQueueViewModel,

        // This is a list of dependencies to inject into the plugin, the order which you request
        // here is the order in which the dependencies will be injected into your view model upon
        // instantiation via the parameters argument
        ["settingsViewModel"],

        // Finally, this is the list of selectors for all elements we want this view model to be bound to.
        ["#tab_plugin_print_queue"]
    ]);
});
