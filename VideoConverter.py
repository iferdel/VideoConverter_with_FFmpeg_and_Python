import os
import re
import subprocess
from pathlib import Path


class VideoConverter():

    def __init__(self, pattern, from_trim_output=False):
        self.pattern = pattern
        self.from_trim_output = from_trim_output
        if self.from_trim_output=='N': self.path = os.getcwd()  
        elif self.from_trim_output=='y': 
            self.path = os.path.join(os.getcwd(), 'OutputFromTrim')
            os.chdir(self.path)
        else: self.path = os.getcwd() 
        self.dirs = os.listdir(self.path)
        self.files = [file for file in self.dirs if re.match(self.pattern, file) is not None]
        
    def resolution_data(self):
        self.resolution = [(subprocess.check_output(f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {file}',
                            shell=True)).decode('utf-8').strip() for file in self.files]

    def set_output_folder(self): #same function name for base and subclass?
        self.output_folder = 'OutputFromCrop'
        if self.from_trim_output=='y':
            if self.output_folder not in os.listdir(Path(self.path).parents[0]): 
                os.mkdir(os.path.join(Path(self.path).parents[0], self.output_folder))
            self.path = os.getcwd()
        else:
            if self.output_folder not in os.listdir(self.path): 
                os.mkdir(os.path.join(self.path, self.output_folder))

    def ffmpeg_call(self, dataframe, ffmpeg_call_column):
        [subprocess.run(f'{i}') for i in dataframe.loc[:,ffmpeg_call_column] if i is not None]


class VideoTrimmer(VideoConverter):

    def __init__(self):
        VideoConverter.__init__(self, pattern='.*((?=.mp4|.MP4|.mov|.MOV))')
        self.path = os.path.join(os.getcwd(), 'InputTotrim')
        self.dirs = os.listdir(self.path)
        self.files = [file for file in self.dirs if re.match(self.pattern, file) is not None]    
    
    def files_to_txt(self):   #si no activo video_data, esta función queda out...
        txt = ['README: Add a pair of values per file with pattern [ti] [tf] (brackets and white space are mandatory), '\
        'where ti: initial time; tf: final time. The pattern per variable (ti and tf) must be in the form of xx:xx:xx. '\
        'Multiple trim are allowed if separated with a white space']
        txt.extend(self.files)
        with open(os.path.join(self.path, "files_to_txt.txt"), "w") as outfile: outfile.write("\n".join(txt)) 

    def txt_file_read(self):
        with open(os.path.join(self.path, "files_to_txt.txt")) as f:
            next(f)
            txt = [i.split('\n')[0].strip() for i in [line for line in f]]
            txt = [item.split(' ') for item in txt]
            files = [item[0] for item in txt]
            trim_parameter = [list(filter(None, item[1:])) for item in txt]
            return files, trim_parameter
    
    def set_output_folder(self):
        self.output_folder = 'OutputFromTrim'
        if self.output_folder not in os.listdir(Path(self.path).parents[0]): 
            os.mkdir(os.path.join(Path(self.path).parents[0], self.output_folder))
        os.chdir(self.path)
    
    def ffmpeg_call(self, dataframe, ffmpeg_call_column):
        super(VideoTrimmer, self).ffmpeg_call(dataframe, ffmpeg_call_column)
        os.chdir(Path(self.path).parents[0])