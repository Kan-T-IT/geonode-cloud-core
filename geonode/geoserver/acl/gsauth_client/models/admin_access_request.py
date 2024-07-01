# coding: utf-8

"""
    GeoServer ACL

    GeoServer Access Control List API  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from geonode.geoserver.acl.gsauth_client.configuration import Configuration


class AdminAccessRequest(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'user': 'str',
        'roles': 'list[str]',
        'instance': 'str',
        'source_address': 'str',
        'workspace': 'str'
    }

    attribute_map = {
        'user': 'user',
        'roles': 'roles',
        'instance': 'instance',
        'source_address': 'sourceAddress',
        'workspace': 'workspace'
    }

    def __init__(self, user=None, roles=None, instance='*', source_address='*', workspace='*', local_vars_configuration=None):  # noqa: E501
        """AdminAccessRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._user = None
        self._roles = None
        self._instance = None
        self._source_address = None
        self._workspace = None
        self.discriminator = None

        if user is not None:
            self.user = user
        self.roles = roles
        if instance is not None:
            self.instance = instance
        if source_address is not None:
            self.source_address = source_address
        if workspace is not None:
            self.workspace = workspace

    @property
    def user(self):
        """Gets the user of this AdminAccessRequest.  # noqa: E501

        the authentication user name performing the request for which the authorization is being requested  # noqa: E501

        :return: The user of this AdminAccessRequest.  # noqa: E501
        :rtype: str
        """
        return self._user

    @user.setter
    def user(self, user):
        """Sets the user of this AdminAccessRequest.

        the authentication user name performing the request for which the authorization is being requested  # noqa: E501

        :param user: The user of this AdminAccessRequest.  # noqa: E501
        :type user: str
        """

        self._user = user

    @property
    def roles(self):
        """Gets the roles of this AdminAccessRequest.  # noqa: E501

        The roles the requesting user belongs to  # noqa: E501

        :return: The roles of this AdminAccessRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._roles

    @roles.setter
    def roles(self, roles):
        """Sets the roles of this AdminAccessRequest.

        The roles the requesting user belongs to  # noqa: E501

        :param roles: The roles of this AdminAccessRequest.  # noqa: E501
        :type roles: list[str]
        """

        self._roles = roles

    @property
    def instance(self):
        """Gets the instance of this AdminAccessRequest.  # noqa: E501


        :return: The instance of this AdminAccessRequest.  # noqa: E501
        :rtype: str
        """
        return self._instance

    @instance.setter
    def instance(self, instance):
        """Sets the instance of this AdminAccessRequest.


        :param instance: The instance of this AdminAccessRequest.  # noqa: E501
        :type instance: str
        """

        self._instance = instance

    @property
    def source_address(self):
        """Gets the source_address of this AdminAccessRequest.  # noqa: E501


        :return: The source_address of this AdminAccessRequest.  # noqa: E501
        :rtype: str
        """
        return self._source_address

    @source_address.setter
    def source_address(self, source_address):
        """Sets the source_address of this AdminAccessRequest.


        :param source_address: The source_address of this AdminAccessRequest.  # noqa: E501
        :type source_address: str
        """

        self._source_address = source_address

    @property
    def workspace(self):
        """Gets the workspace of this AdminAccessRequest.  # noqa: E501


        :return: The workspace of this AdminAccessRequest.  # noqa: E501
        :rtype: str
        """
        return self._workspace

    @workspace.setter
    def workspace(self, workspace):
        """Sets the workspace of this AdminAccessRequest.


        :param workspace: The workspace of this AdminAccessRequest.  # noqa: E501
        :type workspace: str
        """

        self._workspace = workspace

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AdminAccessRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AdminAccessRequest):
            return True

        return self.to_dict() != other.to_dict()