class FileParsingError(Exception):
    """
    Base exception for other file parsing exceptions
    """
    pass


class NoOdooTranslationFileHeader(FileParsingError):
    """
    This error will be raised if not any header is found in odoo File
    """
    pass


class NoFileForProjectError(FileParsingError):
    """
    This error will be raised if there is not translation file for a project
    """
    pass


class NoTranslationFoundInFileError(FileParsingError):
    """
    This error will be raised if there is 0 translation block found in file
    """
    pass


class TranslationBlockStructureNotGoodError(FileParsingError):
    """
    This error will be raised if the structure of a translation block is not good
    (for example : length of block is below 4)
    """
    pass
