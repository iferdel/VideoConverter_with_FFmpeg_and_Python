from editor import VideoEditor
import pandas as pd
import os


class VideoEffects(VideoEditor):
    
    def speed_rate_dataframe(self, rate):
        self.speed_rate = str(rate)
        df = pd.DataFrame({'file': self.files})
        df['file'] = df['file'].str.split(".")
        df['effects_output_file'] = df['file'].str[0] + '_speed_rate_at_{}.'.format(self.speed_rate) + df['file'].iloc[0][1]
        df['file'] = df.loc[:,'file'].str[0] + '.' + df.loc[:,'file'].iloc[0][1]
        for item in df.index:
            df.loc[item, 'ffmpeg_effects_call'] = 'ffmpeg -i {} -filter_complex \
                                            "[0:v]trim=start=0,setpts=PTS-STARTPTS[v1]; \
                                            [v1]setpts=PTS/{}[speed_rate]; \
                                            [speed_rate]concat=n=1:v=1:a=0[out]" \
                                            -map "[out]" -b:v 5M {} {}'.format(os.path.join(self.files_input_path, df.loc[item, 'file'])
                                            , self.speed_rate, self.quiet_mode, os.path.join(self.files_output_path, df.loc[item,'effects_output_file']))
        return df