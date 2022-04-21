import winsound
import io


def save_bytes(filename: str, bytes_audio: bytes) -> None:
    with open(file=filename, mode='wb') as res_file:
        res_file.write(bytes_audio)


def play_bytes(bytes_sound: bytes) -> None:
    winsound.PlaySound(bytes_sound, winsound.SND_MEMORY)
