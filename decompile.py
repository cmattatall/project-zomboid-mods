import sys
import os
import pathlib
import re
import argparse


#installedPZdir = 'C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\org'
#installedPZdir = "D:\\Steam Folder\\steamapps\\common\\ProjectZomboid"

def get_this_script_dir():
    return pathlib.Path(os.path.abspath(__file__)).parent

def get_sources_output_path():
    return get_this_script_dir()/pathlib.Path("sources")

sourcesOutputPath = get_sources_output_path()


def prepend_package_import_to_java_source_file( java_source_file_abspath : str, 
                                                java_project_source_dir : str):
    sourcePath = pathlib.Path(java_source_file_abspath)
    sourcePathDir = sourcePath.parent
    packagePath = sourcePathDir.relative_to(sourcesOutputPath)
    packageName = str(packagePath).replace(os.sep, ".")
    # print(f"packageName:{packageName}") # debug

    missing_pkg_decl = False
    source_file_contents = None # hoist decl because we'll have to write identical content back anyway
    with open(java_source_file_abspath, 'r') as source_file: 
        source_file_contents = source_file.read()
        
        JAVA_PACKAGE_DECLARATION_REGEX = r'^[ \t]*package *$;'
        if not JAVA_PACKAGE_DECLARATION_REGEX in source_file_contents:
            # print(f"file: {java_source_file_abspath} does not contain a package declaration!") # debug
            missing_pkg_decl = True

    if missing_pkg_decl:
        with open(java_source_file_abspath, "w") as source_file_missing_package_decl:
            source_file_contents_with_pkg_decl = f"package {packageName};\n" + source_file_contents
            source_file_missing_package_decl.write(source_file_contents_with_pkg_decl)


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
    for path in pathlib.Path(installedPZdir).rglob('*.class'):

        inputJavaClassPath = str(path)
        javaSourceOutputPathSuffix = path.relative_to(installedPZdir)
        finalPath = pathlib.Path(sourcesOutputPath) / javaSourceOutputPathSuffix
        os.makedirs(finalPath.parent, exist_ok=True)

        testClass = "D:\\Steam Folder\\steamapps\\common\\ProjectZomboid\\com\\jcraft\\jorbis\\Info.class"
        decompilerPath = pathlib.Path(get_this_script_dir())/pathlib.Path("decompiler/build/libs/jd-core-1.1.4.jar")

        outputJavaSourcePath = str(finalPath).rstrip(".class") + ".java"
        
        # always delete, we want latest version of source
        if os.path.exists(outputJavaSourcePath):
            os.remove(outputJavaSourcePath)
        
        #print(f"outputJavaSourcePath={outputJavaSourcePath}") # debug
        os.system(f"java -jar \"{decompilerPath}\" \"{inputJavaClassPath}\" \"{outputJavaSourcePath}\" ")

        # Fix files that are missing their package statements
        # NOTE: 
        # this assumes the directory structure of the .class files
        # mirrors the .java ones of original source
        prepend_package_import_to_java_source_file(outputJavaSourcePath, sourcesOutputPath)