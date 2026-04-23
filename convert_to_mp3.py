import os
import subprocess
import sys
from tqdm import tqdm

# --- Settings ---
SUPPORTED_INPUT_FORMATS = ('.mp3', '.wav', '.aac', '.flac', '.ogg', '.wma', '.m4a', '.opus')
OUTPUT_FORMAT = '.mp3'
AUDIO_BITRATE = '256k' # Output Bitrate MP3 (ex. '192k', '320k')

# --- Helper Functions ---

def get_user_input(prompt, default_value=None):
    """Getting user input with default value."""
    user_input = input(f"{prompt} [{default_value or 'Enter value'}]: ").strip()
    if not user_input and default_value:
        return default_value
    return user_input or None

def check_ffmpeg():
    """Validating FFmpeg accessibility"""
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        print("FFmpeg is installed and accessible.")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("\nERROR: FFmpeg not found or not accessible.")
        print("Please install FFmpeg and make sure it's in your system's PATH.")
        print("You can download FFmpeg from: https://ffmpeg.org/download.html")
        return False

def convert_audio_file(input_file, output_file, progress_bar):
    """
    Convert an audio file using FFmpeg and update progress bar, removing streams and metadata from file.
    With an option to hide anything in log except important errors.
    (You can change -loglevel value to 'warning' or 'info' to see more.)
    """
    command = [
        'ffmpeg',
        '-i', input_file,
        '-codec:a', 'libmp3lame',
        '-b:a', AUDIO_BITRATE,
        '-map_metadata', '-1', # removing metadata
        '-vn', # removing video
        '-loglevel', 'error', # only show errors
        output_file
    ]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate() # Wait for FFmpeg to finish the process

        if process.returncode == 0:
            # File converted successfully
            progress_bar.update(1) # Add one point to progress bar
            return True
        else:
            # FFmpeg error
            print(f"\nError converting {os.path.basename(input_file)}:")
            print(stderr)
            return False
    except Exception as e:
        print(f"\nAn unexpected error occurred while processing {os.path.basename(input_file)}: {e}")
        return False

def main():
    """ Main UI """
    print("=" * 60)
    print("           Advanced Audio Converter with FFmpeg & Python")
    print("=" * 60)

    if not check_ffmpeg():
        sys.exit(1)

    default_input_dir = os.path.join(os.getcwd(), "input_audio")
    default_output_dir = os.path.join(os.getcwd(), "output_audio")

    input_dir = get_user_input("Enter the input directory containing audio files", default_input_dir)
    output_dir = get_user_input("Enter the output directory for converted files", default_output_dir)

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"\nError creating output directory {output_dir}: {e}")
            sys.exit(1)

    audio_files = []
    print(f"\nScanning for audio files in: {input_dir}")
    for filename in os.listdir(input_dir):
        # Checking file format
        if filename.lower().endswith(SUPPORTED_INPUT_FORMATS):
            full_path = os.path.join(input_dir, filename)
            if os.path.isfile(full_path):
                audio_files.append(full_path)

    if not audio_files:
        print("No supported audio files found in the input directory.")
        sys.exit(0)

    print(f"Found {len(audio_files)} audio files to process.")

    success_count = 0
    fail_count = 0
    total_files = len(audio_files)

    # Displaying main progress bar
    with tqdm(total=total_files, unit='file', desc="Converting files", ascii=True) as pbar:
        for input_file in audio_files:
            base_name = os.path.basename(input_file)
            name, _ = os.path.splitext(base_name) # File name only
            output_file = os.path.join(output_dir, f"{name}{OUTPUT_FORMAT}")

            # Skipping existing files (already converted)
            if os.path.exists(output_file):
                print(f"\nSkipping {base_name}: Output file already exists.")
                pbar.update(1) # Include this file in progress bar
                continue

            if convert_audio_file(input_file, output_file, pbar):
                success_count += 1
            else:
                fail_count += 1

    # --- Show result summary ---
    print("\n" + "=" * 60)
    print("Conversion Process Completed")
    print("=" * 60)
    print(f"Total files found: {total_files}")
    print(f"Successfully converted: {success_count}")
    print(f"Failed conversions: {fail_count}")
    print(f"Output files saved to: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
