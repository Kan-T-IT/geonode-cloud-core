
# ACL Client

Integration of Geonode with the Geoserver ACL client


## Version Information

- Geonode: 4.2.4
- Geoserver: 2.25.3.0-CLOUD


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

In the file **geonode/geoserver/acl/acl_client.py**, there's a further abstraction of the auto-generated client API where the most important and commonly used methods are concentrated. This abstraction is utilized in the initial stage to connect with the GeoServer component through this.

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

