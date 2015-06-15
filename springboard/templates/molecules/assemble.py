from os import listdir, pardir, path
from os.path import isfile, join
mypath = path.dirname(path.realpath(__file__))

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# print onlyfiles

DESTINATION_FILE = (path.join(mypath, pardir) + "/molecules.html")

output_file = open(DESTINATION_FILE, "w")

output_file.write("{% import 'atoms.html' as atoms %}\n\n")
output_file.close()

output_file = open(DESTINATION_FILE, "a")

for file_name in onlyfiles:
    if (file_name.endswith('.html')):
        myfile = open(mypath + '/' + str(file_name))
        mytxt = myfile.read()
        output_file.write(mytxt + "\n\n")
        myfile.close()

output_file.close()
