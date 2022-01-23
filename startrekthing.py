import os, pymkv, srt

directory = os.getcwd()

def extract_subs(filename, track_number):
    print('Extracting subs for ' + filename)
    command = 'mkvextract tracks "' + filename + '" ' + str(track_number) + ':' + filename[:-4] + '.srt'
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


def fix_subs(filename):
    print('Fixing subs')
    srt_file = open(filename[:-4] + '.srt', 'r')
    raw_srt = srt_file.read()
    srt_file.close()
    srt_start = raw_srt.find('1') # idk
    raw_srt = raw_srt[srt_start:]
    sub_generator = srt.parse(raw_srt)
    subtitles = list(sub_generator)
    # group sub entries with identical timestamps
    time_values = set(map(lambda x: x.start, subtitles)) # yoink
    grouped_sub_ids = [[subtitle.index for subtitle in subtitles if subtitle.start == time] for time in time_values]
    # combining sub entries could decrement the overall number of subs and mess up the indexing
    # so just in case thisll sort the groups and work from the end
    sorted_grouped_sub_ids = sorted(grouped_sub_ids, key=lambda d: d[0], reverse=True)
    print('Found ' + str(len(sorted_grouped_sub_ids)) + ' groups to fix')
    for group in sorted_grouped_sub_ids:
        if len(group) == 1:
            continue
        fix_lines(subtitles, group)
    # overwrite the file with the fixed subs
    srt_file = open(filename[:-4] + '.srt', 'w')
    srt_file.write(srt.compose(subtitles))
    srt_file.close()
    print('Subs Fixed!')

    
def fix_lines(subtitles, line_group):
    for i in range(line_group[1], line_group[-1] + 1):
        subtitles[line_group[0] - 1].content = subtitles[line_group[0] - 1].content + '<br />' + subtitles[i - 1].content
        subtitles[i - 1].content = ''

for entry in os.scandir(directory):
    if entry.path.endswith(".mkv") and entry.is_file():
        track_number = determine_track_number(entry.path)
        extract_subs(entry.path, track_number)
        fix_subs(entry.path)




