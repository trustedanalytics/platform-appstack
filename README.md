platform-appstack
=================

Cloud Foundry platform definition files to be used with https://github.com/trustedanalytics/cloudfoundry-mkappstack.

## Preparation
If you're behing a proxy you need to configure proxy settings: `https_proxy` environment variable.

Prepare your Python installation:
```
sudo apt-get install python-dev python-pip
```

Install necessary Python libraries:
```
sudo -E pip install -r requirements.txt
```

Be sure that you have added ```127.0.1.1``` address in ```/etc/hosts``` file with specified name, for example:
```127.0.1.1 bastion```

## Usage
### Env vars fetcher script configuration
1. Fill the fetcher_config.yml file before running script.
1. Change values in ```templates/template_variables.yml``` for fields which are not filled automatically by ```env_vars_fetcher/app.py``` script.

### Running the script - first way
1. Run ```python env_vars_fetcher/app.py``` in order to generate settings.yml file.

### Running the script - alternative
For running the Env vars fetcher script you can install project requirements with tox and run the script from tox's environment:
1. Installation of the project dependencies (only before first time running the script):
```
sudo -E pip install tox
tox -r
```
1. After installation dependencies run script using:
```
.tox/py27/bin/python env_vars_fetcher/app.py
```

### After running the Env vars fetcher script
1. Copy settings.yml and appstack.yml to cloudfoundry-mkappstack folder.
1. Please, check the names format of zipped artifacts in artifacts directory.

If they contain versions and are in the following format:
`<appname>-<version>.zip`
(for example: app-launcher-helper-0.4.5.zip) 
* Copy versions.yml file to cloudfoundry-mkappstack folder.
* Verify if versions in versions.yml are the same as versions in zipped artifacts file names. 
* If you encounter differences, update versions in versions.yml file so they are the same as in the zipped artifact file names.

If they do not contain version and are in the following format:
`<appname>.zip` 
(for example: app-launcher-helper.zip) 
* No additional actions are required. Please proceed with further instructions.

Follow further instructions from [Platform Application Layer Deployment](https://github.com/trustedanalytics/platform-wiki/wiki/Platform-application-layer-deployment) to deploy the platform applications and brokers

## Tests

For the first time running run command:
```
sudo -E pip install tox
tox -r
```
Else you can run your tests using:
```
tox
```

