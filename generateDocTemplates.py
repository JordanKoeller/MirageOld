import glob
import os
import sys
import re
import sys




def recursePath(path,dest):
        for file in glob.glob(path+"/*"):
            if os.path.isfile(file) and ('.py' in file or '.pxd' in file):
                classes = findClassNames(file)
                print(classes)
                writeClassDoc(dest+file,classes)
                    
            elif os.path.isdir(file):
                if not os.path.isdir(dest+file):
                    os.makedirs(dest+file)
                recursePath(file,dest)
                
def findClassNames(filename):
    regPattern = '''class (\w+)\(\w+\):'''
    try:
        with open(filename,'r+') as file:
            contents = file.read()
            foundClasses = re.findall(regPattern,contents)
            return set(filter(lambda x: x is not [],foundClasses))
    except UnicodeDecodeError as e:
#        print(filename+" Failed")
        return []
        

def writeClassDoc(filename,classnames):
    fullString = ''
    for className in classnames:
        path = (filename.split('.')[0]+'.').replace('/','.').split('src.')[-1]
        classString = '.. autoclass:: '+path+className
        methodString = '.. automethod:: '+path+className
        fullString += classString + "\n   :members:\n\n"
    try:
        with open(filename.split('.')[0]+'.rst','w+') as file:
            file.write(fullString)
    except UnicodeDecodeError as e:
        pass
#            print(path+ "Failed")
if __name__ == "__main__":
    source = sys.argv[1]
    dest = sys.argv[2]

    recursePath(source,dest)
