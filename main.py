# this script in python automates short video creation, with wisper ai and text to speech, speech to text API

# import libraries for tiktok API
import requests, base64, random, argparse, os, playsound, time, re, textwrap
#personnal libraries
import tiktokAPI.main as TTA
from moviepy.editor import *
import math
import whisper_timestamped
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop
from moviepy.editor import VideoFileClip, clips_array
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.all import resize
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import TextClip
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

def From_Text():
        # API Token
        APItoken = "9ff9907f893258c532a0550ea1ad87f7"

        # text = input ("Enter the text you want to add to the video: ")
        text = "Did you know ? There is no such thing as a fish. Fish is a term used to describe a wide variety of aquatic animals. There are over 30,000 species of fish, including sharks, rays, and lampreys."

        if text[-1] == ".":
                text = text[:-1]
        sentences = text.split(".")
        audio_files = []
        for x in range(len(sentences)):
                TTA.tts(APItoken, "en_us_006", sentences[x], "VoiceOver/output/voice" + str(x) + ".mp3")
                audio_files.append("VoiceOver/output/voice" + str(x) + ".mp3")
        audios = []
        for audio in audio_files:
                audios.append(AudioFileClip(audio))
        audioClips = concatenate_audioclips([audio for audio in audios])
        audioClips.write_audiofile("VoiceOver/output/voice.mp3")

        # get the audio & video duration
        audiofile = AudioFileClip("VoiceOver/output/voice.mp3")
        sound_duration = math.floor(audiofile.duration) + 1
        videofile = VideoFileClip("VoiceOver/sources/video.mp4")
        video_duration = math.floor(videofile.duration)
        music = AudioFileClip("VoiceOver/sources/music.mp3").subclip(0, sound_duration)
        music = music.volumex(0.1)

        # getting a random position in the video
        start = random.randint(0, video_duration - sound_duration)

        # mixing audio with music
        mixed_audio = CompositeAudioClip([music, audiofile])
        mixed_audio.fps = audiofile.fps
        # save the mixed audio
        mixed_audio.write_audiofile("VoiceOver/output/mixed_audio.mp3")

        # mix the video with the audio
        videofile = videofile.subclip(start, start + sound_duration)
        videofile.audio = mixed_audio
        videofile.write_videofile("VoiceOver/output/mixed_video.mp4")

        clip = VideoFileClip("VoiceOver/output/mixed_video.mp4")
        (w, h) = clip.size
        clip = crop(clip, width=1080, height=1920, x_center=w / 2, y_center=h / 2)

        # second step is to add the text to the video with wisper AI
        audio = "VoiceOver/output/voice.mp3"

        # generataing the subtitles in english
        model = whisper_timestamped.load_model("base")
        result = whisper_timestamped.transcribe(model, audio)

        # adding subtitles to the video
        subs = []
        subs.append(clip)
        for segment in result["segments"]:
                for word in segment["words"]:
                        text = word["text"].upper()
                        start = word["start"]
                        end = word["end"]
                        duration = end - start
                        txt_clip = TextClip(text, fontsize=70, color='white', font='Amiri-Bold',bg_color="black").set_duration(duration)
                        txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(start)
                        subs.append(txt_clip)
        clip = CompositeVideoClip(subs)
        # write out the final video
        clip.write_videofile("VoiceOver/output/final.mp4",threads = 16,codec="libx264", fps=24)


