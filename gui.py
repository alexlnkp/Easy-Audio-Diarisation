import os
import sys
import gradio as gr
import der.globals
from tqdm import tqdm

cur_dir = os.getcwd()
sys.path.append(cur_dir)

from der.utils import HTML, argument_parser, convert_to_mono, load_audio, \
    load_diarization, dump_rttm, read_segments_from_rttm, save_combined_audio

os.environ['GRADIO_SERVER_PORT'] = '4444'

OUTPUTS_DIR = os.path.join(cur_dir, 'outputs')

os.makedirs(OUTPUTS_DIR, exist_ok  = True)

TITLE    = 'Easy-Audio-Diarization✨'
RTTMFILE = 'div.rttm'

cli_args = {
    'iscolab': {
        'action': 'store_true',
        'help': 'Specifies whether the code is running on Google Colab or not'
    },
    'paperspace': {
        'action': 'store_true',
        'help': 'Specifies whether the code is running on Paperspace or not'
    },
    'not-autolaunch': {
        'action': 'store_true',
        'help': 'Specifies whether to automatically open the Gradio browser or not/'
    },
    'theme': {
        'type': 'str',
        'default': 'gradio/soft'
    }
}

html = HTML()
args = argument_parser(cli_args)

#region Main functions
def stop_flag():
    der.globals.Stop = True

def process_speaker_diarization(audio_file: str, TOKEN: str, rttm_file: str = RTTMFILE, output_dir:str = OUTPUTS_DIR) -> list:
    der.globals.Stop = False

    if not audio_file: print('You have to upload the audio first!'); return audio_file
    if not TOKEN:      print('You have to input a token!');          return audio_file

    combined_list = []

    diarization = load_diarization(audio_file, TOKEN)
    dump_rttm(diarization, rttm_file)
    original_audio = load_audio(convert_to_mono(audio_file))
    segments = read_segments_from_rttm(rttm_file)
    os.makedirs(output_dir, exist_ok=True)
    combined_audios = {}

    with tqdm(total=len(segments), desc="Segment Export") as pbar:
        for idx, (segment, speaker_id) in enumerate(segments):
            if der.globals.Stop: return audio_file

            segment_folder= os.path.join(output_dir, speaker_id)
            os.makedirs(segment_folder, exist_ok=True)
            speaker_segment_file = os.path.join(segment_folder, f"speaker_{speaker_id}_{idx + 1}.wav")

            start_time_ms = int(segment.start * 1000)
            end_time_ms   = int(segment.end   * 1000)
            segment_audio = original_audio[start_time_ms:end_time_ms]

            segment_audio.export(speaker_segment_file, format="wav")

            if speaker_id not in combined_audios:
                combined_audios[speaker_id] = segment_audio
            else:
                combined_audios[speaker_id] += segment_audio

            pbar.update(1)

    print("Segment export completed.")

    with tqdm(total=len(combined_audios), desc="Combined Audio Export") as pbar:
        for speaker_id, combined_audio in combined_audios.items():
            if der.globals.Stop: return audio_file

            combined_folder = os.path.join(output_dir, speaker_id, "combined")
            os.makedirs(combined_folder, exist_ok=True)

            combined_audio_file = os.path.join(combined_folder, f"speaker_{speaker_id}_combined.wav")
            combined_list.append(combined_audio_file)

            yield combined_list

            save_combined_audio(combined_audio, combined_audio_file)
            pbar.update(1)

    print("Combined audio export completed.")
    return combined_list
#endregion

#region Gradio
def GradioInit(Theme: str) -> gr.Blocks:
    """
    ## Gradio initiation function
    ### Args:
    - Theme (:class:`str`): Gradio theme. Format: `'author/name'`
      - You can get Gradio themes at https://huggingface.co/spaces/gradio/theme-gallery
    """

    with gr.Blocks(theme=Theme, title=TITLE) as app:
        with gr.Column():
            with gr.Row():
                gr.HTML(html._input)
                gr.HTML(html._output)

            with gr.Row():
                input_audio    = gr.Audio(
                    label      = 'Upload files',
                    type       = 'filepath'
                )
                output_audio   = gr.File(
                    label      = 'Download files',
                    type       = 'file',
                    file_count = 'multiple',
                    interactive= False
                )
                
            with gr.Row():
                with gr.Accordion(label = 'Instructions'):
                    gr.HTML(html._instruct)

                API_Key         = gr.Textbox(
                    label       = 'API key',
                    type        = 'password',
                    placeholder = 'Insert your API key here.',
                    show_label  = True,
                    show_copy_button = True
                )

            with gr.Row():
                run_button      = gr.Button(value = 'Run',  variant = 'primary')
                stop_button     = gr.Button(value = 'Stop', variant = 'stop'   )

            run_event   = run_button.click(
                fn      = process_speaker_diarization,
                inputs  = [input_audio, API_Key],
                outputs = [output_audio]
            )

            stop_button.click(
                fn      = lambda: der.globals.__setattr__('Stop', True),
                cancels = [run_event],
            )

        return app
#endregion

def run():
    app = GradioInit(args.theme)
    concurrency_count = 511
    max_size = 1022
    share = True if args.iscolab or args.paperspace else False

    app.queue(concurrency_count=concurrency_count, max_size=max_size)
    app.launch(
        server_name="0.0.0.0",
        server_port=None,
        inbrowser=(not args.not_autolaunch),
        quiet=True,
        share=share,
    )

if __name__ == "__main__":
    run()