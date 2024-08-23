import os
import itertools
import logging
import traceback

from geonode.geoserver.acl import gsauth_client 
from geonode.geoserver.acl.gsauth_client.models import Rule as ACLRule, RuleFilter
from geonode.geoserver.acl.gsauth_client.rest import ApiException
from geonode.geoserver.acl.gsauth_client.models.geom import Geom


logger = logging.getLogger(__name__)


class ACLException(Exception):
    pass


class Rule(ACLRule):
    """ Rule class inherited from gsauth_client.models.Rule but with some additional methods for Geofence format compatibility"""

    ALLOW = "ALLOW"
    DENY = "DENY"
    LIMIT = "LIMIT"
    CM_MIXED = "MIXED"

    def __init__(self, access: (str, bool), id=None, priority=None, workspace=None, layer=None, user=None, group=None, service=None, request=None, subfield=None, geo_limit=None, catalog_mode=None):
        super().__init__(id=id, access=access, priority=priority, workspace=workspace, layer=layer, user=user, role=group, service=service, limits=geo_limit, request=request, subfield=subfield)
        self.fields = {}

        # access may be either a boolean or ALLOW/DENY/LIMIT
        if access is True:
            access = Rule.ALLOW
        elif access is False:
            access = Rule.DENY

        for field, value in (
            ("id", id),
            ("priority", priority),
            ("user", user),
            ("role", group),
            ("service", service),
            ("request", request),
            ("subfield", subfield),
            ("workspace", workspace),
            ("layer", layer),
            ("access", access),
        ):
            if value is not None and value != "*":
                self.fields[field] = value

        _limits = {}
        for field, value in (
            # ("allowedArea", geo_limit),
            ("allowedArea", Geom(wkt=geo_limit)),
            ("catalogMode", catalog_mode),
        ):
            if value is not None:
                _limits[field] = value

        if _limits:
            self.fields["limits"] = _limits

    def set_priority(self, pri: int):
        self.fields["priority"] = pri

    def get_object(self) -> dict:
        logger.debug(f"Creating Rule object: {self.fields}")
        return {"Rule": self.fields}
    

#     def __str__(self) -> str:
#         return super().__str__()

class Batch:
    """_summary_
    A ACL Batch.
    It's a list of operations that will be executed transactionally inside ACL (?).

    e.g.:
    {
      "Batch": {
         "operations": [
            {
                "@service": "rules",
                "@type": "insert",
                "Rule": {
                    "priority": 0,
                    "user": "admin",
                    "service": "WMS",
                    "workspace": "geonode",
                    "layer": "san_andres_y_providencia_administrative",
                    "access": "ALLOW"
                }
            },
            {
                "@service": "rules",
                "@type": "insert",
                "Rule": {
                    "priority": 1,
                    "user": "admin",
                    "service": "GWC",
                    "workspace": "geonode",
                    "layer": "san_andres_y_providencia_administrative",
                    "access": "ALLOW"
                }
            },
            {
                "@service": "rules",
                "@type": "insert",
                "Rule": {
                    "priority": 2,
                    "user": "admin",
                    "service": "WFS",
                    "workspace": "geonode",
                    "layer": "san_andres_y_providencia_administrative",
                    "access": "ALLOW"
                }
            },
            {
                "@service": "rules",
                "@type": "insert",
                "Rule": {
                    "priority": 3,
                    "user": "admin",
                    "service": "WPS",
                    "workspace": "geonode",
                    "layer": "san_andres_y_providencia_administrative",
                    "access": "ALLOW"
                }
            },
            {
                "@service": "rules",
                "@type": "insert",
                "Rule": {
                    "priority": 4,
                    "user": "admin",
                    "workspace": "geonode",
                    "layer": "san_andres_y_providencia_administrative",
                    "access": "ALLOW"
                }
            }
        ]
      }
    }

    Returns:
        _type_: Batch
    """

    def __init__(self, log_name=None) -> None:
        self.operations = []
        self.log_name = f'"{log_name}"' if log_name else ""

    def __str__(self) -> str:
        return super().__str__()

    def add_delete_rule(self, rule_id: int):
        self.operations.append({"@service": "rules", "@type": "delete", "@id": rule_id})

    def add_insert_rule(self, rule: Rule):
        operation = {
            "@service": "rules",
            "@type": "insert",
        }
        operation.update(rule.get_object())
        self.operations.append(operation)

    def length(self) -> int:
        return len(self.operations)

    def get_object(self) -> dict:
        return {"Batch": {"operations": self.operations}}


