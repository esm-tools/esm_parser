import yaml
import logging

logger = logging.getLogger("root")
DEBUG_MODE = logger.level == logging.DEBUG

YAML_AUTO_EXTENSIONS = ["", ".yml", ".yaml", ".YML", ".YAML"]

class EsmConfigFileError(Exception):
    """
    Exception for yaml file containing tabs.

    An exception used when yaml.load() throws a yaml.scanner.ScannerError.
    This error occurs mainly when there are tabs inside a yaml file. This
    exception returns a user-friendly message indicating where the tabs
    are located in the yaml file.
    """

    def __init__(self, fpath):
        report = ""
        # Loop through the lines inside the yaml file searching for tabs
        with open(fpath) as yaml_file:
            for n, line in enumerate(yaml_file):
                # Save lines and line numbers with tabs
                if "\t" in line:
                    report += str(n) + ":" + line.replace("\t","____") + "\n"

        # Message to return
        self.message =  "\n\n\n" \
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
    """
    for extension in YAML_AUTO_EXTENSIONS:
        try:
            with open(filepath + extension) as yaml_file:
                return yaml.load(yaml_file, Loader=yaml.FullLoader)
        except IOError as error:
            logger.debug(
                "IOError (%s) File not found with %s, trying another extension pattern.",
                error.errno,
                filepath + extension,
            )
        except yaml.scanner.ScannerError as error:
            logger.debug("Your file %s has tabs, please use only spaces!",
                filepath + extension,
            )
            raise EsmConfigFileError(filepath + extension)
    raise FileNotFoundError(
        "All file extensions tried and none worked for %s" % filepath
    )


