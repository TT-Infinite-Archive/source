from toontown.toonbase.ToontownGlobals import AnimPropType

def calcPropType(fullString: str) -> AnimPropType:
    """
    Return a given prop type based on the full name of the DNA prop node
    """
    if 'hydrant' in fullString:
        propType = AnimPropType.HYDRANT
    elif 'trashcan' in fullString:
        propType = AnimPropType.TRASHCAN
    elif 'mailbox' in fullString:
        propType = AnimPropType.MAILBOX
    else:
        propType = AnimPropType.UNKNOWN

    return propType
