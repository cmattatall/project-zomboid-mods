import os
import pathlib

#installedPZdir = 'C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\org'
installedPZdir = "D:\\Steam Folder\\steamapps\\common\\ProjectZomboid"

THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sourcesOutputDir = pathlib.Path(THIS_SCRIPT_DIR)/pathlib.Path("sources")

if __name__ == "__main__":
    for path in pathlib.Path(installedPZdir).rglob('*.class'):
        inputJavaClassPath = str(path)
        javaSourceOutputPathSuffix = path.relative_to(installedPZdir)
        finalPath = pathlib.Path(sourcesOutputDir) / javaSourceOutputPathSuffix
        os.makedirs(finalPath.parent, exist_ok=True)

        testClass = "D:\\Steam Folder\\steamapps\\common\\ProjectZomboid\\com\\jcraft\\jorbis\\Info.class"
        decompilerPath = "D:\\Desktop\\zomboid_mods\\decompiler\\my_decompiler\\jd-core\\build\\libs\\jd-core-1.1.4.jar"

        outputJavaSourcePath = str(finalPath).rstrip(".class") + ".java"
        
        # always delete, we want latest version of source
        if os.path.exists(outputJavaSourcePath):
            os.remove(outputJavaSourcePath)

        print(f"outputJavaSourcePath={outputJavaSourcePath}")
        os.system(f"java -jar \"{decompilerPath}\" \"{inputJavaClassPath}\" \"{outputJavaSourcePath}\" ")
        #decompilerPath = "procyon\\build\\Procyon.Decompiler\\libs\\procyon-decompiler-1.0-SNAPSHOT.jar"
        #os.system(f"java -jar \"{decompilerPath}\" -o \"{finalPath}\" \"{inputJavaClassPath}\"")
        #os.system(f"java -jar \"{decompilerPath}\" \"{inputJavaClassPath}\" \"{finalPath}\" ")