class AutoPriorityBatch(Batch):
    """_summary_
    A Batch that handles the priority of the inserted rules.
    The first rule will have the declared `start_rule_pri`, next Rules will have the priority incremented.
    """

    def __init__(self, start_rule_pri: int, log_name=None) -> None:
        super().__init__(log_name)
        self.pri = itertools.count(start_rule_pri)

    def add_insert_rule(self, rule: Rule):
        rule.set_priority(self.pri.__next__())
        super().add_insert_rule(rule)


class AclClient:
    
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
    
    def insert_rule(self, rule):
        try:
            # Call the endpoint to create the rule
            api_response = self.api_instance.create_rule(rule)
            return api_response
        except ApiException as e:
            print("Exception when calling RulesApi->create_rule: %s\n" % e)
            return None

    def delete_rule_by_id(self, rule_id):
        try:
            # Call the endpoint to delete the rule by ID
            self.api_instance.delete_rule_by_id(rule_id)
            print("The rule with ID {} has been deleted successfully.".format(rule_id))
        except ApiException as e:
            print("Exception when calling RulesApi->delete_rule_by_id: %s\n" % e)

    def run_batch(self, batch: Batch, timeout: int = None) -> bool:
        if batch.length() == 0:
            logger.info(f"Skipping batch execution {batch.log_name}")
            return False

        logger.info(f"Running batch {batch.log_name} with {batch.length()} operations")
        try:
            logger.info("***********************")
            # return {"Batch": {"operations": self.operations}}
            # self.operations.append({"@service": "rules", "@type": "delete", "@id": rule_id})

            for op in batch.operations:
                # "Rule": {
                #     "priority": 2,
                #     "user": "admin",
                #     "service": "WFS",
                #     "workspace": "geonode",
                #     "layer": "san_andres_y_providencia_administrative",
                #     "access": "ALLOW"
                # }
                
                _priority = op.get('priority')
                try:
                    _priority = int(_priority)
                except:
                    _priority = None

                if _priority is None:
                    op['priority'] = self.get_first_available_priority()

                if 'Rule' not in op and op['@type'] == 'insert':
                    raise Exception(f"Rule not found in operation {op['@id']}")


                if op['@type'] == 'insert':
                    # Replace keys from geofence format to ACL format
                    if 'limits' in op['Rule']:
                        op['Rule']['geo_limit'] = op['Rule'].pop('limits')
                        
                    if 'role' in op['Rule']:
                        op['Rule']['group'] = op['Rule'].pop('role')

                    rule = Rule(**op['Rule'])
                    self.insert_rule(rule)
                elif op['@type'] == 'delete':
                    self.delete_rule_by_id(op['@id'])
                else:
                    logger.error(f"run_batch -> @type: {op['@type']} not supported for operation {op['@id']}")

                logger.info(op)

            logger.info("***********************")

            # r = requests.post(
            #     f"{self.baseurl}batch/exec",
            #     json=batch.get_object(),
            #     auth=HTTPBasicAuth(self.username, self.pw),
            #     timeout=timeout or self.timeout,
            #     verify=False,
            # )

            # if r.status_code != 200:
            #     logger.debug(
            #         f"Error while running batch {batch.log_name}: [{r.status_code}] - {r.content}"
            #         f"\n {batch.get_object()}"
            #     )
            #     raise ACLException(f"Error while running batch {batch.log_name}: [{r.status_code}]")

            return True

        except Exception as e:
            logger.info(f"Error while requesting batch exec {batch.log_name}")
            logger.debug(f"Error while requesting batch exec {batch.log_name} --> {batch.get_object()}", exc_info=e)
            raise ACLException(f"Error while requesting batch execution {batch.log_name}: {e}")

    def invalidate_cache(self):
        # r = requests.put(f"{self.baseurl}ruleCache/invalidate", auth=HTTPBasicAuth(self.username, self.pw))

        # if r.status_code != 200:
        #     logger.debug("Could not invalidate cache")
        #     raise ACLException("Could not invalidate cache")

        # TODO: Implement cache invalidation
        pass

    def get_first_available_priority(self):
        try:
            last_rule = None

            # Get the count of rules
            rules_count = self.count_all_rules()
            
            # Get the last rule
            if rules_count > 0:
                last_rule = self.get_rules()[rules_count - 1]
            
            if last_rule:
                highest_priority = last_rule.priority
            else:
                highest_priority = 0
            return int(highest_priority) + 1
        except ApiException as e:
            print("Exception when calling RulesApi->get_first_available_priority: %s\n" % e)
            return -1

    def count_all_rules(self):
        try:
            # Get the count of rules
            api_response = self.api_instance.count_all_rules()
            return api_response
        except ApiException as e:
            print("Exception when calling RulesApi->count_all_rules: %s\n" % e)
            raise e

    def get_rules(self, limit=None, next_cursor=None):
        try:
            # Call the endpoint to get the rules
            api_response = self.api_instance.get_rules(limit=limit, next_cursor=next_cursor)
            return api_response
        except ApiException as e:
            print("Exception when calling RulesApi->get_rules: %s\n" % e)
            return None


