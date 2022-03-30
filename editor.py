import os
import re
import subprocess
import pandas as pd
import numpy as np


class VideoEditor():

    def __init__(self, pattern, input_folder, output_folder):
        self.pattern = pattern
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.path = os.getcwd()
        
        if self.input_folder not in os.listdir(self.path): os.mkdir(self.input_folder)
        if self.output_folder not in os.listdir(self.path): os.mkdir(self.output_folder)

        self.files_input_path = os.path.join(self.path, self.input_folder)
        self.files_output_path = os.path.join(self.path, self.output_folder)

        self.dirs = os.listdir(self.files_input_path)
        self.files = [file for file in self.dirs if re.match(self.pattern, file) is not None]     
        
    def ffmpeg_call(self, dataframe, ffmpeg_call_column):
        [subprocess.run(f'{i}') for i in dataframe.loc[:,ffmpeg_call_column] if i is not None]


class VideoCropper(VideoEditor):

    def __init__(self, pattern, input_folder, output_folder):
        super(VideoCropper, self).__init__(pattern, input_folder, output_folder)    
        
        self.resolution = [(subprocess.check_output(f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {os.path.join(self.files_input_path, file)}',
                            shell=True)).decode('utf-8').strip() for file in self.files]
    
    def cropper_dataframe(self):
        df = pd.DataFrame(data={'file': self.files, 'resolution': self.resolution})
        df['resolution'] = df.loc[:, 'resolution'].str.findall('(\d{4}x\d{4})').str[0]
        df['file'] = df.loc[:,'file'].str.split(".")
        df['crop_output_file'] = df.loc[:,'file'].str[0]+'_Cropped' + '.' + df.loc[:,'file'].iloc[0][1]
        df['file'] = df.loc[:,'file'].str[0] + '.' + df.loc[:,'file'].iloc[0][1]
        df = df.reset_index(drop=True)
        for item in df.index:   
            df.loc[item, 'ffmpeg_crop_call'] = np.where(df.loc[item]['resolution'] == '3328x2496', 
                                                        'ffmpeg -i {} -vf "crop=1080:1920:1124:253" -b:v 5M {}'.format(os.path.join(self.files_input_path, df.loc[item,'file']), 
                                                        os.path.join(self.files_output_path, df.loc[item,'crop_output_file'])),
                                                        'ffmpeg -i {} -b:v 5M {}'.format(os.path.join(self.files_input_path, df.loc[item,'file']),
                                                        os.path.join(self.files_output_path, df.loc[item,'crop_output_file'])))
        return df
    
#   TODO def cropper_boundaries(self) TODO


class VideoTrimmer(VideoEditor):
    
    def __init__(self, pattern, input_folder, output_folder):
        super(VideoTrimmer, self).__init__(pattern, input_folder, output_folder)

        if 'files_to_txt.txt' not in os.listdir(self.files_input_path):
            txt = ['README: Add a pair of values per file with pattern [ti] [tf] (brackets and white space are mandatory), '\
            'where ti: initial time; tf: final time. The pattern per variable (ti and tf) must be in the form of xx:xx:xx. '\
            'Multiple trim are allowed if separated with a white space']
            txt.extend(self.files)
            with open(os.path.join(self.path, "files_to_txt.txt"), "w") as outfile: outfile.write("\n".join(txt)) 
        else: input("Make sure to define de trim margins. Press enter to continue...")
   
    def trim_margins_from_file(self):
        with open(os.path.join(self.files_input_path, "files_to_txt.txt")) as f:
            next(f)
            txt = [i.split('\n')[0].strip() for i in [line for line in f]]
            txt = [item.split(' ') for item in txt]
            files = [item[0] for item in txt]
            trim_parameter = [list(filter(None, item[1:])) for item in txt]
            return files, trim_parameter