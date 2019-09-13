# App to quickly upload timesheet to Redmine

## Installation

```
$ pip install -r requirements.txt

$ pip install setup.py
```

## Usage

This tool includes several commands to help with time entries visualization. Currently, it is mostly read-only functions. Time entry creation will be included in next versions.

Before using the tool, basic configuration options need to be set. In the config folder there is a sample configuration file:

```
myredpy.yml.example
```

The Redmine URL and Redmine Key must be set here as a minimum for the app to function correctly.

For Linux users, this file can be in any of the next directories:

```
/etc/myredpy/myredpy.yml
~/.config/myredpy/myredpy.yml
~/.myredpy/config/myredpy.yml
~/.myredpy.yml
```

For windows users, you can have it in:

```
C:\Users\user\.myredpy\.myredpy.yml
```

Once both Redmine properties are set, you can execute a command to test it.

```
$ myredpy projects
```

This should list all your current active projects. 

For additional commands, you can type have -h or --help for a description of the function, usage, and parameters if any.

Time entry command example:

```
$ myredpy time-entry today
```
Returns the time entries for the current day grouped by project and day

```
$ myredpy time-entry week
```
Returns the time entries for the current week grouped by project and day


```
$ myredpy time-entry week -l
```
Returns the time entries for the previous week grouped by project and day

```
$ myredpy time-entry fortnight
```
Returns the time entries for the current bi-week period grouped by project and day

## Settings

Aditionally this tool uses TinyDb to store some defaults and configurations. This can be edited directly in the db.json which is at the configuration folder or with some commands included. For the available commands check 

```
$ myredpy settings --help
```

This is a list of some of the configurable settings:

- ignored_projects: A comma-separated list with project_ids to ignore. They are ignored when presenting the time entries views thus not including them in the calculations. Sample value: "1, 50, 18"
- ommit_prefix: If some projects start with the same prefix name (i.e. 'Product Support - 150 Project A'), this setting can be used to omit the prefix. Useful due to the limited space of display for the console application. Sample value: 'Product Support - '.
- project_alias: If more customization is required, this setting allows to set an entire custom project alias. Just set project id and the project alias to use.


## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate


### run myredpy cli application

$ myredpy --help


### run pytest / coverage

$ make test
```

## Deployments

### Docker

Included is a basic `Dockerfile` for building and distributing `MyRedPy`,
and can be built with the included `make` helper:

```
$ make docker

$ docker run -it myredpy --help
```