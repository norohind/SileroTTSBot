import re
import wave
import torch
import warnings
import contextlib

# for type hints only


class TTSModelMulti_v2():
    def __init__(self, model_path, symbols):
        self.model = self.init_jit_model(model_path)
        self.symbols = symbols
        self.device = torch.device('cpu')
        speakers = ['aidar', 'baya', 'kseniya', 'irina', 'ruslan', 'natasha',
                    'thorsten', 'tux', 'gilles', 'lj', 'dilyara']
        self.speaker_to_id = {sp: i for i, sp in enumerate(speakers)}

    def init_jit_model(self, model_path: str):
        torch.set_grad_enabled(False)
        model = torch.jit.load(model_path, map_location='cpu')
        model.eval()
        return model

    def prepare_text_input(self, text, symbols, symbol_to_id=None):
        if len(text) > 140:
            warnings.warn('Text string is longer than 140 symbols.')

        if symbol_to_id is None:
            symbol_to_id = {s: i for i, s in enumerate(symbols)}

        text = text.lower()
        text = re.sub(r'[^{}]'.format(symbols[2:]), '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if text[-1] not in ['.', '!', '?']:
            text = text + '.'
        text = text + symbols[1]

        text_ohe = [symbol_to_id[s] for s in text if s in symbols]
        text_tensor = torch.LongTensor(text_ohe)
        return text_tensor

    def prepare_tts_model_input(self, text: str or list, symbols: str, speakers: list):
        assert len(speakers) == len(text) or len(speakers) == 1
        if type(text) == str:
            text = [text]
        symbol_to_id = {s: i for i, s in enumerate(symbols)}
        if len(text) == 1:
            return self.prepare_text_input(text[0], symbols, symbol_to_id).unsqueeze(0), torch.LongTensor(speakers), torch.LongTensor([0])

        text_tensors = []
        for string in text:
            string_tensor = self.prepare_text_input(string, symbols, symbol_to_id)
            text_tensors.append(string_tensor)
        input_lengths, ids_sorted_decreasing = torch.sort(
                torch.LongTensor([len(t) for t in text_tensors]),
                dim=0, descending=True)
        max_input_len = input_lengths[0]
        batch_size = len(text_tensors)

        text_padded = torch.ones(batch_size, max_input_len, dtype=torch.int32)
        if len(speakers) == 1:
            speakers = speakers*batch_size
        speaker_ids = torch.LongTensor(batch_size).zero_()

        for i, idx in enumerate(ids_sorted_decreasing):
            text_tensor = text_tensors[idx]
            in_len = text_tensor.size(0)
            text_padded[i, :in_len] = text_tensor
            speaker_ids[i] = speakers[idx]

        return text_padded, speaker_ids, ids_sorted_decreasing

    def process_tts_model_output(self, out, out_lens, ids):
        out = out.to('cpu')
        out_lens = out_lens.to('cpu')
        _, orig_ids = ids.sort()

        proc_outs = []
        orig_out = out.index_select(0, orig_ids)
        orig_out_lens = out_lens.index_select(0, orig_ids)

        for i, out_len in enumerate(orig_out_lens):
            proc_outs.append(orig_out[i][:out_len])
        return proc_outs

    def to(self, device):
        self.model = self.model.to(device)
        self.device = device

    def get_speakers(self, speakers: str or list):
        if type(speakers) == str:
            speakers = [speakers]
        speaker_ids = []
        for speaker in speakers:
            try:
                speaker_id = self.speaker_to_id[speaker]
                speaker_ids.append(speaker_id)
            except Exception:
                raise ValueError(f'No such speaker: {speaker}')
        return speaker_ids

    def apply_tts(self, texts: str or list,
                  speakers: str or list,
                  sample_rate: int = 16000):
        speaker_ids = self.get_speakers(speakers)
        text_padded, speaker_ids, orig_ids = self.prepare_tts_model_input(texts,
                                                                          symbols=self.symbols,
                                                                          speakers=speaker_ids)
        with torch.inference_mode():
            out, out_lens = self.model(text_padded.to(self.device),
                                       speaker_ids.to(self.device),
                                       sr=sample_rate)
        audios = self.process_tts_model_output(out, out_lens, orig_ids)
        return audios

    @staticmethod
    def write_wave(path, audio, sample_rate):
        """Writes a .wav file.
        Takes path, PCM audio data, and sample rate.
        """
        with contextlib.closing(wave.open(path, 'wb')) as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio)

    def save_wav(self, texts: str or list,
                 speakers: str or list,
                 audio_pathes: str or list = '',
                 sample_rate: int = 16000):
        if type(texts) == str:
            texts = [texts]

        if not audio_pathes:
            audio_pathes = [f'test_{str(i).zfill(3)}.wav' for i in range(len(texts))]
        if type(audio_pathes) == str:
            audio_pathes = [audio_pathes]
        assert len(audio_pathes) == len(texts)

        audio = self.apply_tts(texts=texts,
                               speakers=speakers,
                               sample_rate=sample_rate)
        for i, _audio in enumerate(audio):
            self.write_wave(path=audio_pathes[i],
                            audio=(_audio * 32767).numpy().astype('int16'),
                            sample_rate=sample_rate)
        return audio_pathes
