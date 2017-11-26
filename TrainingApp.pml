<?xml version="1.0" encoding="UTF-8" ?>
<Package name="TrainingApp" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="basicChannelDialog" src="basicChannelDialog/basicChannelDialog.dlg" />
        <Dialog name="dialog" src="dialog/dialog.dlg" />
    </Dialogs>
    <Resources>
        <File name="demo-service" src="demo-service.py" />
        <File name="icon" src="icon.png" />
    </Resources>
    <Topics>
        <Topic name="dialog_enu" src="dialog/dialog_enu.top" topicName="dialog" language="en_US" />
        <Topic name="dialog_fif" src="dialog/dialog_fif.top" topicName="dialog" language="fi_FI" />
        <Topic name="basicChannelDialog_enu" src="basicChannelDialog/basicChannelDialog_enu.top" topicName="basicChannelDialog" language="en_US" />
    </Topics>
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
