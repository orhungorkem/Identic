import argparse
import os
import hashlib



#Returns hash of the file in given path
def hashFile(path):
    f=open(path,"rb")  #read with bytes
    sfile=f.read()
    hash_object=hashlib.sha256(sfile)
    hexo=hash_object.hexdigest()
    f.close()
    return hexo



#Recursively traverses the directories in order to find duplicates in -f and -c options. 
def traversefc(dirpath,hashdict,duplicates):  #Takes a path, a dictionary in order to keep hashes of directories, a list to store yielded duplicates.
    #Hashdict format -> Hash:Path
    os.chdir(dirpath) #Update current directory as given path
    files = [f for f in os.listdir(".") if os.path.isfile(f)]  #list the files in current directory(not in nested directories)
    for i in files:
        filepath=dirpath+"/"+i  
        hexstr=hashFile(filepath)  #Hash the files
        if hexstr in hashdict: #A file with same has already added (means duplicate)
            duppath=hashdict[hexstr]  #get path of the duplicate
            induplicates=False  #suppose the duplicate file is not already involved in duplicate
            for i in duplicates:
                if(duppath in i):
                    induplicates=True  #now see the duplicate file has already been matched with another duplicate
                    i.append(filepath)  #then just append the new file into them
            if(not induplicates): #first duplicate of the file found
                duplicates.append([filepath,hashdict[hexstr]]) #add a new index of duplicates
        else:
            hashdict[hexstr]=filepath #no duplicate found, so add new hash to hashdict 
        
    directories=[d for d in os.listdir(".") if os.path.isdir(d)] #list the subdirectories in current directory
    for dirc in directories:
        traversefc(dirpath+"/"+dirc,hashdict,duplicates)  #preorder traversal


        
#Recursively traverses the directories in order to find duplicates in -d and -c options
def traversedc(dirpath,dirdictdh,dirdicthd,duplicates): #dirdictdh=path:hash dirdicthd=hash:path

    os.chdir(dirpath)
    directories=[d for d in os.listdir(".") if os.path.isdir(d)]
    for d in directories:
        traversedc(dirpath+"/"+d,dirdictdh,dirdicthd,duplicates) #postorder traversal since subdirectories must be examined first
    os.chdir(dirpath)
    hashlist=[] #will keep hashes of subdirectories and files
    for d in directories:
        dpath=dirpath+"/"+d
        hashlist.append(dirdictdh[dpath]) #adding hash of subdirectory to hashlist(subdirectories has already been processed with recursion)
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    for i in files:
        filepath=dirpath+"/"+i
        hexstr=hashFile(filepath)
        hashlist.append(hexstr)  #append file hashes
    hashlist.sort() #to process hashes in a fixed order
    hashstr=""  
    for hash in hashlist:
        hashstr+=hash  #concatinate hashlist components into a string to finally hash the string
    currenthash=(hashlib.sha256(hashstr.encode('utf-8'))).hexdigest()  #this is the hash of current directory
    if currenthash in dirdicthd:   #checking if similar hash has already been found
        duppath=dirdicthd[currenthash]  #get the duplicate path
        induplicates=False
        for i in duplicates:
            if(duppath in i):
                induplicates=True
                i.append(dirpath)
        if(not induplicates):
            duplicates.append([dirpath,duppath]) 
    else:
        dirdicthd[currenthash]=dirpath  #add the distinct hash to hash list
    dirdictdh[dirpath]=currenthash  #store the hash of current directory in order to compare its ancestors later



    
#Recursively traverses the directories in order to find duplicates in -f and -n options
def traversefn(dirpath,namedict,duplicates):  #namedict format: name:path
    os.chdir(dirpath)
    files = [f for f in os.listdir(".") if os.path.isfile(f)]  #list files
    for f in files:
        filepath=dirpath+"/"+f  #reach to full path
        if f in namedict:  #check files with same name
            induplicates=False
            duppath=namedict[f]  #after getting the path of duplicate, same process is applied as above functions
            for i in duplicates:
                if(duppath in i):
                    induplicates=True
                    i.append(filepath)
            if(not induplicates):
                duplicates.append([filepath,duppath])
        else:
            namedict[f]=filepath
            
    directories=[d for d in os.listdir(".") if os.path.isdir(d)]
    for dirc in directories:
        traversefn(dirpath+"/"+dirc,namedict,duplicates)  #preorder traversal


        

