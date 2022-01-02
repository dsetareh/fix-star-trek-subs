import os, pymkv

directory = os.getcwd()

def extract_subs(filename, track_number):
    print('Extracting subs for ' + filename)
    command = 'mkvextract tracks ' + filename + ' ' + str(track_number) + ':' + filename[:-4] + '.srt'
    stream = os.popen(command)
    stream.read() # scuffed wait for command to finish

# this is slow asf
def determine_track_number(filename):
    print('Determining english subs track id for ' + filename)
    mkv = pymkv.MKVFile(filename)
    for track in mkv.tracks:
        if track.track_type == 'subtitles' and track.language == 'eng':
            print('Found eng subs on Track ' + str(track.track_id))
            return track.track_id
    print('No english subtitles found, quitting')
    exit(1)

for entry in os.scandir(directory):
    if entry.path.endswith(".mkv") and entry.is_file():
        track_number = determine_track_number(entry.path)
        extract_subs(entry.path, track_number)