def mount_from_video(video_entry, iteration):
        """Takes a video of 25 sec max and add subtitles and music to it, and a fun video on top of the screen"""
        print("TITLE WILL BE :"+"FV/output_FV/LastVideo/final"+str(iteration)+".mp4")
        #get a video from src_fv
        # videofile = VideoFileClip(video_entry)
        # #get the duration of the video
        # video_duration = math.floor(videofile.duration)
        # #if the video is less or equal to 25 sec, we don't need to crop it
        # if video_duration > 25:
        #         start = random.randint(0, video_duration - 25)
        #         videofile = videofile.subclip(start, start + 25)
        #         video_duration = math.floor(videofile.duration)
        video_duration = video_entry.duration
        print("video duration will be INSIDE FROMVIDEO :",video_duration)
        # This function generate subtitles from a video, add music and another video on top of the screen
        music = AudioFileClip("FV/src_fv/music.mp3").subclip(0, video_duration)
        # print("video duration will be  :",video_duration)
        #choose a random fun video from the fun 
        rndchc = random.choice(os.listdir("FV/src_fv/fun_vid_container"))
        print("fun video chosen is :",rndchc)
        funvideo = VideoFileClip("FV/src_fv/fun_vid_container/" + rndchc)
        # getting a random position in the fun video
        funvideoduration = math.floor(funvideo.duration)
        #choose a random position in the fun video
        start = random.randint(0, funvideoduration - video_duration)
        funvideo = funvideo.subclip(start, start + video_duration)
        print("funvideo duration will be  :",funvideo.duration)
        funvideo.audio = music
        funvideo.audio = funvideo.audio.volumex(0.1)

        #write out the audio
        video_entry.audio.write_audiofile("FV/output_FV/audio.mp3")
        #get the audio from the video
        todub_audio = "FV/output_FV/audio.mp3"
        #generate subtitles
        model = whisper_timestamped.load_model("base")
        result = whisper_timestamped.transcribe(model, todub_audio)
        # adding subtitles to the video
        subs = []
        subs.append(video_entry)
        for segment in result["segments"]:
                for word in segment["words"]:
                        text = word["text"].upper()
                        start = word["start"]
                        end = word["end"]
                        duration = end - start
                        txt_clip = TextClip(text, fontsize=70, color='white', font='Amiri-Bold',bg_color="black").set_duration(duration)
                        txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(start)
                        subs.append(txt_clip)
        video_entry = CompositeVideoClip(subs)
        # write out the final video
        final_clip = clips_array([ [video_entry],[funvideo]])
        # final_clip.write_videofile("FV/output_FV/concatNotCropped.mp4", threads = 16,codec="libx264", fps=24)
        # crop_video("FV/output_FV/concatNotCropped.mp4", "FV/output_FV/LastVideo/final"+str(iteration)+".mp4")
        width, height = final_clip.size
        target_width = int(height * 9/16)
        target_height = height
        crop_x1 = (width - target_width) / 2
        crop_x2 = width - crop_x1
        crop_y1 = 0
        crop_y2 = height
        cropped_video = final_clip.crop(x1=crop_x1, y1=crop_y1, x2=crop_x2, y2=crop_y2)
        cropped_video.write_videofile("FV/output_FV/LastVideo/final"+str(iteration)+".mp4", threads = 16,codec="libx264", fps=24)

def cut_n_videos(entry_path, output_path="FV/output_fv/LastVideo",offset=0) :
        """takes the video in entry_path and cut it in n videos of 59 seconds each"""
        video = VideoFileClip(entry_path)
        video_duration = math.floor(video.duration)
        #if the video is less or equal to 59 sec, we don't need to crop it
        if video_duration <= 59:
                mount_from_video(video, offset)
        #getting rid of the intro/credits
        video = video.subclip(5,video_duration-10)
        n = math.ceil(video_duration/59)
        video_duration = math.floor(video.duration)
        #mount each part of 60 s videos, the iteration var allow to restart the process from the middle of the video if the prgram crashed
        for i in range(n):
                #anew indice is needed to mount the video from the middle
                new_indice = i+offset
                #if it's the end of the video, we mount the last part
                if video_duration <= (new_indice+1)*59:
                        mount_from_video(video.subclip(new_indice*59, (new_indice+1)*59), offset)
                else :
                        subclip = video.subclip(new_indice*59, (new_indice+1)*59)
                        mount_from_video(subclip, new_indice)

cut_n_videos("FV/src_fv/lastvideo.mp4",offset=5)
# From_Text()
