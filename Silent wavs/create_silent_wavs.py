import wave, struct, sys, pathlib
names = ["pz6_gun_load_voice.wav","pz6_gun_loaded_voice.wav",
         "GOrder2.wav","GOrder3.wav","GOrder4.wav","GOrder5.wav"]
pathlib.Path("Resources").mkdir(exist_ok=True)
for n in names:
    with wave.open(f"Resources/{n}",'w') as w:
        w.setparams((1,2,22050,0,'NONE','not compressed'))
        silence = struct.pack('<h',0)
        w.writeframes(silence*2205)   # 0.1 s of silence
print("6 silent wavs created")
