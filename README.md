# cover-letter-cli
Simple templating tool to speed up generating personalized cover letters and reduce the chance of errors when editing by hand in a word processor.

Provided a correctly formated template, the tool will prompt the user in the command line to enter the text they would like for each template variable. It will then save the resulting cover letter to your clipboard, and export a pdf to the current directory if that option is specified.

A template can be provided as a path to a .txt file, or they can be stored in a local mongoDB instance and retrieved by name. Functionality is provided to add and delete template from the database.

### Template Format
The templating functionality is very simple. Variables must be placed in the template as follows: `${fooBar}`. The tool will replace all instances of a variable with whatever the user enters in the CLI when prompted. 

#### Example
`Hi! My name is ${firstName} ${lastName}, please hire me! I really need a ${jobType}.`

### Installation & Usage
main.py can just be run directly if you don't feel like fully installing the tool. Otherwise, it can be built and installed with `pip` and `setuptools`.

1. Clone the repo. 
2. In the repo root directory, run `python3 setup.py bdist_wheel`
3. Navigate to `dist/` and run `pip install coverletter-0.0.1-py3-none-any.whl`

#### Usage
If you install the package as above, the tool will be usable from the terminal with the `coverletter` command.

`-a [Path]` or `--add [Path]` Path to the .txt file of the template you would like to add to the database.

`-n [Name]` or `--name [Name]` Generate a cover letter from the template with the specified name.

`-d [Name]` or `--delete [Name]` Delete template with specified name from database.

`--path [Path]` Generate a cover letter from the template at the specified path.

`-p` or `--pdf` Flag indicating whether a pdf output should be saved to the current directory.


### Limitations
- On Linux, `xcel` or `xclip` must be install for the clipboard copying to work properly.
- The pdf library used by this tool only allows latin-1 characters to be add to the PDF. If you see `?` characters in your output, it's because whatever was there before was not a valid latin-1 character.


