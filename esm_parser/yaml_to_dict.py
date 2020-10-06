import yaml
import logging

logger = logging.getLogger("root")
DEBUG_MODE = logger.level == logging.DEBUG

YAML_AUTO_EXTENSIONS = ["", ".yml", ".yaml", ".YML", ".YAML"]


class EsmConfigFileError(Exception):
    """
    Exception for yaml file containing tabs or other syntax issues.

    An exception used when yaml.load() throws a yaml.scanner.ScannerError.
    This error occurs mainly when there are tabs inside a yaml file or
    when the syntax is incorrect. If tabs are found, this exception returns
    a user-friendly message indicating where the tabs are located in the
    yaml file.

    Parameters
    ----------
    fpath : str
        Path to the yaml file
    """

    def __init__(self, fpath, yaml_error):
        report = ""
        # Loop through the lines inside the yaml file searching for tabs
        with open(fpath) as yaml_file:
            for n, line in enumerate(yaml_file):
                # Save lines and line numbers with tabs
                if "\t" in line:
                    report += str(n) + ":" + line.replace("\t", "____") + "\n"

        # Message to return
        if len(report) == 0:
            # If no tabs are found print the original error message
            print("\n\n\n" + yaml_error)
        else:
            # If tabs are found print the report
            self.message = "\n\n\n" \
                           f"Your file {fpath} has tabs, please use ONLY spaces!\n" \
                            "Tabs are in following lines:\n" + report
        super().__init__(self.message)


def yaml_file_to_dict(filepath):
    """
    Given a yaml file, returns a corresponding dictionary.

    If you do not give an extension, tries again after appending one.
    It raises an EsmConfigFileError exception if yaml files contain tabs.

    Parameters
    ----------
    filepath : str
        Where to get the YAML file from

    Returns
    -------
    dict
        A dictionary representation of the yaml file.

    Raises
    ------
    EsmConfigFileError
        Raised when YAML file contains tabs or other syntax issues.
    FileNotFoundError
        Raised when the YAML file cannot be found and all extensions have been tried.
    """
    for extension in YAML_AUTO_EXTENSIONS:
        try:
            with open(filepath + extension) as yaml_file:
                cfg = yaml.load(yaml_file, Loader=yaml.FullLoader)
                cfg["debug_info"] = {"loaded_from_file": yaml_file.name}
                return cfg
        except IOError as error:
            logger.debug(
                "IOError (%s) File not found with %s, trying another extension pattern.",
                error.errno,
                filepath + extension,
            )
        except yaml.scanner.ScannerError as yaml_error:
            logger.debug("Your file %s has syntax issues!",
                filepath + extension,
            )
            raise EsmConfigFileError(filepath + extension, yaml_error)
    raise FileNotFoundError(
        "All file extensions tried and none worked for %s" % filepath
    )
