# Contributing

We are open to, and grateful for, any contributions made by the community. By contributing to axios, you agree to abide by the [code of conduct](https://https://github.com/Stimson-Center/stimson-web-curator/blob/master/CODE_OF_CONDUCT.md).

### Code Style

Please follow the [node style guide](https://github.com/felixge/node-style-guide).

### Commit Messages

Commit messages should be verb based, using the following pattern:

- `Fixing ...`
- `Adding ...`
- `Updating ...`
- `Removing ...`

### Testing

Please update the tests to reflect your code changes. Pull requests will not be accepted if they are failing on [Travis CI](https://travis-ci.org/axios/axios).

### Documentation

Please update the [docs](README.md) accordingly so that there are no discrepancies between the API and the documentation.

### Developing

- `npm run test` run the jasmine and mocha tests
- `npm run build` run webpack and bundle the source
- `npm run start` run in production mode
- `npm run local` run in development mode


Please don't include changes to `dist/` in your pull request. This should only be updated when releasing a new version.

### Deploying to Google Cloud Platform

```bash
    ./run_deploy
    open https://stimson-web-curator.uk.r.appspot.com
```

### Running locally

Running production in browser

```bash
    docker --version
    cd ~/stimson-web-scraper
    ./run_docker.sh
```
You will automatically be put into the virtual machine:

(venv) tf-docker /app >


```bash
    ./run_tests.sh
```
