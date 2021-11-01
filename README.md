# Atılım Research Assistant Lab Assignment Program (ARALAP)

ARALAP is a Python program for dealing with assistant lab assignment problem.

## Installation

After cloning the project create a courses json file along with multiple assistant program json files. The examples will be provided in a future commit.

## Usage

There are two CLIs for different purposes. The `interop` interface is for other 
programs and the `schedule` interface is for humans. Some required options are 
shared between two interfaces.

```bash
python main.py
```

or if you want to use a previously generated program and only redistribute the courses that are not present in the file, you can use:

```bash
python main.py -e old-program.json
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPL v3.0](https://choosealicense.com/licenses/gpl-3.0/)