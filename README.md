[![PyPI version](https://badge.fury.io/py/caplena.svg)](https://badge.fury.io/py/caplena)
[![Downloads](https://static.pepy.tech/personalized-badge/caplena?period=month&units=international_system&left_color=black&right_color=brightgreen&left_text=downloads/month)](https://pepy.tech/project/caplena)

# Caplena Python Library

The Caplena Python library provides convenient access to the Caplena REST API from applications written in the Python programming language.

## Documentation

To learn more about what you can use Caplena for and for how to create your own API key, please see [our main website](https://caplena.com/).

To learn more about the REST API that constitutes the basis for this project, take a look at our [REST API docs](https://caplena.com/docs/developers/).

To view the Python API docs and refernces, head over to our [SDK documentation](https://caplena.com/docs/sdk/python/).

## Installation

### Minimum Version

We recommend using the latest version of Python. Caplena supports Python 3.8 and newer.

### Dependencies

The following distributions will be installed automatically when installing Caplena.

- [Requests](https://docs.python-requests.org/en/latest/) is an elegant and simple HTTP library for Python.
- [Typing Extensions](https://github.com/python/typing/tree/master/typing_extensions) enables use of new type system features on older Python versions.

### Installing Caplena

Within your Python environment of choice, use the following command to install Caplena:

```sh
$ pip install caplena
```

Caplena is now installed.

## Development

To use `caplena-python` in a development environment, we recommend you to set up a development virtualenv. Once done, you
can run the following command to install all required dependencies:

```sh
make install
```

Run all tests:

```sh
make test
```

Run all tests in watch mode:

```sh
make test-watch
```

Run the formatter:

```sh
make fmt
```

Run the linter:

```sh
make lint
```

Build the Sphinx SDK docs:

```sh
make build-docs
```

The Sphinx generated documentation is automatically generated and uploaded to our [developer documentation portal](https://caplena.com/docs/sdk/python/), using Github Actions.

Build the Python package:

```sh
make build-sdk
```

Publish the Python package:

```sh
make publish-sdk
```

Show all supported commands:

```sh
make help
```
