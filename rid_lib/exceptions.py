class RidException(Exception):
    pass

class InvalidRidFormatError(RidException):
    pass

class InvalidReferenceFormatError(RidException):
    pass

class UndefinedMeansError(RidException):
    pass

class TypeImplementationError(RidException):
    pass 