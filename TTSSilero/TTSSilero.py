import contextlib
import os
import io
import wave
import torch.package

from .Speakers import Speakers
from .multi_v2_package import TTSModelMulti_v2


class TTS:
    def __init__(self, threads: int = 12):
        device = torch.device('cpu')
        torch.set_num_threads(threads)
        local_file = 'model_multi.pt'

        if not os.path.isfile(local_file):
            torch.hub.download_url_to_file(
                'https://models.silero.ai/models/tts/multi/v2_multi.pt',
                local_file
            )

        self.model: TTSModelMulti_v2 = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
        self.model.to(device)

        self.sample_rate = 16000

    def synthesize_text(self, text: str, speaker: Speakers = Speakers.kseniya, seek: int = None) -> io.BytesIO:
        return self.to_wav(self._synthesize_text(text, speaker), seek)

    def _synthesize_text(self, text: str, speaker: Speakers) -> list[torch.Tensor]:
        """
        Performs splitting text and synthesizing it

        :param text:
        :return:
        """

        results_list: list[torch.Tensor] = self.model.apply_tts(
            texts=[text],
            speakers=speaker.value,
            sample_rate=self.sample_rate
        )

        return results_list

    def to_wav(self, synthesized_text: list[torch.Tensor], seek: int = None) -> io.BytesIO:
        res_io_stream = io.BytesIO()

        with contextlib.closing(wave.open(res_io_stream, 'wb')) as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            for result in synthesized_text:
                wf.writeframes((result * 32767).numpy().astype('int16'))

        if type(seek) is int:
            res_io_stream.seek(seek)

        return res_io_stream


