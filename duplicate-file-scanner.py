#!/bin/python3
import os, sys
from hashlib import sha512


def get_formatted_file_size(file_size):
    suffixes = ['bytes', 'KiB', 'MiB', 'GiB', 'TiB']

    for suffix in suffixes:
        if file_size < 1024:
            return f"{file_size:.2f} {suffix}"
        file_size /= 1024

    return f"{file_size:.2f} {suffixes[-1]}"


def calculate_sha512(file_path):
    # Create a SHA512 hash object
    sha512_hash = sha512()

    # Open the file in binary mode and read it in chunks
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            # Update the hash object with the chunk
            sha512_hash.update(chunk)

    # Get the hexadecimal representation of the hash
    sha512_hex = sha512_hash.hexdigest()

    return sha512_hex


def explore(path, all_files, skipped, stats, verbose=False):
    try:
        # Path leads to file
        if os.path.isfile(path):
            sha512_digest = calculate_sha512(path)
            size = os.path.getsize(path)
            stats['total-files'] += 1
            stats['total-size'] += size

            # Duplicate file
            if sha512_digest in all_files:
                if verbose:
                    print(f"Duplicate of '{all_files[sha512_digest][0]}' found: {path}")
                all_files[sha512_digest][2].append(path)
                stats['duplicates'] += 1
                stats['duplicate-size'] += size

            # First occurence of file
            else:
                if verbose:
                    print(f"New file found: {path}")
                all_files[sha512_digest] = (os.path.basename(path), size, [path])
                stats['unique-files'] += 1

        # Path leads to directory
        elif os.path.isdir(path):
            if verbose:
                print(f'Entering directory: {path}')
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                explore(entry_path, all_files, skipped, stats, verbose)
            stats['total-dirs'] += 1

        # Path is invalid
        elif verbose:
            print(f'Invalid path: {path}')

    # If file or directory is inaccessible for any reason, skip it and keep track of everything that was skipped.
    except:
        if verbose:
            print(f"Couldn't access '{path}', skipping.")
        skipped.append(path)


def create_results_summary(all_files, skipped, stats):
    # Summary
    answer = f"""============ Summary ============
Files scanned            : {stats['total-files']:,}
Directories scanned      : {stats['total-dirs']:,}
Total file size          : {get_formatted_file_size(stats['total-size'])}
Unique files             : {stats['unique-files']:,}
Duplicates               : {stats['duplicates']:,}
Potential storage savings: {get_formatted_file_size(stats['duplicate-size'])}

"""

    # List skipped paths, if there are any
    if len(skipped) != 0:
        answer += f"A total of {str(len(skipped))} paths were inaccessible, and thus were skipped:\n"
        for path in skipped[:-1]:
            answer += f"├ '{path}'\n"
        answer += f"└ '{skipped[-1]}'\n\n"

    if stats['duplicates'] == 0:
        answer += "Good news, no duplicates were found!\n"
    else:
        answer += "\n====== Files that have duplicates ======\n\n"
        # List information for files that have duplicates
        for unique_file in all_files:
            # Skip files that don't have duplicates
            if len(unique_file[1][2])>1:
                # Show general information about the file
                name = unique_file[1][0]
                size = unique_file[1][1]
                duplicate_count = len(unique_file[1][2])
                answer += f"'{name}' ({get_formatted_file_size(size)} per file, {get_formatted_file_size(size * duplicate_count)} total):\n"
                answer += f"SHA512 digest: {unique_file[0]}\n"

                # Show locations where this file was found
                answer += f"Found in locations:\n"
                for path in unique_file[1][2][:-1]:
                    answer += f"├ '{path}'\n"
                answer += f"└ '{unique_file[1][2][-1]}'\n\n"

    return answer


