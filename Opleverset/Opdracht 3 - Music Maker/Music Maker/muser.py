import glob as gl
import os
import tomita.legacy.pysynth as ps

class Muser:
    def generate (self, song, name):
        ps.make_wav(
            song,
            bpm=60,
            transpose=1,
            pause=0.1,
            boost=1.15,
            repeat=0,
            fn=str(name)+'.wav',
            silent=False
        )