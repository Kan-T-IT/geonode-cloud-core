
# ACL Client

Integration of Geonode with the Geoserver ACL client

## Repository

- [Geonode v4.1.3-gscloud](https://git.kan.com.ar/kan/productos/geoportal_express/-/commits/v4.1.3-gscloud)


## Version Information

- Geonode: 4.1.3
- Geoserver: 2.23.0


## Development Description

The GeoServer ACL includes a client auto-generator in multiple selectable languages. In this case, it was executed in Python. The resulting code can be found in the directory **geonode/geoserver/acl/gsauth_client**.


There are three types of APIs generated from it:

- Admin Rules
- Authorization
- Rules

At the moment, development is focused on this last item.

Note: The API provides a Swagger available for documentation and usage of the RESTful service, which can be accessed with a username and password: **{SITE_URL}/acl**


### API Authentication

For authentication with the ACL API, environment variables defined in the Geonode project's .env file are used:

- ACL_HOST=
- ACL_USERNAME=
- ACL_PASSWORD=


### Rule Manager

In the file **geonode/geoserver/acl_client.py**, there's a further abstraction of the auto-generated client API where the most important and commonly used methods are concentrated. This abstraction is utilized in the initial stage to connect with the GeoServer component through this.

```
class RuleManager:
    
    def __init__(self, host=None, username=None, password=None):
        # Configure basic authentication
        self.configuration = gsauth_client.Configuration(
            host=host or os.environ.get("ACL_HOST", None),
            username=username or os.environ.get("ACL_USERNAME", None),
            password=password or os.environ.get("ACL_PASSWORD", None)
        )
        # Create an instance of the API client
        self.api_client = gsauth_client.ApiClient(self.configuration)
        # Create an instance of the API
        self.api_instance = gsauth_client.RulesApi(self.api_client)
```

This class will call its respective methods as required, such as obtaining, editing, deleting, among other operations.


### Reutilization of Geofence structure

To simplify integration in this initial stage, existing logic used by Geofence to define rules is utilized. Since these are similar tools and share common parameters, this approach is adequate.

The function invoked during layer upload and permission setting is **create_geofence_rules**, which is defined in the file **geonode/geoserver/security.py**

The call is made during the iteration of the services that have been created

```
from geonode.geoserver.signals import custom_rule_assign

params = {
    'workspace': workspace_name,
    'layer': layer_name,
    'user': username,
    'group': groupname,
    **rule_fields,
}

custom_rule_assign.send_robust(sender=None, **params)
```

Here, a custom Django signal named **handle_custom_rule_assign**, defined in **geonode/geoserver/signals.py**, is subscribed to. This signal ultimately invokes the methods of the aforementioned **RuleManager** class and, in turn, the methods it provides.

```
from django.dispatch import receiver

from geonode.geoserver.acl_client import rule_manager, gsauth_client

custom_rule_assign = Signal()

@receiver(custom_rule_assign)
def handle_custom_rule_assign(sender, **kwargs):

    message = f"""A geofence rule has been assigned to the object: {kwargs}"""
    logger.debug(message)
    priority = rule_manager.get_first_available_priority()
    new_rule = gsauth_client.Rule(
        priority=priority,
        access = "ALLOW" if kwargs["access"] else "DENY", 
        workspace=kwargs["workspace"], 
        layer=kwargs["layer"], 
        service=kwargs["service"], 
        user=kwargs["user"]
    )
    created_rule = rule_manager.create_rule(new_rule)

```

### Logs
To visualize the Celery logs, it's necessary to set the **DEBUG** environment variable to **True**.

Another important thing to consider is the logging configuration, where we can define which types of logs we want to observe in the settings.py file.

```
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d " "%(thread)d %(message)s"},
        "simple": {
            "format": "%(message)s",
        },
        "br": {"format": "%(levelname)-7s %(asctime)s %(message)s"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "br": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "br"},
    },
    "loggers": {
        "django": {
            "handlers": ["console"], 
            "level": "DEBUG",
            "propagate": False,
        },
        "geonode": {
            "handlers": ["console"], 
            "level": "DEBUG",
            "propagate": False,   
        },
        "geonode.br": {"level": "INFO", "handlers": ["br"], "propagate": False},
        "geoserver-restconfig.catalog": {
            "level": "ERROR",
        },
        "owslib": {
            "level": "ERROR",
        },
        "pycsw": {
            "level": "ERROR",
        },
        "celery": {
            "handlers": ["console"], 
            "level": "DEBUG",
            "propagate": False,  
        },
        "mapstore2_adapter.plugins.serializers": {
            "level": "ERROR",
        },
        "geonode_logstash.logstash": {
            "level": "ERROR",
        },
    },
}
```

Once we have the Geonode containers running, to observe the Celery logs in the console, execute:

```
docker-compose logs -f celery
```
