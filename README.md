# Identic
A project to detect duplicate files and directories

To execute:

1. Navigate the file of identic.py from terminal.
2. Enter command: python identic.py [arguments] [list of directories]

Arguments:

-f:look for duplicate files
-d:look for duplicate directories
-c:look for duplicate contents
-n:look for duplicate file/directory names
-cn:look for both names and content
-s:duplicate sizes should be printed

Ex: python identic.py -f -c path_of_dir1
Returns files with same contents in dir1.