class AclUtils:
    
    def __init__(self, acl_client):
        # Instance of the API
        self.acl_client = acl_client
        self.api_instance = acl_client.api_instance

    def update_rule_by_id(self, rule_id, rule):
        try:
            # Call the endpoint to update the rule by ID
            api_response = self.api_instance.update_rule_by_id(rule_id, rule)
            return api_response
        except ApiException as e:
            print("Exception when calling RulesApi->update_rule_by_id: %s\n" % e)
            return None

    def get_dataset_rules(
        self,
        # page: int = None,
        # entries: int = None,
        workspace: str = None,
        layer: str = None,
    ):
        
        result_rules = None

        if workspace is None or layer is None:
            print("Exception when calling RulesApi->get_rules: %s\n" % e)
            return []
        
        try:
            # rule_filter = RuleFilter(workspace=workspace, layer=layer)
            # # rule_filter = {}
            # # rule_filter["workspace"] = workspace
            # # rule_filter["layer"] = layer
            # print(rule_filter.to_dict())

            # result_rules = self.api_instance.query_rules(rule_filter=rule_filter)

            rules = self.api_instance.query_rules()
            _rules = []
            for r in rules:
                if r.layer == layer and r.workspace == workspace:
                    dict_rule = {}
                    keys = ["id", "priority", "user", "role", "service", "request", "subfield", "workspace", "layer", "access", "limits"]
                    for key in keys:
                        dict_rule[key] = getattr(r, key)
                    dict_rule["group"] = dict_rule.pop("role")
                    dict_rule["geo_limit"] = dict_rule.pop("limits")
                    _rules.append(Rule(**dict_rule))

            result_rules = {"rules": _rules}
        except ApiException as e:
            print("Exception when calling RulesApi->get_rules: %s\n" % e)
            return []

        return result_rules

    def collect_delete_layer_rules(self, workspace_name: str, layer_name: str, batch: Batch = None) -> Batch:
        """Collect delete operations in a Batch for all rules related to a layer"""

        try:
            # Scan ACL Rules associated to the Dataset
            gs_rules = self.get_dataset_rules(workspace=workspace_name, layer=layer_name)

            if not batch:
                batch = Batch(f"Delete {workspace_name}:{layer_name}")

            cnt = 0
            if gs_rules and gs_rules["rules"]:
                logger.info(
                    f"Going to collect {len(gs_rules['rules'])} rules for layer '{workspace_name}:{layer_name}'"
                )
                for r in gs_rules["rules"]:
                    # if r["layer"] and r["layer"] == layer_name:
                    if r.layer and r.layer == layer_name:
                        batch.add_delete_rule(r.id)
                        cnt += 1
                    else:
                        logger.warning(f"Bad rule retrieved for dataset '{workspace_name or ''}:{layer_name}': {r}")

            logger.info(f"Adding {cnt} rule deletion operations for '{workspace_name or ''}:{layer_name}")
            return batch

        except Exception as e:
            logger.error(f"Error collecting rules for {workspace_name}:{layer_name}", exc_info=e)
            tb = traceback.format_exc()
            logger.debug(tb)

        return None

    def delete_layer_rules(self, workspace_name: str, layer_name: str) -> bool:
        """Delete all Rules related to a specific Layer"""

        try:
            batch = self.collect_delete_layer_rules(workspace_name, layer_name)
            logger.info(f"Going to remove {batch.length()} rules for layer {workspace_name}:{layer_name}")
            return self.acl_client.run_batch(batch)

        except Exception as e:
            logger.error(f"Error removing rules for {workspace_name}:{layer_name}", exc_info=e)
            tb = traceback.format_exc()
            logger.info(tb)
            return False

    def get_first_available_priority(self):
        return self.acl_client.get_first_available_priority()