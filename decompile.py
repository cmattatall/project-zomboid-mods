import sys
import os
import pathlib
import re
import argparse


def get_this_script_dir():
    return pathlib.Path(os.path.abspath(__file__)).parent

def get_sources_output_path():
    return get_this_script_dir()/pathlib.Path("sources")

def get_source_file_package_name(java_source_file_abspath : str):
    sourcePath = pathlib.Path(java_source_file_abspath)
    sourcePathDir = sourcePath.parent
    packagePath = sourcePathDir.relative_to(get_sources_output_path())
    packageName = str(packagePath).replace(os.sep, ".")
    return packageName

def fix_java_source_file(java_source_file_abspath : str):

    # Fix files that are missing their package statements
    # NOTE: 
    # this assumes the directory structure of the .class files
    # mirrors the .java ones of original source
    prepend_package_decl_to_java_source_file(java_source_file_abspath)
    fix_nested_class_imports(java_source_file_abspath)


def get_package_keyword_regex():
    return r'^[ \t]*package *$;'

def prepend_package_decl_to_java_source_file( java_source_file_abspath : str):

    packageName = get_source_file_package_name(java_source_file_abspath)
    # print(f"packageName:{packageName}") # debug

    missing_pkg_decl = False
    with open(java_source_file_abspath, 'r') as source_file: 
        source_file_contents = source_file.read()
        
        JAVA_PACKAGE_DECLARATION_REGEX = get_package_keyword_regex()
        if not JAVA_PACKAGE_DECLARATION_REGEX in source_file_contents:
            print(f"file: {java_source_file_abspath} does not contain a package declaration!") # debug
            source_file.close()
            with open(java_source_file_abspath, "w") as source_file_missing_package_decl:
                source_file_contents_with_pkg_decl = f"package {packageName};\n" + source_file_contents
                source_file_missing_package_decl.write(source_file_contents_with_pkg_decl)

def prepend_package_import_to_java_source_file( java_source_file_abspath : str, import_name : str):
    with open(java_source_file_abspath, "r") as source_file:
        source_file_contents = source_file.read()
        if source_file_contents == None:
            raise f"Error occurred trying to read source file contents of {java_source_file_abspath} in function:prepend_package_import_to_java_source_file"

        source_file.close()
        with open(java_source_file_abspath, "w") as source_file:

            # If the "package" keyword is not there, we can just append the imports,
            # But if it is there we need to be certain we add the imports AFTER
            # the package declaration.
            new_source_file_contents = source_file_contents
            source_file_lines = source_file_contents.splitlines()
            for line in source_file_lines:
                match = re.search("package[ \t]([^ \t]+);", line)
                if match != None:
                    print(f"match.group():{match.group()}")
                    new_source_file_contents = new_source_file_contents.replace(line, line + f"\nimport {import_name};")
            source_file.write(new_source_file_contents) 

def get_class_declarations(java_source_file_abspath : str):
    class_declarations = []

    #print(f"GETTING CLASS DECLARATIONS FROM {java_source_file_abspath}") # debug
    
    # If we assume the syntax from the decompiler is correct, 
    # we can just look for the class token and take the next
    with open(java_source_file_abspath, "r") as source_file:
        source_lines  = source_file.readlines()
        for line in source_lines:
            matches = re.search("[\t ]?class[\t ]+([a-zA-z0-9_]+)[ \t{{]", line)
            if matches != None:
                # HACK: assume no more than 1 class declaration on a line
                class_name = matches.group(1)
                #print(f"matches.group(1):{matches.group(1)}") # debug
                class_declarations.append(class_name)
    return class_declarations


