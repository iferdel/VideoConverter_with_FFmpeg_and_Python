from editor import VideoCropper, VideoTrimmer
from effects import VideoEffects
import multiprocessing

def trimmer():
    trim = VideoTrimmer(pattern='.*((?=.mp4|.MP4|.mov|.MOV))', 
                        input_folder='InputToTrim', output_folder='OutputFromTrim', ffmpeg_quiet_mode=True) 
    print(trim.__str__())
    print(trim.__dict__)
    df = trim.trimmer_dataframe()
    p = multiprocessing.Process(target=trim.ffmpeg_call, args=(df, 'ffmpeg_trim_call'))
    p.start()
    p.join()

def cropper():
    crop = VideoCropper(pattern='.*((?=.mp4|.MP4|.mov|.MOV))', 
                        input_folder='OutputFromTrim', output_folder='OutputFromCrop', ffmpeg_quiet_mode=True)
    print(crop.__str__())
    df = crop.cropper_dataframe()
    p = multiprocessing.Process(target=crop.ffmpeg_call, args=(df, 'ffmpeg_crop_call'))
    p.start()
    p.join()

def speed_effects(speed_rate):
    effects = VideoEffects(pattern='.*((?=.mp4|.MP4|.mov|.MOV))', 
                           input_folder='OutputFromCrop', output_folder='OutputFromEffects', ffmpeg_quiet_mode=True)
    print(effects.__str__())
    df = effects.speed_rate_dataframe(speed_rate)
    p = multiprocessing.Process(target=effects.ffmpeg_call, args=(df, 'ffmpeg_effects_call'))
    p.start()
    p.join()

def main():
    trimmer()
    cropper()
    speed_effects(0.8)
    
if __name__=='__main__':
    main()