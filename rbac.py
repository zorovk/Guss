# Copyright 2012 Hai Thanh Nguyen
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Role-Based Access Control system

    Implements the hierarchical model of role-based access control.
"""

from google.appengine.ext import ndb

class RoleModel(ndb.Model):
    parents = ndb.KeyProperty(repeated=True)
    name = ndb.StringProperty()

class PermissionModel(ndb.Model):
    desc = ndb.StringProperty()

class RoleAssignmentModel(ndb.Model):
    user_key = ndb.KeyProperty()
    role_key = ndb.KeyProperty()

class PermissionAssignmentModel(ndb.Model):
    role_key = ndb.KeyProperty()
    perm_id = ndb.StringProperty()

def default_role(string_id, name=None, parents=[]):
    """Helper for creating a new and/or getting an existing role that has a string id"""
    _roles_valid(parents)
    q = RoleModel.get_by_id(string_id)
    if q == None:
        if name==None: raise Exception(u"""The role does not exist. You must provide a "name" argument if you wanna create the role."""
                """\nHave you installed the RBAC system?""")
        return RoleModel(id=string_id, name=name, parents=parents).put()
    return q.key

def register_permission(perm_id, desc):
    """Create a new permission
    NOTICE: Permission registrations (using this function) MUST be put in the register_permissions function of rbac_setup.py
        You must go to /upgrade for this function to take effect
    """
    q = PermissionModel.get_by_id(perm_id)
    if not q:
        model = PermissionModel(id=perm_id, desc=desc)
        model.put()

def _roles_valid(roles):
    """Internal helper."""
    for role_key in roles:
        if role_key.get() == None:
            raise Exception(u'The role with id "%s" does not exist.' % role_key.id())
            return False
    return True

def register_role(name, parents=[]):
    """Create a new role
    Args:
      name: A human-readable name for the role
      parents: A list of keys of the roles to be used as this role's parent
    """
    #Make sure that the parents are all valid
    _roles_valid(parents)
    return RoleModel(name=name, parents=parents).put()

def add_role(user_key, role_key):
    """Assign a new role to a user"""
    q = RoleAssignmentModel.gql("WHERE user_key = :1 AND role_key = :2", user_key, role_key)
    if q.count(1) == 0:
        model = RoleAssignmentModel(user_key=user_key, role_key=role_key)
        model.put()

def has_permission(role_key, perm_id):
    q = PermissionAssignmentModel.gql("WHERE role_key = :1 AND perm_id = :2", role_key, perm_id)
    return q.count(1) > 0

def has_permissions(role_key, perms):
    for perm in perms:
        if not has_permission(role_key, perm):
            return False
    return True

def check_permission_role(role_key, perms):
    """Similar to check_permission, but only applies to a specific role"""
    if not isinstance(perms, list):
        perms = [perms]
    if has_permissions(role_key, perms):
        return True
    else:
        parents = role_key.get().parents
        for parent in parents:
            if check_permission_role(parent, perms):
                return True
        return False

def allow(role_key, perms):
    """Assign a permission to a role
    Args:
        role_key: the key of the role
        perms: can be a string or a list of strings - one or more permission id's
    """
    if not isinstance(perms, list):
        perms = [perms]
    for perm_id in perms:
        if not has_permission(role_key, perm_id):
            model = PermissionAssignmentModel(role_key=role_key, perm_id=perm_id)
            model.put()

def get_roles(user_key):
    q = ndb.gql("SELECT role_key FROM RoleAssignmentModel WHERE user_key = :1", user_key)
    return [role.role_key for role in q]

def check_permission(user_key, perms):
    """Check if a user is allowed to do something.
    Args:
        user: the key of the user to check
        perms: a permission or a list of permissions to check
    """
    roles = get_roles(user_key)
    if not isinstance(perms, list):
        perms = [perms]
    for perm_id in perms:
        if PermissionModel.get_by_id(perm_id) == None:
            raise Exception(u'Permission "%s" does not exist' % perm_id)
    super_admin_role = default_role("super_admin")
    if super_admin_role in roles:
        return True #If user is "super admin", everything is allowed
    for role_key in roles:
        if check_permission_role(role_key, perms):
            return True
    return False
