class CheckPointKnowledgeError(Exception):
    pass

class CheckPointCorruptedHeadersError(Exception):
    pass

class CheckPointUnknownVerbError(Exception):
    pass

class CheckPointUnknownRequestDataTypeError(Exception):
    pass

class CheckPointInsufficientCreds(Exception):
    pass

class CheckPointParamsTemplateError(Exception):
    pass

class CheckPointParamsInputError(Exception):
    pass

class CheckPointAPIResponseParsingError(Exception):
    pass

class CheckPointObjectsMergingError(Exception):
    pass

class CheckPointAndroidMasterAuthError(Exception):
    pass

class CheckPointAndroidAppOAuth2Error(Exception):
    pass

class CheckPointOSIDAuthError(Exception):
    pass

class CheckPointCredsNotLoaded(Exception):
    pass

class CheckPointInvalidSession(Exception):
    pass

class CheckPointNotAuthenticated(Exception):
    pass

class CheckPointInvalidTarget(Exception):
    pass

class CheckPointLoginError(Exception):
    pass