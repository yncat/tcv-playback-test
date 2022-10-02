from bass import pybass
import ctypes
import os
import subprocess
os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))

buf = []


def filecloseproc(user):
    return


def filelenproc(user):
    print("filelenproc")
    return 0


def filereadproc(buffer, length, user):
    print("readproc %s" % length)
    read = buf[0:length]
    del buf[0:length]
    print("remain %d" % len(buf))
    ctypes.memmove(buffer, ctypes.c_char_p(bytes(read)), len(read))
    print("returning %d" % len(read))
    return len(read)


def fileseekproc(offset, user):
    return False


fileprocs = pybass.BASS_FILEPROCS()
fileprocs.close = pybass.FILECLOSEPROC(filecloseproc)
fileprocs.length = pybass.FILELENPROC(filelenproc)
fileprocs.read = pybass.FILEREADPROC(filereadproc)
fileprocs.seek = pybass.FILESEEKPROC(fileseekproc)

ret = pybass.BASS_Init(-1, 44100, 0, 0, 0)
cmd = [
    "ffmpeg",
    "-i",
    "https://twitcasting.tv/zzz_dmsk/metastream.m3u8/?video=1",
    "-max_muxing_queue_size",
    "1024",
    "-codec:a",
    "libmp3lame",
    "-b:a",
    "192k",
    "-f",
    "mp3",
    "pipe:1"
]

played = False
fp = open("test.mp3", "wb")
popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
print("start loop")
while(True):
    bin = popen.stdout.read(2048)
    buf.extend(list(bin))
    fp.write(bin)
    print("buf length %s" % len(buf))
    if not played and len(buf) > 128000:
        print("play start")
        hstream = pybass.BASS_StreamCreateFileUser(
            pybass.STREAMFILE_BUFFERPUSH, pybass.BASS_STREAM_BLOCK, fileprocs, 0)
        print("hstream: %s" % hstream)
        ret = pybass.BASS_ChannelPlay(hstream, False)
        played = True
        print("start playing: %s" % ret)
    if played and len(buf) > 32000:
        ln = len(buf)
        read = bytes(buf[0:ln])
        del buf[0:ln]
        pybass.BASS_StreamPutFileData(
            hstream, ctypes.c_char_p(read), len(read))
        print("data put")
