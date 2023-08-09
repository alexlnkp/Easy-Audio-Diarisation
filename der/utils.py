from pydub import AudioSegment
from pyannote.audio import Pipeline
from pyannote.core import Segment
import argparse
import os

def convert_to_mono(audio_path):
    output_path = audio_path
    audio = AudioSegment.from_file(audio_path)
    if audio.channels != 1:
        mono_audio = audio.set_channels(1)

        output_path = os.path.join(
            os.path.dirname(audio_path), "mono_" +\
                  os.path.basename(audio_path)
        )

        mono_audio.export(output_path, format="wav")
    return output_path

class HTML:
    """
    #### A utility class for generating HTML elements and instructions.

    ## Attributes:
    - _input (:class:`str`): HTML heading element for the input section.
    - _output (:class:`str`): HTML heading element for the output section.
    - _instruct (:class:`str`): Instructions in HTML format.

    ## Methods:
    - _create_heading(text: `str`): Creates an HTML heading element with the specified text.

    ## Usage:
    ```cpp
        html = HTML()
        input_html = html._input
        output_html = html._output
        instructions_html = html._instruct
    ```
    """

    _instruct_styles = '''
        .ps1 {
            font-size: 18px;
            padding-top: 7px;
            padding-left: 10px;
        }
    '''

    _dbr = '<br/><br/>'

    def __init__(self) -> None:
        self._input = self._create_heading('Input')
        self._output = self._create_heading('Output')

        self._instruct =\
        f'''
        <style>{self._instruct_styles}</style>
        <p class="ps1">
        1. Visit <a href="https://hf.co/pyannote/speaker-diarization">hf.co/pyannote/speaker-diarization</a> and accept user conditions. {self._dbr}
        2. Visit <a href="https://hf.co/pyannote/segmentation">hf.co/pyannote/segmentation</a> and accept user conditions.               {self._dbr}
        3. Visit <a href="https://hf.co/settings/tokens">hf.co/settings/tokens</a> to create an access token.                            {self._dbr}
        4. Instantiate pretrained speaker diarization pipeline.                                                                          {self._dbr}
        </p>
        '''

    @staticmethod
    def _create_heading(text: str) -> str:
        return f'<h1 class="heading-style">{text}</h1>'
    
def argument_parser(args: dict) -> argparse.Namespace:
    """
    #### Parses command line arguments based on the provided argument dictionary.
    ## Args:
        args (:class:`dict`): A dictionary containing argument names and their options.
    ### Returns:
        :class:`argparse.Namespace`: An object containing the parsed command line arguments.
    """

    parser = argparse.ArgumentParser()
    for arg_name, arg_options in args.items():
        arg_type = arg_options.pop('type', None)
        if arg_type is str:
            arg_options['type'] = str
        parser.add_argument(f'--{arg_name}', **arg_options)
    return parser.parse_args()

load_audio = lambda audio_file: AudioSegment.from_wav(audio_file)

def load_diarization(audio_file, token, min_speakers=2, max_speakers=30):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=token)
    return pipeline(audio_file, min_speakers=min_speakers, max_speakers=max_speakers)

def dump_rttm(diarization, output_file):
    with open(output_file, 'w') as file:
        diarization.write_rttm(file)

def read_segments_from_rttm(rttm_file):
    segments = []
    with open(rttm_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            start_time = float(parts[3])
            end_time = start_time + float(parts[4])
            speaker_id = parts[7]
            segments.append((Segment(start_time, end_time), speaker_id))
    return segments

def save_segment(segment, audio, output_file):
    start_time_ms = int(segment.start * 1000)
    end_time_ms = int(segment.end * 1000)
    segment_audio = audio[start_time_ms:end_time_ms]
    segment_audio.export(output_file, format="wav")

def save_combined_audio(combined_audio, output_file):
    combined_audio.export(output_file, format="wav")