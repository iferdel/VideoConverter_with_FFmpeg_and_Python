from converter_base import VideoCropper, VideoTrimmer
import pandas as pd
import numpy as np
import os
from pathlib import Path
import multiprocessing

def trim_dataframe(file_list, trim_list):
    df = pd.DataFrame(data={'file': file_list, 'ti-tf': trim_list})
    df = df.apply(pd.Series.explode)
    df['tf'] = df['ti-tf'].shift(-1)
    df = df.iloc[:-1]
    df = df[0::2]
    df.rename(columns={'ti-tf': 'ti'}, inplace=True) 
    df['ti'] = df['ti'].str.strip('[]')
    df['tf'] = df['tf'].str.strip('[]')
    return df
    
def resolution_dataframe(file_list, resolution_list):
    df = pd.DataFrame(data={'file': file_list, 'resolution': resolution_list})
    df['resolution'] = df.loc[:, 'resolution'].str.findall('(\d{4}x\d{4})').str[0]
    df['resolution_call'] = np.where(df.loc[:, 'resolution']=='3328x2496', 1, 0)
    return df

def trimmer_converter():
    trim = VideoTrimmer(pattern='.*((?=.mp4|.MP4|.mov|.MOV))')   #this three lines looks like inicialization, so they could be compressed
    trim.set_input_folder(input_folder='InputToTrim')
    trim.set_output_folder(output_folder='OutputFromTrim')
    trim.files_to_txt()
    df = trim_dataframe(trim.txt_file_read()[0], trim.txt_file_read()[1])
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

def crop_converter():
    crop = VideoCropper(pattern='.*((?=.mp4|.MP4|.mov|.MOV))')
    crop.set_input_folder(input_folder='OutputFromTrim')
    crop.set_output_folder(output_folder='OutputFromCrop')
    crop.resolution_data()
    df = resolution_dataframe(crop.files, crop.resolution)
    df['file'] = df.loc[:,'file'].str.split(".")
    df['crop_output_file'] = df.loc[:,'file'].str[0]+'_Cropped' + '.' + df.loc[:,'file'].iloc[0][1]
    df['file'] = df.loc[:,'file'].str[0] + '.' + df.loc[:,'file'].iloc[0][1]
    df = df.reset_index(drop=True)
    for item in df.index:   
        df.loc[item, 'ffmpeg_crop_call'] = np.where(df.loc[item]['resolution'] == '3328x2496', 
                                                      'ffmpeg -i {} -vf "crop=1080:1920:1124:253" -b:v 5M {}'.format(os.path.join(crop.files_input_path, df.loc[item,'file']), 
                                                       os.path.join(crop.files_output_path, df.loc[item,'crop_output_file'])),
                                                      'ffmpeg -i {} -b:v 5M {}'.format(os.path.join(crop.files_input_path, df.loc[item,'file']),
                                                       os.path.join(crop.files_output_path, df.loc[item,'crop_output_file'])))
    p = multiprocessing.Process(target=crop.ffmpeg_call, args=(df, 'ffmpeg_crop_call'))
    p.start()
    
def main():
    trimmer_converter()
    crop_converter()

if __name__=='__main__':
    main()