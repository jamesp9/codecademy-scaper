#!/usr/bin/env python3

import urllib.request
import urllib.parse
import urllib.error
import re
import ast
import argparse
import os.path
import sys
import string
import json
import pprint

parser = argparse.ArgumentParser(description="Scrape and save the code examples from Codecademy website")
parser.add_argument("-o", "--outputdir",
        help="Directory where output files are written to. Default is ccurrent directory.")
parser.add_argument("-w", "--overwrite",
        help="Overwrite file if they already exist.", action='store_true', default=False)
group = parser.add_mutually_exclusive_group()
group.add_argument("-u", "--url", help="The Codecademy url you would like to scrape.")
group.add_argument("-f", "--infile", help="File containing already dumped contents of a url.")

args = parser.parse_args()
# data = ''


def geturlcontents(url):
    # url file object(ufo)
    ufo = urllib.request.urlopen(url)
    content = ufo.readlines()
    ufo.close()
    return content


def writefile(directory, filename, data):
    if not os.path.exists(directory):
        print(("Creating directory {}".format(directory)))
        os.makedirs(directory)

    filename = os.path.join(directory, filename)

    # print("Overwrite files: {}".format(args.overwrite))
    if not os.path.exists(filename) or args.overwrite:
        print(("Writing {}".format(filename)))
        with open(filename, 'w') as fo:
            fo.writelines(data)
    else:
        print(("{} already exists.".format(filename)))


def myfilename(filename):
    allowedchars = "-_. %s%s" % (string.ascii_letters, string.digits)
    newfilname = ''
    filename = filename.replace(' ', '.')
    filename = re.sub('\.{2,}', '', filename)
    for char in filename:
        if char in allowedchars:
            newfilname += char
    return newfilname


if args.infile is None and args.url is None:
    parser.print_help()
    sys.exit()

# Open HTML file saved from Firefox
if args.infile:
    print(args.infile)
    if os.path.isfile(args.infile):
        with open(args.infile, 'r') as fo:
            html = fo.readlines()
    else:
        parser.print_help()
        sys.exit()
elif args.url:
    html = geturlcontents(args.url)

course_json = None
# Get the JSON object containing all the data
for h in html:
    # if 'CCDATA.composer.course' in h or 'CCDATA.composer.current_project' in h:
    if 'CCDATA.composer.course' in h:
        course_output = re.sub('^[^\{]*', '', h)  # regex character class, match anything that isn't { at start of line
        course_output = re.sub(';$', '', course_output)  # strip ; at end of line
        course_data = json.loads(course_output)

with open('course_output.json', 'w') as fo:
    # fo.write(pprint.pformat(course_data))
    fo.write(json.dumps(course_data))

with open('data_structure.txt', 'w') as fo:
    fo.write(pprint.pformat(course_data))

# pprint.pprint(course_data)

course_name = course_data['name']
course_path = course_name.replace(' ', '_').lower()
print(course_path)


for project in course_data['projects']:
    print('=' * 79)
    print("Project Index: {}".format(project['index']))
    print("Project Name: {}".format(project['name']))
    project_path = str(project['index']) + '-' + project['name'].replace(' ', '_').lower()
    print('=' * 79)
    for checkpoint in project['checkpoints']:
        print("\tCheckpoint Index: {}".format(checkpoint['index']))
        print("\tCheckpoint Name: {}".format(checkpoint['name']))
        checkpoint_path = str(checkpoint['index']) + '-' + checkpoint['name'].replace(' ', '_').lower()
        print("\t{}".format('-' * 79))

        try:
            for latest_file in checkpoint['latest_files']:
                print("\t\tFilename: {}".format(latest_file['filename']))
                filename = latest_file['filename']
                file_content = latest_file['content']

                path = os.path.join(course_path, project_path, checkpoint_path)
                writefile(path, filename, file_content)

            use_default_files = False
        except KeyError as msg:
            use_default_files = True

        if use_default_files:
            for default_file in checkpoint['default_files']:
                print("\t\tFilename(default): {}".format(default_file['filename']))
                filename = default_file['filename']
                file_content = default_file['content']

                path = os.path.join(course_path, project_path, checkpoint_path)
                writefile(path, filename, file_content)

        print("\t\t{}".format('-' * 79))




# print("\n")
# if 'project_index' in course_data:
#     course_index = course_data['project_index']
# elif 'index' in course_data:
#     course_index = course_data['index']

# #print("Project Index: {}\n".format(course_index))
# print(("Course: {}".format(course)))
# #print("Projects: {}".format(len(course_data['projects'])))
# if 'projects' in course_data:
#     for project in course_data['projects']:
#         proj_index = project['index']
#         proj_name = project['name']
#         #print("project type:{}".format(type(project)))
#         #print("project keys:{}".format(project.keys()))
#         #print("\tProject Name:{}".format(proj_name))
#         projdir = str(proj_index) + '-' + myfilename(proj_name)
#         print(("\tProject: {}".format(course)))
#         for checkpoint in project['checkpoints']:
#             check_index = checkpoint['index']
#             check_name = checkpoint['name']
#             #print("Checkpoint Keys: {}".format(checkpoint.keys()))
#             #print("\t\tCheckpoint Index: {}".format(checkpoint['index']))
#             #print("\t\tCheckpoint Name: {}".format(checkpoint['name']))
#             cpdir = str(check_index) + '-' + myfilename(check_name)
#             print(("\t\tCheckpoint: {}".format(cpdir)))
#             for default_file in checkpoint['default_files']:
#                 #print("default_file:{}".format(default_file))
#                 #ucontent = default_file['content'].decode('utf-8')
#                 print(("\t\t\tfilename:{}".format(default_file['filename'])))
#                 #print("content type:{}".format(type(ucontent) ))
#                 filepath = os.path.join('course',course, projdir, cpdir)
#                 writefile(filepath, default_file['filename'], ucontent)
#             print("\n")
# elif 'checkpoints' in course_data:
#     for checkpoint in course_data['checkpoints']:
#         check_index = checkpoint['index']
#         check_name = checkpoint['name']
#         #print("Checkpoint Keys: {}".format(checkpoint.keys()))
#         #print("\t\tCheckpoint Index: {}".format(checkpoint['index']))
#         #print("\t\tCheckpoint Name: {}".format(checkpoint['name']))
#         cpdir = str(check_index) + '-' + myfilename(check_name)
#             print(("\t\tCheckpoint: {}".format(cpdir)))
#             for default_file in checkpoint['default_files']:
#                 #print("default_file:{}".format(default_file))
#                 #ucontent = default_file['content'].decode('utf-8')
#                 print(("\t\t\tfilename:{}".format(default_file['filename'])))
#                 #print("content type:{}".format(type(ucontent) ))
#                 filepath = os.path.join('current_project', course, cpdir)
#                 writefile(filepath, default_file['filename'], ucontent)
#             print("\n")
