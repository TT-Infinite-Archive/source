Models = {
    # Event Page stuff
    'phase_4/models/parties/schtickerbookHostingGUI',
    'phase_4/models/parties/schtickerbookInvitationGUI',
    'phase_4/models/parties/eventSignIcons',
    'phase_4/models/parties/partyDecorations',
    # Common Buttons
    'phase_3/models/gui/chat_button_gui',
    'phase_3.5/models/gui/friendslist_gui',
    'phase_3.5/models/gui/inventory_gui',
    # Guild
    'phase_9/models/gui/guild-remove',
    'phase_9/models/gui/guild-top'
}


def preload():
    for model in Models:
        preloader.loadModel(model)