def get_nested_class_source_files(java_source_file_abspath : str):
    nested_class_source_files = []
    java_source_file_path = pathlib.Path(java_source_file_abspath)
    java_source_file_parent_dir = java_source_file_path.parent
    java_source_file_name = java_source_file_path.name.rstrip(".java")

    #print(f"java_source_file_parent_dir:{str(java_source_file_parent_dir)}") # debug
    #print(f"java_source_file_name:{str(java_source_file_name)}") # debug

    # HACK: We are just going to filter for all *.java files and remove based on rules
    # TODO: Fix me so that I actually can glob by pattern instad of grabbing everything and filtering
    # (this is N^2)
    #NESTED_CLASS_GLOB_PATTERN = f"{java_source_file_name}\\$*"
    NESTED_CLASS_GLOB_PATTERN = f"{java_source_file_name}\$(([^\$1])+[\$]?)+\.java"
    ALL_JAVA_FILES_PATTERN = f"*.java"
    for pathStr in pathlib.Path(str(java_source_file_parent_dir)).glob(ALL_JAVA_FILES_PATTERN):
        filePath = pathlib.Path(pathStr)
        fileName = filePath.name
        if re.match(NESTED_CLASS_GLOB_PATTERN, fileName):
            print(f"file:{fileName} matches {NESTED_CLASS_GLOB_PATTERN}") # debug
            nested_class_path_abs = str(java_source_file_parent_dir/filePath)
            nested_class_source_files.append(nested_class_path_abs)

    return nested_class_source_files

def fix_nested_class_imports(java_source_file_abspath : str):
    nested_class_source_files = get_nested_class_source_files(java_source_file_abspath)

    source_file_alias_path = java_source_file_abspath.replace(".java", "$1.java")
    print(f"source_file_alias_path:{source_file_alias_path}")
    if os.path.exists(source_file_alias_path):
        os.remove(source_file_alias_path)

    for nested_source in nested_class_source_files:
        # print(f"Found nested source file: {nested_source}") # debug
        nested_class_declarations = get_class_declarations(nested_source)

        for className in nested_class_declarations:
            import_name = f"{get_source_file_package_name(java_source_file_abspath)}.{className}"
            # print(f"Adding import statement for {import_name} to {java_source_file_abspath}") # debug
            prepend_package_import_to_java_source_file(java_source_file_abspath, import_name)

        fix_java_source_file_name(nested_source)


def get_decompiler_path():
    return pathlib.Path(get_this_script_dir())/pathlib.Path("decompiler/build/libs/jd-core-1.1.4.jar")


def get_class_file_java_output_path(class_file_pathabs : str, pz_install_root : str):
    class_path_obj = pathlib.Path(class_file_pathabs)
    output_path_suffix = class_path_obj.relative_to(pz_install_root)
    output_path_str = str(get_sources_output_path() / output_path_suffix )
    output_path_str = output_path_str.rstrip(".class") + ".java"
    output_pathObj = pathlib.Path(output_path_str)
    os.makedirs(output_pathObj.parent, exist_ok=True)
    #print(f"output_path_str:{output_path_str}") # debug
    return str(output_pathObj)


def decompile_class_file(class_file_path : str, pz_install_root : str):
    java_source_output_path = get_class_file_java_output_path(class_file_path, pz_install_root)
    # print(f"{class_file_path} will be decompiled into java_source_output_path:{java_source_output_path}") # Debug

    # always delete, we want latest version of source
    if os.path.exists(java_source_output_path):
        os.remove(java_source_output_path)

    os.system(f"java -jar \"{get_decompiler_path()}\" \"{class_file_path}\" \"{java_source_output_path}\" ")

    fix_java_source_file(java_source_output_path)
    return str(java_source_output_path)


def fix_java_source_file_name(java_source_file_path : str):
    java_source_path_obj = pathlib.Path(java_source_file_path)
    output_source_dir = java_source_path_obj.parent
    sourcefile_name = java_source_path_obj.name
    new_source_name = sourcefile_name.split("$")[-1]
    new_sourcefile_path = output_source_dir/pathlib.Path(new_source_name)
    print(f"renaming {java_source_file_path} -> {new_sourcefile_path}") # Debug

    if os.path.exists(new_sourcefile_path):
        os.remove(new_sourcefile_path)
    os.rename(java_source_file_path, new_sourcefile_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zomboid_path", 
                        required=True, 
                        action="store", 
                        dest="PZ_install_root", 
                        help='''
                        This is the path to the install directory of project zomboid on your system. 
                        E.G. \'C:\\Program Files (x86)\\Steam\\steamapps\\common\\ProjectZomboid\\org\''''
    )
    args = parser.parse_args()
    installedPZdir = args.PZ_install_root

    for class_file in pathlib.Path(installedPZdir).rglob('*.class'):
        decompile_class_file(class_file, installedPZdir)
