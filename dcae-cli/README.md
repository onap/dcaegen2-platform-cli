# dcae-cli

The `dcae-cli` is a Python command-line tool used to manage and to test components and their data formats in onboarding.

## Documentation

Please review the [DCAE platform documentation](ONAP URL TBD) which has a detailed [`dcae-cli` walkthrough](ONAP URL TBD).

## Local use

The dcae-cli requires access to an onboarding catalog which is a postgres database.  If there is no shared instance for your team or organization, then a workaround is to run a local instance of postgres on your machine.  One quick way is to run a postgres Docker container:

```
docker run -e POSTGRES_PASSWORD=<your password> -e PGDATA=/var/lib/postgresql/data/pgdata -v <local directory>:/var/lib/postgresql/data/pgdata -p 5432:5432 -d postgres:9.5.2
```

Use your favorite sql client to log into this local instance and create a database named `dcae_onboarding_db`.

Now that your onboarding catalog is setup, run `dcae_cli --reinit` and walkthrough the prompts to configure your dcae-cli to point to this local instance.
