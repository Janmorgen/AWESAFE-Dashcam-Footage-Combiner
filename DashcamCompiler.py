from moviepy.editor import *
import os
import lightnet

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
mov_paths=[]

# Finds files with the specified extension in the specified starting_folder
#   in this case it is used to find .MOV files in the working directory of
#   the program.
def mov_finder(starting_folder,extension):
    file_paths = []
    for file in os.listdir(starting_folder):
        if file.endswith(extension):
            file_paths.append(os.path.join(dir_path,file))
    return file_paths

# Finds and filters all the letters in a string
def find_letter(string):
    letters=[]
    for letter in string:
        if letter.isalpha():
            letters.append(letter)
    return letters

# Finds and filters all the digits in a string
def find_digits(string):
    digits=[]
    for letter in string:
        if letter.isdigit():
            digits.append(int(letter))
    return digits

# Sorts the movie file paths in order for easier processing
def sort_mov_files(paths):
    paths.sort()

# Resolution switch for user choice, larger resolutions require more time to combine (probably obvious)
def res_switch(num):
    switch={
        1:[1920, 1080],
        2:[1280, 720],
        3:[720, 480]
    }
    return switch.get(num,switch.get(3))

# Clearly increments something, not entirely sure how or why anymore though
def increment_list(list):
    if list[len(list)-1] == 9:
        list[len(list) - 1] = 0
        if list[len(list)-2] == 9:
            list[len(list)-2] = 0
            if list[len(list)-3] == 9:
                list[len(list) - 3] = 0
            else:
                list[len(list) - 3] += 1
        else:
            list[len(list)-2] += 1
    else:
        list[len(list) - 1] +=1
    return list

# Clearly decrements something, not entirely sure how or why anymore though
def decrement_list(list):
    if list[len(list)-1] == 0:
        if list[len(list) - 2] == 0:
            if list[len(list) - 3] != 0:
                list[len(list) - 3] -= 1
                list[len(list) - 2] = 9
                list[len(list) - 1] = 9
        else:
            list[len(list) - 2] -= 1
            list[len(list) - 1] = 9
    else:
        list[len(list) - 1] -= 1

    return list

def list_to_string(list):
    return (list.__str__().replace(" ", "").replace(",", "").replace("[", "").replace("]", "").replace("\'", ""))

# Finds all footage A (windshield facing) and footage B (driver facing) footage that correspond to one another,
#   basically footage in the same timeframe
def find_pairing(string):
    paired=[]
    digits=find_digits(string.split("_")[3].split(".")[0])

    letter=find_letter(string.split("_")[3].split(".")[0])

    if letter[0]=='A':
        digits=increment_list(digits)
        for i in range(0,len(digits)):
            paired.append (digits[i])
        paired.append('B')
    if letter[0]=='B':
        digits=increment_list(digits)
        for i in range(0,len(digits)):
            paired.append(digits[i])
        paired.append('A')
    return list_to_string(paired)

# Finds the required file names to complete the footage set
def find_missing(list):
    sort_mov_files(list)
    first=find_digits(list[0].split("_")[3].split(".")[0])
    count=first
    missing_pairs=[]

    for i in range(0, len(list)):
        if find_digits(list[i].split("_")[3].split(".")[0])[2]!=count[2]:
            missing_pairs.append(find_pairing(list[i-1]))
            count=find_digits(list[i].split("_")[3].split(".")[0])
        increment_list(count)
    return (missing_pairs)

# Grab all .MOV file paths in working directory and sort them
mov_paths=mov_finder(DIR_PATH,".MOV")
sort_mov_files(mov_paths)


count =0
clip_count=0
clips=[]
print("Found ", len(mov_paths)," in working directory...")

# Checks if enough .MOV file paths have been found to create combined footage, also checks if
#   there are files missing from pairings or from sequence, if so, the program terminates
if len(mov_paths)<2:
    print("Insufficient number of .MOV files detected.\nTerminating process...")
    os._exit(-1)
if len(mov_paths)%2!=0:
    print("Unable to pair an uneven number of .MOV files.\nTerminating process...")
    os._exit(-1)
missing=find_missing(mov_paths)
if len(missing)!=0:
    print("File set is missing ", len(missing)," file(s): ",(missing),"\nTerminating process...")
    os._exit(-1)

# Uses the first .MOV file to determine when the footage was shot, then prints the year follwed by date,
#   in format: YYYY_MMDD
year_of_clips=mov_paths[0].split("_")[0].split("/")
year_of_clips=str(year_of_clips[len(year_of_clips)-1])
date_of_clips=str(mov_paths[0].split("_")[1])
final_date_clips=year_of_clips+'_'+date_of_clips
print(final_date_clips)

# Asks user to select from a choice of 3 different resolutions for the combined footage
answer=int(input("\nWhat resolution would you like for the resultant video?\n   [1] 1920x1080\n   [2] 1280x720\n   [3] 720x480\n> "))
# answer=3
size=[]
size=res_switch(answer)
size1=size[1],size[0]
size2=(int(size1[0]*.22),int(size1[1]*.1875))
print("\n")

# Combines all A and B footage into single clips then adds them to a list, B footage is centered at bottom
# Clip count should always end up being half of mov_paths as every clip is
#   a combination of A and B footage
while True:
    print("clip_count= ",clip_count,"\nmov_paths= ", len(mov_paths))
    if clip_count==len(mov_paths)/2:
        break
    clip1=VideoFileClip(mov_paths[count],audio=True,target_resolution=size1)
    clip2=VideoFileClip(mov_paths[count+1],audio=False,target_resolution=size2)

    final_clip=CompositeVideoClip([clip1,clip2.set_pos(("center","bottom"))])
    clips.append(final_clip)
    count+=2
    clip_count+=1

# Combines all clips into a single moviepy object
final_clip=(concatenate_videoclips(clips))

# Writes or "renders" footage into a single mp4 file with the date, audio can be heard
#   if using VLC for playback, as far as I know its a common issue
final_clip.write_videofile((final_date_clips+"_all.mp4"), fps=30,audio=True)