#Recursively traverses the directories in order to find duplicates in -d and -n options
#Process is almost same with traversedc, the only difference is that hashes are calculated according to names, not content.
def traversedn(dirpath,dictdh,dicthd,duplicates):

    os.chdir(dirpath)
    directories=[d for d in os.listdir(".") if os.path.isdir(d)]
    for d in directories:
        traversedn(dirpath+"/"+d,dictdh,dicthd,duplicates) #postorder traversal(first examine subdirectories)
    os.chdir(dirpath)
    hashlist=[]  #will keep names of files and hashes of subdirectories
    for d in directories:
        dpath=dirpath+"/"+d
        hashlist.append(dictdh[dpath]) #adding hash of subdirectory to hashlist(subdirectories have been processed with recursion already)
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    for i in files:
        hashlist.append(i)  #append file names(not content hashes)
    name=dirpath[dirpath.rfind('/')+1:]  #extract the name of current directory
    hashlist.append(name)
    hashlist.sort() #to process elements in a fixed order
    hashstr=""
    for hash in hashlist:
        hashstr+=hash
    currenthash=(hashlib.sha256(hashstr.encode('utf-8'))).hexdigest()  
    if currenthash in dicthd:
        duppath=dicthd[currenthash]
        induplicates=False
        for i in duplicates:
            if(duppath in i):
                induplicates=True
                i.append(dirpath)
        if(not induplicates):
            duplicates.append([dirpath,duppath]) 
    else:
        dicthd[currenthash]=dirpath  
    dictdh[dirpath]=currenthash  #add hash of directory to be reached by ancestors

def traverseSizes(dirpath,sizedict):
    os.chdir(dirpath)
    directories=[d for d in os.listdir(".") if os.path.isdir(d)]
    for d in directories:
       traverseSizes(dirpath+"/"+d,sizedict)
    os.chdir(dirpath)
    cursize=0
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    for f in files:
        cursize+=os.stat(f).st_size
    for d in directories:
        cursize+=sizedict[dirpath+"/"+d]
    sizedict[dirpath]=cursize

def isNested(path1,path2):   #seek path2 in path1
    if(path1==path2):
        return True
    os.chdir(path1)
    directories=[d for d in os.listdir(".") if os.path.isdir(d)]
    nestres=False
    for d in directories:
        if(isNested(path1+"/"+d,path2)):
           nestres=True
    return nestres

        
parser = argparse.ArgumentParser()

parser.add_argument('-f', action="store_true",dest='checkfile', default=False)
parser.add_argument('-d', action="store_true",dest='checkdir', default=False)
parser.add_argument('-c', action="store_true",dest='checkcontents', default=False)
parser.add_argument('-n', action="store_true",dest='checknames', default=False)
parser.add_argument('-cn', action="store_true",dest='checkboth', default=False)
parser.add_argument('-s', action="store_true",dest='checksizes', default=False)

args,alldirs=parser.parse_known_args() #dirs keep directories as list(since directories are the unknown arguments in command line)

valid=True

#CHECK IF ARGUMENTS ARE VALID
if(not args.checknames^args.checkcontents^args.checkboth): 
    if(not args.checknames|args.checkcontents|args.checkboth): # no -c -n -cn
        args.checkcontents=True #default condition
    else:
        if(args.checknames&args.checkcontents):
            args.checkboth=True
            args.checknames=False
            args.checkcontents=False
        else:
            valid=False #any 2 of -c -n -cn are together
else:
    if(args.checknames&args.checkcontents&args.checkboth): # all of -c -n -cn
        valid=False

if(args.checkfile&args.checkdir):  # -d -f together 
    valid=False

if(not args.checkfile|args.checkdir):  #default -f
    args.checkfile=True

    
if(args.checksizes&args.checknames&(not args.checkcontents)):  #-s -n together, ignore -s
    args.checksizes=False

if(not valid):
    print("invalid options")


#CONVERT RELATIVE PATHS TO FULL PATHS
for dir in alldirs:
    if(dir[0]!='/'):  #relative path
        currentpath=os.popen("pwd").read()  #get current directory
        adddir=currentpath.replace("\n","")+"/"+dir   #join current directory with given path to convert it  to fullpath
        alldirs.remove(dir)
        alldirs.append(adddir)  #dirs will be traversed

#ELIMINATE NESTED PATHS
dirsset=set()
for d in alldirs:
    dirsset.add(d)

dirs=[]
for i in dirsset:
    dirs.append(i)
for i in dirs:
    for j in dirs:
        if(i==j):
            continue
        if(isNested(i,j)):
            dirs.remove(j)
        
if(dirs==[]):
    dirs.append(os.getcwd())
        

