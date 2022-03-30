from editor import VideoCropper, VideoTrimmer
from effects import VideoEffects
import pandas as pd
import os
import multiprocessing

def trim_dataframe(file_list, trim_list):
    df = pd.DataFrame(data={'file': file_list, 'ti-tf': trim_list})
    df = df.apply(pd.Series.explode)
    df['tf'] = df['ti-tf'].shift(-1) #shift(-1) to generate the pattern ti-tf
    df.rename(columns={'ti-tf': 'ti'}, inplace=True)
    df = df.iloc[:-1] # remove last row
    df = df[0::2] # take back only the rows with pair indexes from the explode (to avoid having tf-ti pattern)
    df['ti'] = df['ti'].str.strip('[]'); df['tf'] = df['tf'].str.strip('[]') #strip brackets from trim range as they are not included in ffmpeg syntax 
    return df

def trimmer():
    trim = VideoTrimmer(pattern='.*((?=.mp4|.MP4|.mov|.MOV))', input_folder='InputToTrim', output_folder='OutputFromTrim') 
    df = trim_dataframe(file_list=trim.trim_margins_from_file()[0], trim_list=trim.trim_margins_from_file()[1])
    df['file'] = df.loc[:,'file'].str.split(".")
    df['trim_output_file'] = df.loc[:, 'file'].str[0] + '_ti_' + df.loc[:, 'ti'] + '_tf_' + df.loc[:, 'tf'] + \
                                       '.' + df.loc[:, 'file'].iloc[0][1]
    df['trim_output_file'] = [x.replace(':', '_') for x  in df.loc[:, 'trim_output_file'].to_numpy()]
    df['file'] = df.loc[:,'file'].str[0]+'.'+df.loc[:,'file'].iloc[0][1]
    df = df.reset_index(drop=True)
    for item in df.index:
        df.loc[item, 'ffmpeg_trim_call'] = 'ffmpeg -ss {} -i {} -to {} -minrate 10M -c:v copy {}'.format(
                                  df.loc[item,'ti'], os.path.join(trim.files_input_path, df.loc[item,'file']), df.loc[item,'tf'], 
                                  os.path.join(trim.files_output_path, df.loc[item,'trim_output_file']))
    p = multiprocessing.Process(target=trim.ffmpeg_call, args=(df, 'ffmpeg_trim_call'))
    p.start()

def cropper():
    crop = VideoCropper(pattern='.*((?=.mp4|.MP4|.mov|.MOV))', input_folder='OutputFromTrim', output_folder='OutputFromCrop')
    df = crop.cropper_dataframe()
    p = multiprocessing.Process(target=crop.ffmpeg_call, args=(df, 'ffmpeg_crop_call'))
    p.start()

def speed_effects(speed_rate):
    effects = VideoEffects(pattern='.*((?=.mp4|.MP4|.mov|.MOV))', input_folder='OutputFromCrop', output_folder='OutputFromEffects')
    df = effects.speed_rate_dataframe(speed_rate)
    p = multiprocessing.Process(target=effects.ffmpeg_call, args=(df, 'ffmpeg_effects_call'))
    p.start()

def main():
    trimmer()
    cropper()
    speed_effects(0.4)

if __name__=='__main__':
    main()