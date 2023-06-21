# Duplicate File Scanner

Duplicate File Scanner is a Python script that scans specified sources for duplicate files and generates a results page listing the duplicate files found. It provides options to control verbosity, saving results to file, and force overwriting existing results files.

## Usage

```
$ python3 duplicate-file-scanner.py [arguments] <source_paths>...
```

## Arguments

- `-h, --help`: Print the help page.
- `-v, --verbose`: Enable verbose mode. Print detailed information during the scanning process.
- `-s [filename], --save-results=[filename]`: Save the results page to the specified file. If multiple sources are provided, separate files will be generated for each source.
- `-f, --force, --overwrite`: Used in combination with `-s` or `--save-results`. Force overwrite if the results file already exists.

## Examples

```
$ python3 duplicate-file-scanner -v /path/to/source
```

Scan for duplicate files in the `/path/to/source` directory and display verbose output.

```
$ python3 duplicate-file-scanner -s results.txt /path/to/source1 /path/to/source2
```

Scan for duplicate files in multiple sources and save the results to the specified file `results.txt`.

```
$ python3 duplicate-file-scanner -s results.txt -f /path/to/source
```

Scan for duplicate files in the `/path/to/source` directory, force overwrite the results file if it exists.

## Author

Theodoros Nicolaou

## Credits

This script was developed with the assistance of ChatGPT, an AI language model by OpenAI. Visit [https://openai.com/](https://openai.com/) to learn more about ChatGPT.

## License

This code is licensed under the MIT license. Details can be found in the 'LICENSE' file.
