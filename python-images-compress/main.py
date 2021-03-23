import os

directory = "M:\\my_super_files_700\\"
directory_compressed = "M:\\my_super_files_700_compressed\\"

with os.scandir(path=directory) as it:
    for entry in it:
        if not entry.is_file():
            print("dir:\t" + entry.name)
        else:
            print("file:\t" + entry.name)
            os.system("cjpeg -quant-table 2 -quality 60 -outfile {} {}".format(directory_compressed+entry.name, directory+entry.name))
