import os
from flask import request
import ldapconfig

'''
Gets the users username credential
'''
def uid_trim():
    if ldapconfig.test:
        return "development_uid"
    else:
        import string
        uid = request.remote_user
        uid_stripped = string.split(uid, '@')[0]
        print uid_stripped
        return uid_stripped


# def get_dn(uid):
#     if ldapconfig.test:
#         return ""
#     else:
#         import ldap
#         searchFilter = "(&(uid=%s)(objectClass=posixAccount))" % uid
#         searchAttribute = ["dn"]
#         searchScope = ldap.SCOPE_SUBTREE
#         l = ldap.initialize(ldapconfig.ldaphost)
#         try:
#             l.protocol_version = ldap.VERSION3
#             l.simple_bind_s(ldapconfig.username, ldapconfig.password)
#             valid = True
#         except Exception, error:
#             print error
#         try:
#             ldap_result_id = l.search(ldapconfig.basedn, searchScope, searchFilter, searchAttribute)
#             result_set = []
#             result_type, result_data = l.result(ldap_result_id, 0)
#             print result_data
#             return result_data
#         except ldap.LDAPError, e:
#             print e
#         l.unbind_s()

'''
gets a user's full name and returns in the format "Firstname Surname"
'''
def get_fullname(uid=""):
    if ldapconfig.test:
        return "Firstname Surname"
    else:
        import ldap
        if uid=="":
            uid=uid_trim()
        searchFilter = "(&(uid=%s)(objectClass=posixAccount))" % uid
        searchAttribute = ["cn"]
        searchScope = ldap.SCOPE_SUBTREE
        l = ldap.initialize(ldapconfig.ldaphost)
        try:
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(ldapconfig.username, ldapconfig.password)
            valid = True
        except Exception, error:
            print error
        try:
            ldap_result_id = l.search(ldapconfig.basedn, searchScope, searchFilter, searchAttribute)
            result_set = []
            result_type, result_data = l.result(ldap_result_id, 0)
            # print result_data[0][1]['cn'][0]
            try:
                return result_data[0][1]['cn'][0]
            except Exception as e:
                print(e)
                return "Firstname Surname"
        except ldap.LDAPError, e:
            return 'An Error Occurred'
        l.unbind_s()


superusers_usernames=["cenv0594",
                      "cenv0252",
                      "hert1424"]

'''gets a list of the groups for which this user is a member'''
def get_groups(uid):
    if ldapconfig.test:
        # return[]
        return ["superusers"]
    else:
        import ldap
        searchFilter = '(|(&(objectClass=*)(memberUid=%s)))' % uid
        searchAttribute = ["cn"]
        searchScope = ldap.SCOPE_SUBTREE
        l = ldap.initialize(ldapconfig.ldaphost)
        try:
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(ldapconfig.username, ldapconfig.password)
            valid = True
        except Exception, error:
            print error
        try:
            result_set = l.search_s(ldapconfig.basedn, searchScope, searchFilter, searchAttribute)
            # result_set is a list containing lists of tuples, each containing a list - fun!
            groups = ['all_users']
            #todo: remove the next bit which is hardcoded for IT suport users
            if uid in superusers_usernames or ldapconfig.test==True:
                groups.append("superusers")
            for res in result_set:
                # disentangle the various nested stuff!
                groups.append(((res[1])['cn'])[0])
            print groups
            return groups
        except ldap.LDAPError, e:
            return []
        l.unbind_s()

'''
filters this users groups for a given service
'''
def get_groups_filtered(uid, filter):
    import string
    if ldapconfig.test:
        return ["filteredgroup1", "filteredgroup2"]
    else:
        groups=[]
        result_set = get_groups(uid)
        # result_set is a list containing lists of tuples, each containing a list - fun!
        for res in result_set:
            if res.find(filter) != -1:
                groups.append(res)
        print groups
        return groups

