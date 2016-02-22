# pbauto-generator
This is the python project that allows users to generate a custom Pandoras Box Automation library. We use it internally, but maybe you can make good use of it.

## Requirements
### Python 3.5+
Get python for your operating system from https://www.python.org/downloads/

### Python Packages
Use the package manager **pip** to install requirements ```pip install -r requirements.txt```

## Files & Directories
* **generator.py** - The main file that generates the code using the templates.
* **db.json** - A json file that contains all relevant information about the Pandoras Box Automation functions.
* **config.json** - The configuration file that controls which files are processed.
* **source/** - This directory contains all Jinja2 based templates that are parsed by the generator.

## How it works
Each template file in jobs can use the database data (*you can find a copy of it in db.json*) to generate text files. The *config.json* contains instructions on what to process.

## Contributing
Since all the code files are generated off templates, it is the best to contribute directly to the templates. If you don't know how, just push changes on the generated files and we will make sure that it gets updated in the templates.

## Support
visit http://www.coolux.de/support/customerservice/