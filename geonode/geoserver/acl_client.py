import os

from geonode.geoserver.acl import gsauth_client 
from geonode.geoserver.acl.gsauth_client.rest import ApiException


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

    def get_first_available_priority(self):
        try:
            # Get the count of rules
            rules_count = self.count_all_rules()
            # Get the last rule
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

    def get_rule_by_id(self, rule_id):
        try:
            # Call the endpoint to get the rule by ID
            api_response = self.api_instance.get_rule_by_id(rule_id)
            return api_response
        except ApiException as e:
            print("Exception when calling RulesApi->get_rule_by_id: %s\n" % e)
            return None

    def create_rule(self, rule):
        try:
            # Call the endpoint to create the rule
            api_response = self.api_instance.create_rule(rule)
            return api_response
        except ApiException as e:
            print("Exception when calling RulesApi->create_rule: %s\n" % e)
            return None

    def update_rule_by_id(self, rule_id, rule):
        try:
            # Call the endpoint to update the rule by ID
            api_response = self.api_instance.update_rule_by_id(rule_id, rule)
            return api_response
        except ApiException as e:
            print("Exception when calling RulesApi->update_rule_by_id: %s\n" % e)
            return None

    def delete_rule_by_id(self, rule_id):
        try:
            # Call the endpoint to delete the rule by ID
            self.api_instance.delete_rule_by_id(rule_id)
            print("The rule with ID {} has been deleted successfully.".format(rule_id))
        except ApiException as e:
            print("Exception when calling RulesApi->delete_rule_by_id: %s\n" % e)


rule_manager = RuleManager()
