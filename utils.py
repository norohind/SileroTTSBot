import winsound
import io


def save_bytes_io(filename: str, bytes_stream: io.BytesIO) -> None:
    with open(file=filename, mode='wb') as res_file:
        bytes_stream.seek(0)
        res_file.write(bytes_stream.read())


def play_bytes_io(bytes_stream: io.BytesIO) -> None:
    bytes_stream.seek(0)
    winsound.PlaySound(bytes_stream.read(), winsound.SND_MEMORY)
