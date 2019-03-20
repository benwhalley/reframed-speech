#!/usr/local/bin/python


"""
Script to select audio chunks from speech files.
"""

import operator
import os
import pydub
import itertools

# set this to wherever you want the new sliced audio files saving
# and run the script from the director containing the raw audio files
# (or a copy to be safe)


COPY_OF_ALL_AUDIO_PATH = "/Volumes/G-DRIVE with Thunderbolt/Reframed1_Audio/audio/"
NEWFILESPATH = "/Volumes/G-DRIVE with Thunderbolt/Reframed1_Audio/sliced/"


os.chdir(COPY_OF_ALL_AUDIO_PATH)

onlyfiles = sorted(
    [
        i
        for i in [f for f in os.listdir(COPY_OF_ALL_AUDIO_PATH) if os.path.isfile(f)]
        if i[0] != "."
    ]
)


# XXX can restart from a last position if interrupted
lastfilecomplete = "10383-session-2904-06-14.m4a"
onlyfiles = onlyfiles[onlyfiles.index(lastfilecomplete) + 1 :]


filesandextensions = zip(
    onlyfiles,
    [(i, j.replace(".", "").lower()) for i, j in map(os.path.splitext, onlyfiles)],
)
audiofiles = [i for i in filesandextensions if i[1][1] in "mp3 mp4 m4a".split()]


# take a slice from a list by passing a tuple
tupslice = lambda l, tup: l[tup[0] : tup[1]]


m = lambda i: i * 1000 * 60  # calculate n miliseconds for n mintes


def make_chunks(audio, chunks):
    return [tupslice(audio, i) for i in chunks]


def join_chunks(audiochunks, gap=10):
    gap = pydub.AudioSegment.silent(1000 * gap)  # 10 sec gap
    slices = itertools.chain(*itertools.izip(audiochunks, itertools.repeat(gap)))
    return reduce(operator.add, slices)


def choose_regular_chunks(audio, chunkinterval, chunkduration, start=1):
    totalmins = len(audio) / 1000 / 60
    lastchunkstart = totalmins - chunkduration
    return [
        (m(i), m(i + chunkduration))
        for i in range(start, lastchunkstart, chunkinterval)
    ]


def write_chunks(audiochunks, name, save_spliced=True, gap=5):
    spliced = join_chunks(audiochunks, gap)
    subpath = os.path.join(NEWFILESPATH, n)
    try:
        os.mkdir(subpath)
    except Exception as e:
        print(e)

    with open(os.path.join(subpath, n + ".txt"), "w") as f:
        chunktomin = lambda x: (x[0] / 1000 / 60, x[1] / 1000 / 60)
        f.write("Original file name: " + orig + "\n")
        f.write(
            "Chunk timings in minutes: " + str(list(map(chunktomin, chunks))) + "\n"
        )
        f.write("Original audio length in minutes: " + str(len(raw) / 1000 / 60))

    if save_spliced:
        spliced.export(os.path.join(subpath, n + os.extsep + "wav"), format="wav")

    [
        j.export(os.path.join(subpath, "chunk_{}.wav".format(i)), format="wav")
        for i, j in enumerate(audiochunks)
    ]


for orig, tup in audiofiles:
    print(orig)
    n, ext = tup
    simplername = n.lower().replace(" ", "-").replace(",", "")

    try:
        raw = pydub.AudioSegment.from_file(orig)
        raw.export(os.path.join(COPY_OF_ALL_AUDIO_PATH, simplername + ".m4a"))
        chunks = choose_regular_chunks(
            raw, 12, 4, 1
        )  # 12 interval, 4 min chunks, start at 1
        audiochunks = make_chunks(raw, chunks)
        write_chunks(audiochunks, simplername, save_spliced=False)

    except Exception as e:
        print(orig, e)
