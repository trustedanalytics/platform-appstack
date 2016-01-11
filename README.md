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
Be sure that you have configured ```/etc/hosts``` properly. For this purpose run command ```hostname```.
As a result of this operation you will see hostname of your machine. Now open ```/etc/hosts``` file and find there one line:
```127.0.0.1 <your_hostname>```. If you cannot find it, you should add it there.

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
Copy settings.yml and appstack.yml to cloudfoundry-mkappstack folder.

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

