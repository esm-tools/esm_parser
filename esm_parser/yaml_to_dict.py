import yaml
import logging
import esm_parser

logger = logging.getLogger("root")
DEBUG_MODE = logger.level == logging.DEBUG

YAML_AUTO_EXTENSIONS = ["", ".yml", ".yaml", ".YML", ".YAML"]


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
                # Check for duplicates
                check_duplicates(yaml_file)
                # Back to the beginning of the file
                yaml_file.seek(0, 0)
                # Actually load the file
                yaml_load =  yaml.load(yaml_file, Loader=yaml.FullLoader)
                # Check for incompatible ``_changes`` (no more than one ``_changes``
                # type should be accessible simultaneously)
                check_changes_duplicates(yaml_load, filepath + extension)
                return yaml_load
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


def check_changes_duplicates(yamldict_all, fpath):
    """
    Finds variables containing ``_changes`` (but excluding ``add_``) and checks
    if they are compatible with the same ``_changes`` inside the same file. If they
    are not compatible returns an error where the conflicting variable paths are
    specified. More than one ``_changes`` type in a file are allowed but they need
    to be part of the same ``_choose`` and not be accessible simultaneously in any
    situation.

    Parameters
    ----------
    yamldict_all : dict
        Dictionary read from the yaml file
    fpath : str
        Path to the yaml file
    """
    changes_note = "Note that if there are more than one ``_changes`` in the " \
                   "file, they need to be placed inside different cases of the " \
                   "same ``choose`` and these options need to be compatible " \
                   "(only one ``_changes`` can be reached at a time).\n" \
                   "Use ``add_<variable>_changes`` if you want to add/overwrite " \
                   "variables inside the main ``_changes``."
    # If it is a couple setup, check for ``_changes`` duplicates separately for each component
    if "general" not in yamldict_all:
        yamldict_all = {"main": yamldict_all}
    # Loop through the components or main
    for yamldict in yamldict_all.values():
        # Check if any <variable>_changes exist, if not, return
        changes_list = esm_parser.find_key(yamldict, "_changes", "add_",
                                           paths2finds = [], sep=",")
        if len(changes_list) == 0:
            return

        # Find ``_changes`` types
        changes_types = set([y for x in changes_list for y in x.split(",")
                             if "_changes" in y])
        # Define ``_changes`` groups
        changes_groups = []
        for change_type in changes_types:
            changes_groups.append([x for x in changes_list if change_type == x.split(",")[-1]])

        # Loop through the different groups
        for changes_group in changes_groups:
            # Check for ``_changes`` without ``choose_``, "there can be only one"
            changes_no_choose = [x for x in changes_group if "choose_" not in x]
            if len(changes_no_choose) > 1:
                changes_no_choose = [x.replace(",",".") for x in changes_no_choose]
                raise Exception("\n\nMore than one ``_changes`` out of a ``choose_``in "
                                + fpath + ":\n    - " + "\n    - ".join(changes_no_choose) +
                                "\n" + changes_note + "\n\n")
            elif len(changes_no_choose) == 1:
                changes_group.remove(changes_no_choose[0])
                if len(changes_group) > 0:
                    changes_group = [x.replace(",",".") for x in changes_group]
                    raise Exception("\n\nThe general ``" + changes_no_choose[0] +
                                    "`` and ``_changes`` in ``choose_`` are not compatible in "
                                    + fpath + ":\n    - " +
                                    "\n    - ".join(changes_group) + "\n" +
                                    "\n" + changes_note + "\n\n")

            # Check for incompatible ``_changes`` inside ``choose_``
            changes_group_split = [x.split(",") for x in changes_group]
            for count, changes in enumerate(changes_group_split):
                path2choose, case = find_last_choose(changes)
                for other_changes in changes_group_split[count+1:]:
                    sub_path2choose, sub_case = find_last_choose(other_changes)
                    if path2choose in sub_path2choose or sub_path2choose in path2choose:
                        if case == sub_case:
                            raise Exception("\n\nThe following ``_changes`` can be accessed " +
                                         "simultaneously in " + fpath + ":\n" +
                                         "    - " + ".".join(changes) + "\n" +
                                         "    - " + ".".join(other_changes) + "\n" +
                                         "\n" + changes_note + "\n\n")
                    else:
                        raise Exception ("\n\nThe following ``_changes`` can be accessed " +
                                         "simultaneously in " + fpath + ":\n" +
                                         "    - " + ".".join(changes) + "\n" +
                                         "    - " + ".".join(other_changes) + "\n" +
                                         "\n" + changes_note + "\n\n")

            # Load the yaml file
            with open(fpath) as yaml_file:
                # Loop through the <variable>_changes found in the dictionary
                for changes in changes_list:
                    pass

def find_last_choose(var_path):
    """
    Locates the last ``choose_`` on a string containing the path to a
    variable separated by ",", and returns the path to the choose (also
    separated by ",") and the case that follows the ``choose_``.

    Parameters
    ----------
    var_path : str
        String containing the path to the last ``choose_`` separated by
        ",".
    """
    # Find the last ``choose_``
    last_choose = [x for x in var_path if "choose_" in x][-1]
    # Find the last ``choose_`` index
    choose_index = var_path.index(last_choose)
    # Defines the path to the last ``choose_``
    path2choose = ",".join(var_path[:var_path.index(last_choose)+1])
    # Defines the case of the last ``choose_``
    case = var_path[choose_index+1]
    return path2choose, case


def check_duplicates(src):
    """
    Checks that there are no duplicates in a yaml file, and if there are
    returns an error stating which key is repeated and in which file the
    duplication occurs.

    Parameters
    ----------
    src : object
        Source file object

    Exceptions
    ----------
    ConstructorError
        If duplicated keys are found, returns an error
    """

    class PreserveDuplicatesLoader(yaml.loader.Loader):
    # We eliberately define a fresh class inside the function,
    # because add_constructor is a class method and we don't want to
    # mutate pyyaml classes.
        pass

    def map_constructor(loader, node, deep=False):
        """
        Mapping, finds any duplicate keys.
        """
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            value = loader.construct_object(value_node, deep=deep)

            if key in mapping:
                raise yaml.constructor.ConstructorError(
                    "pping", node.start_mark,
                    "\n\nKey ``{0}`` is duplicated {1}\n\n"
                    .format(key, str(key_node.start_mark).replace("  ","").split(",")[0]))

            mapping[key] = value

        return loader.construct_mapping(node, deep)

    PreserveDuplicatesLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, map_constructor)
    return yaml.load(src, Loader=PreserveDuplicatesLoader)


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
