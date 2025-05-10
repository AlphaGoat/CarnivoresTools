import os
import numpy as np
from scipy.io.wavfile import write

from utils.read_map import RSCReader

RATE = 22050


def parse_sounds(rsc_file_path,
                 output_dir):

    with RSCReader(rsc_file_path) as rsc_reader:
        header = rsc_reader.get_header()
        sounds = rsc_reader.get_soundsblock()

    # Plot random sounds
    random_sounds = sounds.random_sound_sections

    for i, sound_section in enumerate(random_sounds):
        data = sound_section.random_data

        scaled = np.int16(data / np.max(np.abs(data)) * 32767)

        write(os.path.join(output_dir, f"random_sound_{i:02d}.wav"), RATE, scaled)


if __name__ == "__main__":
    rsc_file_path = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/AREAS/AREA3.RSC"
    output_path = "resources/sound_plots"
    os.makedirs(output_path, exist_ok=True)
#    render_flat_map(map_file_path, rsc_file_path)
    parse_sounds(rsc_file_path, output_path)
