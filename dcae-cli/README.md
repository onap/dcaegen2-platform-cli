# dcae-cli

The `dcae-cli` is a Python command-line tool used to manage and to test components and their data formats in onboarding.

## Documentation

Please review the [DCAE platform documentation](http://onap.readthedocs.io/en/latest/submodules/dcaegen2.git/docs/index.html) which has a detailed [`dcae-cli` walkthrough](http://onap.readthedocs.io/en/latest/submodules/dcaegen2.git/docs/sections/components/dcae-cli/walkthrough.html).

## Usage

You will be prompted to initialize the `dcae-cli` the first time you run the tool.  You also have the option to [re-initializing using the `--reinit` flag](http://onap.readthedocs.io/en/latest/submodules/dcaegen2.git/docs/sections/components/dcae-cli/quickstart.html#reinit).

You will be prompted to provide a remote server url.  The remote server is expected to host several required artifacts that the `dcae-cli` requires like the json schemas to do validation.  Use the following to use the bleeding edge:

```
Please enter the remote server url: https://git.onap.org/dcaegen2/platform/cli/plain
```

You will also be prompted for details on the postgres database to connect with.  Follow the instructions below to run a local instance and provide the connection details in the initialization.

### Local use

The dcae-cli requires access to an onboarding catalog which is a postgres database.  If there is no shared instance for your team or organization, then a workaround is to run a local instance of postgres on your machine.  One quick way is to run a postgres Docker container:

```
docker run -e POSTGRES_PASSWORD=<your password> -e PGDATA=/var/lib/postgresql/data/pgdata -v <local directory>:/var/lib/postgresql/data/pgdata -p 5432:5432 -d postgres:9.5.2
```

Use your favorite sql client to log into this local instance and create a database named `dcae_onboarding_db`.
