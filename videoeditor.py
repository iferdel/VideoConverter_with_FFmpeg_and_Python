import os
import re
import subprocess


class VideoEditor():

    def __init__(self, pattern):
        self.pattern = pattern
        self.path = os.getcwd()

    def set_input_folder(self, input_folder):
        self.input_folder = input_folder
        if self.input_folder not in os.listdir(self.path):
            os.mkdir(self.input_folder)
        self.files_input_path = os.path.join(self.path, self.input_folder)
        del input_folder
        self.dirs = os.listdir(self.files_input_path)
        self.files = [file for file in self.dirs if re.match(self.pattern, file) is not None]
    
    def set_output_folder(self, output_folder):
        self.output_folder = output_folder
        if self.output_folder not in os.listdir(self.path):
            os.mkdir(self.output_folder)
        self.files_output_path = os.path.join(self.path, self.output_folder)
        
    def ffmpeg_call(self, dataframe, ffmpeg_call_column):
        [subprocess.run(f'{i}') for i in dataframe.loc[:,ffmpeg_call_column] if i is not None]


class VideoCropper(VideoEditor):
        
    def resolution_data(self): 
        self.resolution = [(subprocess.check_output(f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {os.path.join(self.files_input_path, file)}',
                            shell=True)).decode('utf-8').strip() for file in self.files]
                
    # def crop_position(self, x_from, y_from)


class VideoTrimmer(VideoEditor):
    
    def files_to_txt(self): #podría ser inicializador
        if 'files_to_txt.txt' not in os.listdir(self.files_input_path):
            txt = ['README: Add a pair of values per file with pattern [ti] [tf] (brackets and white space are mandatory), '\
            'where ti: initial time; tf: final time. The pattern per variable (ti and tf) must be in the form of xx:xx:xx. '\
            'Multiple trim are allowed if separated with a white space']
            txt.extend(self.files)
            with open(os.path.join(self.path, "files_to_txt.txt"), "w") as outfile: outfile.write("\n".join(txt)) 
        # elif self.files not in with open(os.path.join(self.path, "files_to_txt.txt"), "w") as outfile: outfile.write("\n".join(txt)): rewrite # algo así TODO
        # else: input("Make sure to define de trim margins. Press enter to continue...")
   
    def txt_file_read(self):
        with open(os.path.join(self.files_input_path, "files_to_txt.txt")) as f:
            next(f)
            txt = [i.split('\n')[0].strip() for i in [line for line in f]]
            txt = [item.split(' ') for item in txt]
            files = [item[0] for item in txt]
            trim_parameter = [list(filter(None, item[1:])) for item in txt]
            return files, trim_parameter


# class SlowFastMotion(VideoEditor): TODO    

# if __name__ == '__main__':
#     c = VideoCropper(pattern='.*((?=.mp4|.MP4|.mov|.MOV))')
#     c.set_input_folder('OutputFromTrim')
#     c.set_output_folder('OutputFromCrop')
#     c.resolution_data()
#     print(c.path, c.files_input_path, c.files_output_path, c.files, c.resolution) 


if __name__ == '__main__':
    c = VideoTrimmer(pattern='.*((?=.mp4|.MP4|.mov|.MOV))')
    c.set_input_folder('InputToTrim')
    c.set_output_folder('OutputFromTrim')
    c.files_to_txt()
    c.txt_file_read()
    print(c.path, c.files_input_path, c.files_output_path, c.files)