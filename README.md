platform-appstack
=================

Cloud Foundry platform definition files to be used with https://github.com/trustedanalytics/cloudfoundry-mkappstack.

## Preparation
Prepare your Python installation:
```
sudo apt-get install python-dev python-pip
```

Install necessary Python libraries:
```
sudo pip install -r requirements.txt
```

## Usage
1. Fill the fetcher_config.yml file before running script.
1. Change values in templates/template_variables.yml for fields which are not filled automatically by script.
1. Run ```python env_vars_fetcher/app.py``` in order to generate settings.yml file.
1. Copy settings.yml and appstack.yml (also versions.yml file if you want) to cloudfoundry-mkappstack folder.
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

Follow further instructions from [Platform Deployment Procedure](https://github.com/trustedanalytics/platform-wiki/wiki/Platform-Deployment-Procedure%3A-bosh-deployment) to deploy the platform applications and brokers

## Tests

Install necessary Python library:
```
sudo pip install tox
```

For the first time running run command:
```
tox -r
```
Else you can run your tests using:
```
tox
```