def print_help_page():
    script_name = os.path.basename(sys.argv[0])
    page = f"""
NAME
    {script_name} - Scan for duplicate files and generate a results page

SYNOPSIS
    python3 {script_name} [arguments] <source_paths>...

DESCRIPTION
    This script scans specified sources for duplicate files and generates a
    results page listing the duplicate files found. It provides options to
    control verbosity, saving results to file, and force overwriting existing
    results files.

OPTIONS
    -h, --help
        Print this help page.

    -v, --verbose
        Enable verbose mode. Print detailed information during the scanning
        process.

    -s [filename], --save-results=[filename]
        Save the results page to the specified file. If multiple sources are
        provided, separate files will be generated for each source.

    -f, --force, --overwrite
        Used in combination with -s or --save-results. Force overwrite if the
        results file already exists.

AUTHOR
    Theodoros Nicolaou

CREDITS
    This script was developed with the assistance of ChatGPT, an AI language
    model by OpenAI. Visit https://openai.com/ to learn more about ChatGPT.

EXAMPLES
    $ python3 {script_name} -v /path/to/source
        Scan for duplicate files in the /path/to/source directory and display
        verbose output.

    $ python3 {script_name} -s results.txt /path/to/source1 /path/to/source2
        Scan for duplicate files in multiple sources and save the results to the
        specified file results.txt.

    $ python3 {script_name} -s results.txt -f /path/to/source
        Scan for duplicate files in the /path/to/source directory, force
        overwrite the results file if it exists.

REPORTING BUGS
    Report bugs or issues at: https://github.com/theodoros1234/duplicate-file-scanner/issues

COPYRIGHT
    This is free software; see the source code for copying conditions. There is
    NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""
    print(page)


if __name__=='__main__':
    # Parse information from command line arguments
    sources = []
    show_help = False
    verbose = False
    results_dest = []
    get_results_dest = False
    overwrite_results_dest = False
    error = False

    for arg in sys.argv[1:]:
        if get_results_dest:
            get_results_dest = False
            if arg == '':
                print("ERROR: Asked to save results, but no destination was given.")
                error = True
                break
            else:
                results_dest.append(arg)
        elif arg == '-h' or arg == '--help':
            show_help = True
        elif arg == '-v' or arg == '--verbose':
            verbose = True
        elif arg == '-f' or arg == '--force' or arg == '--overwrite':
            overwrite_results_dest = True
        elif arg == '-s':
            get_results_dest = True
        elif arg.startswith('--save-results='):
            results_dest.append(arg[15:])
            if results_dest[-1] == '':
                print("ERROR: Asked to save results, but no destination was given.")
                error = True
                break
        else:
            sources.append(arg)

    if len(sys.argv) == 1:
        show_help = True
    elif len(sources) == 0 and not show_help:
        print("ERROR: No sources given.")
        error = True
    elif get_results_dest == True:
        print("ERROR: Asked to save results, but no destination was given.")
        error = True

    # Check help page if asked for or if invalid a
    if show_help or error:
        print_help_page()
        # Exit with error code if there was an error
        if error:
            exit(1)
    else:
        # Check if all sources exist and are accessible
        for source in sources:
            if not os.path.exists(source):
                print(f"ERROR: Source '{source}' doesn't exist or can't be accessed.")
                exit(1)

        # Check if any of the paths to save results already exist
        if not overwrite_results_dest:
            problem = False
            for dest in results_dest:
                if os.path.exists(dest):
                    problem = True
                    print(f"ERROR: Results destination file '{dest}' already exists.")
            if problem:
                print("Use '-f', '--force' or '--overwrite' to overwrite any existing files.")
                exit(1)

        # Start scanning through given sources
        all_files = {}
        skipped = []
        stats = {
            'total-files': 0,
            'total-dirs': 0,
            'total-size': 0,
            'unique-files': 0,
            'duplicates': 0,
            'duplicate-size': 0
        }
        for source in sources:
            explore(source, all_files, skipped, stats, verbose)

        # Sort results by file size
        all_files = sorted(all_files.items(), key=lambda x: x[1][1] * len(x[1][2]), reverse=True)
        print(all_files)

        # Create and print results page
        results = create_results_summary(all_files, skipped, stats)
        print(results)

        # Save results to user specified destinations (if there are any)
        for dest in results_dest:
            try:
                with open(dest, 'w') as f:
                    f.write(results)
            except Exception as e:
                print(f"WARNING: Could not save to 'dest'. The following exception was raised: {repr(e)}")

