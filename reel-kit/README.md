# reel-kit (Quiet Verse)
Code that builds the vector-background reels. Library only; no builds run on import.
- compose.py: background, bubbles, watermark, character cutouts (cut/*.png: krishna, krishna_flute, shiva, man, man_full, man_pray).
- vreel.py: `sp(theme,seed,who,char,text,ch_h=,extra=,bs=)` makes one scene; `build([(audio_path, scene), ...], end_scene, out_mp4)` renders 1080x1920 24fps with the audio. `end_fg(lines)` makes the end card. See the bottom of git history (commit "Week 2 reels: switch to vector backgrounds") for the Week 2 scene lists.
- Voices (ElevenLabs, model eleven_v4): Krishna = Ishaan, voice_id niLTODfB1j2nXIbp3M14; the man = Keshav, voice_id WHvZF5poLGMBdCKsjSGC.
- Style: bubbles cream (man), gold (Krishna), light blue (Shiva); watermark @thequietverse.ultimate; end card "Follow @thequietverse.ultimate".
Usage: `import sys; sys.path.insert(0,'reel-kit'); from vreel import *` (needs numpy, opencv, pillow, ffmpeg, Inter fonts).
