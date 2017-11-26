#!/usr/bin/env python
import qi
import sys
import os


class DemoService:
    services_connected = None
    connected_signals = []
    

    def __init__(self, application):
        # Getting a session that will be reused everywhere
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        # Getting a logger. Logs will be in /var/log/naoqi/servicemanager/{application id}.{service name}
        self.logger = qi.Logger(self.service_name)
        
        # Do some initializations before the service is registered to NAOqi
        self.logger.info("Initializing...")
        self.connect_services()
        self.logger.info("Initialized!")
        self.add_memory_subscriber("DemoService/exit", self.exit_service)
        self.logger.info("Service started")

    @qi.nobind
    def exit_service(self,value):
        self.logger.info("Calling stop service...")
        self.stop_service(value)

    @qi.nobind
    def start_service(self):
        self.logger.info("Starting service...")
        self.load_dialog()
        # do something when the service starts
        self.logger.info("Started!")

    @qi.nobind
    def stop_service(self, value):
        # probably useless, unless one method needs to stop the service from inside.
        # external naoqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.application.stop()
        self.logger.info("Stopped!")

    @qi.nobind
    def connect_services(self):
        # connect all services required by your module
        # done in async way over 30s,
        # so it works even if other services are not yet ready when you start your module
        # this is required when the service is autorun as it may start before other modules...
        self.logger.info('Connecting services...')
        self.services_connected = qi.Promise()
        services_connected_fut = self.services_connected.future()

        def get_services():
            try:
                self.memory = self.session.service('ALMemory')
                self.dialog = self.session.service('ALDialog')
                # connect other services if needed...
                self.logger.info('All services are now connected')
                self.services_connected.setValue(True)
            except RuntimeError as e:
                self.logger.warning('Still missing some service:\n {}'.format(e))

        get_services_task = qi.PeriodicTask()
        get_services_task.setCallback(get_services)
        get_services_task.setUsPeriod(int(2*1000000))  # check every 2s
        get_services_task.start(True)
        try:
            services_connected_fut.value(30*1000)  # timeout = 30s
            get_services_task.stop()
        except RuntimeError:
            get_services_task.stop()
            self.logger.error('Failed to reach all services after 30 seconds')
            raise RuntimeError


    ### Utility functions ###

    @qi.nobind
    def load_dialog(self):
        self.logger.info("Loading dialog")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        lang = self.dialog.getLanguage()
        self.logger.info(lang)
        if (lang == 'English'):
            topic_path = os.path.realpath(os.path.join(dir_path, "..", "trainingapp/dialog", "dialog_enu.top"))
        else:
            topic_path = os.path.realpath(os.path.join(dir_path, "..", "trainingapp/dialog", "dialog_fif.top"))
        self.logger.info(topic_path)
        try:
            self.loadedTopic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loadedTopic)
            self.dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded...")
            
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))

    @qi.nobind
    def unload_dialog(self):
        # if needed, here is how to unload a dialog from Python
        self.logger.info("Unloading dialog")
        try:
            #dialog = self.session.service("ALDialog")
            self.dialog.unsubscribe(self.service_name)
            self.dialog.deactivateTopic(self.loadedTopic)
            self.dialog.unloadTopic(self.loadedTopic)
            self.logger.info("Dialog unloaded.")
        except Exception, e:
            self.logger.info("Error while unloading dialog: {}".format(e))

    @qi.nobind
    def add_memory_subscriber(self, event, callback):
        # add memory subscriber utility function
        self.logger.info("Subscribing to {}".format(event))
        try:
            self.memory.declareEvent(event)
            sub = self.memory.subscriber(event)
            con = sub.signal.connect(callback)
            self.connected_signals.append([sub, con])
        except Exception, e:
            self.logger.info("Error while subscribing: {}".format(e))

    @qi.nobind
    def remove_memory_subscribers(self):
        # remove memory subscribers utility function
        self.logger.info("unsubscribing to all signals...")
        for sub, con in self.connected_signals:
            try:
                sub.signal.disconnect(con)
            except Exception, e:
                self.logger.info("Error while unsubscribing: {}".format(e))

    @qi.nobind
    def show_tablet(self):
        # how to load and display the webpage on the tablet
        dir_path = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
        folder = os.path.basename(dir_path)
        self.logger.info("Loading tablet page for app: {}".format(folder))
        try:
            ts = self.session.service("ALTabletService")
            ts.loadApplication(folder)
            ts.showWebview()
        except Exception, e:
            self.logger.info("Error while loading tablet: {}".format(e))

    @qi.nobind
    def on_disable_movements(self, useless_value):
        # if needed, here is how to disable movements for a short time
        try:
            self.session.service("ALBasicAwareness").setEnabled(False)
            # ALMotion.setBreathEnabled("Body", 0)
            self.session.service("ALMotion").setIdlePostureEnabled("Head", 1)
            # ALBackgroundMovement.setEnabled(0)
        except Exception, e:
            self.logger.info("Error while disabling movements: {}".format(e))

    @qi.nobind
    def on_enable_movements(self, useless_value):
        # if needed, enable movements back
        try:
            self.session.service("ALBasicAwareness").setEnabled(True)
            # ALMotion.setBreathEnabled("Body", 0)
            self.session.service("ALMotion").setIdlePostureEnabled("Head", 0)
            # ALBackgroundMovement.setEnabled(0)
        except Exception, e:
            self.logger.info("Error while enabling movements: {}".format(e))

    ### ################# ###

    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")
        self.unload_dialog()
        # do something
        self.remove_memory_subscribers()
        self.logger.info("End!")

if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python my_super_service.py --qi-url 10.0.137.169
    app = qi.Application(sys.argv)
    app.start()
    service_instance = DemoService(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_service()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)