if valid:

    duplicates=[]   #in all cases, duplicate data will be stored in this list with nested lists

    if(args.checkcontents):  #-c
        if(args.checkfile): #-f
            hashdict={}  #parameter will be given to recursive function
            for dir in dirs:  
                traversefc(dir,hashdict,duplicates)
            

        else: #-d option
            dirdictdh={} #parameters will be given
            dirdicthd={}
            for dir in dirs:
                traversedc(dir,dirdictdh,dirdicthd,duplicates)
            
    elif(args.checknames): #-n
        if(args.checkfile):  #-f
            namedict={}  
            for dir in dirs:
                traversefn(dir,namedict,duplicates)
            
        else:  #-d
            dirdictdh={}
            dirdicthd={}
            for dir in dirs:
                traversedn(dir,dirdictdh,dirdicthd,duplicates)

    elif(args.checkboth):  #-cn
        if(args.checkfile):  #-f
            hashduplicates=[]   #will keep the duplicates according to content
            hashdict={}
            for dir in dirs:
                traversefc(dir,hashdict,hashduplicates)
                #now seperate same named files in hashduplicates
            for group in hashduplicates:
                namedict={}  #name:pathlist  will keep the paths with same names together
                for path in group:
                    name=path[path.rfind('/')+1:]  #extract the name from path
                    if(name in namedict):  #check if name has already appeared before
                        namedict[name].append(path)  #if so, just add the path to values of the key(name)
                    else:
                        namedict[name]=[path]  #else, add the new name to dictionary
                for i in namedict:
                    if(len(namedict[i])>1):   #current name belongs to more than one file
                        duplicates.append(namedict[i]) #files with same content and name will be added to final list
        else:    
            hashduplicates=[]  #will keep the directories having identical contents
            dirdictdh={}
            dirdicthd={}
            for dir in dirs:
                traversedc(dir,dirdictdh,dirdicthd,hashduplicates)
            contentdict={}  #will keep content hashes for all directories
            for i in hashduplicates:
                for j in i:
                    contentdict[j]=dirdictdh[j]  
            nameduplicates=[]  #will keep directories having same name structure
            dirdictdhname={}
            dirdicthdname={}
            for dir in dirs:
                traversedn(dir,dirdictdhname,dirdicthdname,nameduplicates)
            namedict={}  #will keep name hashes for all directories
            for i in hashduplicates:
                for j in i:
                    namedict[j]=dirdictdhname[j] 
            generalhd={}  #will keep concatination of 2 types of hashes for all directories
            for i in hashduplicates:
                for j in i:
                    generalhash=namedict[j]+contentdict[j]  #concatination
                    if(generalhash in generalhd):  #looking for duplicate
                        generalhd[generalhash].append(j)
                    else:
                        generalhd[generalhash]=[j]
            for i in generalhd:
                if(len(generalhd[i])>1):  #if a general hash belongs to more than one directory, those are duplicate according to -cn too
                    duplicates.append(generalhd[i])
            
                

    
    if(args.checksizes):  #-s
        if(args.checkdir):
            sizedict={}
            for d in dirs:
                traverseSizes(d,sizedict)
            sizelist=[]  #will keep tuples in format (duplicatelist1,size1)(duplicatelist2, size2)...
            for dup in duplicates:
                path=dup[0]  # get one path from all duplicate lists
                dupsize=sizedict[path]
                sizelist.append((dup,dupsize))  #add index to sizelist as tuple
            for s in sizelist:
                s[0].sort()  #sort duplicates among themselves
            sizelist.sort()
            sizelist.reverse()
            sizelist.sort(key = lambda x: x[1])  #sort list according to sizes
            sizelist.reverse() #but decreasing
            for dups in sizelist:
                for i in dups[0]:
                    print(i+"\t"+str(dups[1]))
                print(" ")
        else:
            sizedict={}
            sizelist=[]
            for dup in duplicates:
                path=dup[0]
                dupsize=os.stat(path).st_size
                sizelist.append((dup,dupsize))
            for s in sizelist:
                s[0].sort()
            sizelist.sort()
            sizelist.reverse()
            sizelist.sort(key=lambda x:x[1])
            sizelist.reverse()
            for dups in sizelist:
                for i in dups[0]:
                    print(i+"\t"+str(dups[1]))
                print(" ")
                    
            
    else:  #if no size required
        for i in duplicates:
            i.sort()  
        duplicates.sort()
        for i in duplicates:
            for j in i:
                print(j)
            print(" ")
       

