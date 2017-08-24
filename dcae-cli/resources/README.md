# Resources

## `config.json`

To be used to distribute backend configuration information like the onboarding database connection information to end users of dcae-cli.

```
curl -v --user <user>:<password> https://<your file server host>/dcae-cli/config.json --upload-file config.json
```

### Format

```
{
    "active_profile": <active profile option>,
    "db_url": <onboarding catalog database connection>
}
```

## `profiles.json`

To be used to distribute platform team approved environment profiles to end users of dcae-cli.

```
curl -v --user <user>:<password> https://<your file server host>/dcae-cli/profiles.json --upload-file profiles.json
```

### Format

```
{
    "env-name": {
        "docker_host": <docker hostname:port>,
        "cdap_broker": <cdap broker consul name>,
        "consul_host": <consul hostname>,
        "config_binding_service": <config binding service consul name>
    }
}
```
