from VideoConverter import VideoConverter, VideoTrimmer
import pandas as pd
import numpy as np
import os
from pathlib import Path

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
    converter = VideoTrimmer()
    if 'files_to_txt.txt' not in os.listdir(converter.path): converter.files_to_txt()
    else: input("Make sure to define de trim margins. Press enter to continue...")
    df = trim_dataframe(converter.txt_file_read()[0], converter.txt_file_read()[1])
    converter.set_output_folder()
    df['file'] = df.loc[:,'file'].str.split(".")
    df['trim_output_file'] = df.loc[:,'file'].str[0]+'_ti_'+df.loc[:,'ti']+'_tf_'+df.loc[:,'tf']+ \
                                       '.'+df.loc[:,'file'].iloc[0][1]
    df['trim_output_file'] = [x.replace(':', '_') for x  in df.loc[:,'trim_output_file'].to_numpy()]
    df['file'] = df.loc[:,'file'].str[0]+'.'+df.loc[:,'file'].iloc[0][1]
    df = df.reset_index(drop=True)
    for item in df.index:
        df.loc[item, 'ffmpeg_trim_call'] = 'ffmpeg -ss {} -i {} -to {} -minrate 10M -c:v copy {}'.format(
                                  df.loc[item,'ti'], df.loc[item,'file'], df.loc[item,'tf'], 
                                  os.path.join(Path(converter.path).parents[0], converter.output_folder, df.loc[item,'trim_output_file']))
    converter.ffmpeg_call(dataframe=df, ffmpeg_call_column='ffmpeg_trim_call')

def crop_converter():
    choices = ['y','N']
    from_trim_output_user_input = None
    while from_trim_output_user_input not in choices:
        from_trim_output_user_input = input('Convert files from trim output folder? [y/N]')
        if from_trim_output_user_input not in choices: print('Incorrect answer')
    converter = VideoConverter(pattern='.*((?=.mp4|.MP4|.mov|.MOV))', from_trim_output=from_trim_output_user_input)
    converter.resolution_data()
    df = resolution_dataframe(converter.files, converter.resolution)
    converter.set_output_folder()
    df['file'] = df.loc[:,'file'].str.split(".")
    df['crop_output_file'] = df.loc[:,'file'].str[0]+'_Cropped'+'.'+df.loc[:,'file'].iloc[0][1]
    df['file'] = df.loc[:,'file'].str[0]+'.'+df.loc[:,'file'].iloc[0][1]
    df = df.reset_index(drop=True)
    for item in df.index:
        if converter.from_trim_output == 'y':
            df.loc[item, 'ffmpeg_crop_call'] = np.where(df.loc[item]['resolution'] == '3328x2496', 
                                                      'ffmpeg -i {} -vf "crop=1080:1920:1124:253" -b:v 5M {}'.format(df.loc[item,'file'], 
                                                       os.path.join(Path(converter.path).parents[0], converter.output_folder, df.loc[item,'crop_output_file'])),
                                                      'ffmpeg -i {} -b:v 5M {}'.format(df.loc[item,'file'],
                                                       os.path.join(Path(converter.path).parents[0], converter.output_folder, df.loc[item,'crop_output_file'])))
        else:
            df.loc[item, 'ffmpeg_crop_call'] = np.where(df.loc[item]['resolution'] == '3328x2496', 
                                                      'ffmpeg -i {} -vf "crop=1080:1920:1124:253" -b:v 5M {}'.format(df.loc[item,'file'], 
                                                       os.path.join(converter.path, converter.output_folder, df.loc[item,'crop_output_file'])),
                                                      'ffmpeg -i {} -b:v 5M {}'.format(df.loc[item,'file'],
                                                       os.path.join(converter.path, converter.output_folder, df.loc[item,'crop_output_file'])))
    converter.ffmpeg_call(dataframe=df, ffmpeg_call_column='ffmpeg_crop_call')

def main():
    trimmer_converter()
    crop_converter()

if __name__=='__main__':
    main()