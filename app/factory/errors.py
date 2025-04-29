"""
Error classes for bot factory
"""


class FactoryStartArgumentError(Exception):
    def __init__(self, code: int, error_arg: str = "", message: str = ""):
        """
        Exception raised for errors in the input factory arguments

        Args:
            code: code error
            error_arg: arg which raise error
            message: explanation of the error

        """
        self.message = message
        if not message:
            match code:
                case 1:
                    self.message = "Wrong argument format"
                case 2:
                    self.message = "Function argument set earlier than function"
                case 3:
                    self.message = "No arguments set in main.py"
                case 4:
                    self.message = "Executable function not found"
            if error_arg:
                self.message += f" >>> {error_arg}"

        super().__init__(self.message)


class FactoryRequirementVersionError(Exception):
    def __init__(self, module_name: str, n_ver: float | int, h_ver: float | int):
        """
        Exception for error in the module requirements version

        Args:
            module_name: name of module which version is incorrect
            n_ver: new version of module
            h_ver: current version of module

        """
        msg = (f"Version of the module \"{module_name}\" is incorrect." +
               f" Need version ({n_ver}.x ver.) | Have ({h_ver} ver.)")
        super().__init__(msg)


class DatabaseNameError(Exception):
    def __init__(self, name: str):
        """
        Exception for error in the load connection data for DB

        Args:
            name - database's name

        """
        super().__init__(f"Connection data for database \"{name}\" are not found.")


class DatabaseConnectionDataError(Exception):
    """
    Exception for error in the validation connection data for DB

    Args:
        name - database's name
        par - parameter's name

    """

    def __init__(self, name: str, par: str):
        super().__init__(f"Parameter \"{par}\" for database \"{name}\" are not found.")
