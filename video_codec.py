import argparse
import os

from system import call_subprocess

DEFAULT_IMG_FORMAT = 'jpg'
DEFAULT_IMG_PREFIX = 'frame'
DEFAULT_ENCODER = 'libx265'
DEFAULT_CONTAINER = "mkv"
DEFAULT_FRAMERATE = "24000/1001"
DEFAULT_ENCODER_PARAMS = ["-crf", "28", "-preset", "fast", "-x265-params", "profile=main10"]
DEFAULT_PIX_FMT = "yuv420p10le"

FORMAT_CHOICES = [
    'jpg',
    'png',
    'webm'
]

def decode(source: str, destination: str=None, format: str=DEFAULT_IMG_FORMAT, prefix: str=DEFAULT_IMG_PREFIX) -> str:
    workdir = os.path.dirname(source)
    filename = os.path.basename(source)
    video_name = '.'.join(filename.split('.')[:-1])
    dest = os.path.join(workdir, video_name+"-raw")
    if destination:
        dest = destination
    os.makedirs(dest)
    call_subprocess(["ffmpeg", "-i", source, "-qscale:v", "1", "-qmin", "1", "-qmax", "1", "-vsync", "0", f"{dest}/{prefix}%08d.{format}"])
    return dest

def encode(source: str, audio_origin: str, framerate:str = DEFAULT_FRAMERATE, destination: str=None, encoder: str=DEFAULT_ENCODER, encoder_params: list=[], pix_fmt: str=DEFAULT_PIX_FMT, container: str=DEFAULT_CONTAINER, format: str=DEFAULT_IMG_FORMAT, prefix: str=DEFAULT_IMG_PREFIX):
    dest = os.path.dirname(source)
    name = os.path.basename(source)
    if destination:
        dest = destination
        os.makedirs(dest, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-r", framerate,
        "-i", f"{source}/{prefix}%08d.{format}",
        "-i", audio_origin,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:a", "copy",
        "-c:v", encoder
    ]
    if encoder_params:
        cmd += encoder_params
    cmd += [
        "-pix_fmt", pix_fmt,
        f"{dest}/{name}-enhanced.{container}"
    ]
    call_subprocess(cmd, quiet=False)
    return f"{dest}/{name}-enhanced.{container}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help='Video source')
    parser.add_argument('--destination', '-d', type=str, required=False, help='Destination folder path')
    parser.add_argument('--prefix', '-p', type=str, required=False, help='Prefix output names')
    parser.add_argument('--format', '-f', type=str, required=False, choices=FORMAT_CHOICES, help='Image format')
    args = parser.parse_args()

    decode(args.source, args.destination, format=args.format, prefix=args.prefix)