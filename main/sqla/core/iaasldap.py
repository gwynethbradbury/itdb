import os
from flask import request
import ldapconfig


class LDAPUser():

    def confirmed(self):
        return True
    def is_anonymous(self):
        return False

    '''
    Gets the users username credential
    '''
    def uid_trim(self):
        if ldapconfig.test:
            return "cenv0594"
        else:
            import string
            uid = request.remote_user
            uid_stripped = string.split(uid, '@')[0]
            print uid_stripped
            return uid_stripped
    '''
    Gets the users username credential
    '''
    def uid_suffix(self):
        if ldapconfig.test:
            return "development_suffix"
        else:
            import string
            uid = request.remote_user
            uid_stripped = string.split(uid, '@')[1]
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
    def get_fullname(self,uid=""):
        if ldapconfig.test:
            return "Firstname Surname"
        else:
            import ldap
            if uid=="":
                uid=self.uid_trim()
            suffix=self.uid_suffix()
            if (suffix=="ox.ac.uk"):
               searchFilter = "(&(objectClass=user)(sAMAccountName=%s))" % uid
               searchAttribute = ["displayName"]
               searchScope = ldap.SCOPE_SUBTREE
               l = ldap.initialize(ldapconfig.ldaphost_ad)
               try:
                   l.protocol_version = ldap.VERSION3
                   l.simple_bind_s(ldapconfig.username_ad, ldapconfig.password_ad)
                   valid = True
               except Exception, error:
                   print error
               try:
                   ldap_result_id = l.search(ldapconfig.basedn_ad, searchScope, searchFilter, searchAttribute)
                   result_type, result_data = l.result(ldap_result_id, 0)
                   try:
                       return result_data[0][1]['displayName'][0]
                   except Exception as e:
                       print(e)
                       return "Firstname Surname"
               except ldap.LDAPError, e:
                   return 'An Error Occurred (AD)'
               l.unbind_s()



            else:
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
                   result_type, result_data = l.result(ldap_result_id, 0)
                   try:
                       return result_data[0][1]['cn'][0]
                   except Exception as e:
                       print(e)
                       return "Firstname Surname"
               except ldap.LDAPError, e:
                   return 'An Error Occurred'
               l.unbind_s()


    # # For testing
    # superusers_usernames=["cenv0594",
    #                       "cenv0252",
    #                       "hert1424"]

    '''gets a list of the groups for which this user is a member'''
    def get_groups(self):
        uid = self.uid_trim()
        groups = ['all_users']
        if ldapconfig.test:
            # return[]
            groups.append("superusers")
            # groups.append("onlinelrn")
            return groups
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
                for res in result_set:
                    # disentangle the various nested stuff!
                    groups.append(((res[1])['cn'])[0])
                # print groups
                return groups
            except ldap.LDAPError, e:
                return []
            l.unbind_s()

    '''
    filters this users groups for a given service
    '''
    def get_groups_filtered(self, filter):
        uid = self.uid_trim()
        import string
        if ldapconfig.test:
            return ["filteredgroup1", "filteredgroup2"]
        else:
            groups=[]
            result_set = self.get_groups()
            # result_set is a list containing lists of tuples, each containing a list - fun!
            for res in result_set:
                if res.find(filter) != -1:
                    groups.append(res)
            print groups
            return groups


    '''
    check whether this user is authorised against the given project
    '''
    def is_authenticated(self):
        #todo: complete authentication rules
        return True

    def is_active(self):
        return True

    def has_role(self,role):
        if role in self.get_groups():
            return True
        return False

    '''
    Determines whether a user is authorised to view this project
    caveat: if this is an admin-only page, _admin is added to the group name
    '''
    def is_authorised(self, service_name, is_admin_only_page=False):
        if "development_uid" == self.uid_trim():
            return True

        usersgroups = self.get_groups()
        if "superusers" in usersgroups:
            return True
        if is_admin_only_page:
            service_name = service_name + "_admin"
        if service_name in usersgroups:
            return True
        return False

    def change_password(self,old_password,new_password,repeat_password):
        success=0
        msg="Could not change password. "
        if self.is_correct_password(old_password):
            if new_password==repeat_password:
                # change the password
                self._set_password(self.uid_trim(),old_password,new_password)
                msg="Password changed successfully"
                success=1
            else:
                msg=msg+"New password inconsistent."
        else:
            msg=msg+"Old password does not match."

        return success, msg


    def _set_password(self, uid, oldpw,newpw):
        #todo
        # pass

        if ldapconfig.test:
            return

        import ldap

        suffix = self.uid_suffix()
        if (suffix == "ox.ac.uk"):
            # searchFilter = "(&(objectClass=user)(sAMAccountName=%s))" % uid
            # searchAttribute = ["displayName"]
            # searchScope = ldap.SCOPE_SUBTREE
            l = ldap.initialize(ldapconfig.ldaphost_ad)
            l.protocol_version = ldap.VERSION3
            try:
                l.simple_bind_s(ldapconfig.username_ad, ldapconfig.password_ad)
            except Exception, error:
                print error

            try:
                l.passwd_s(uid, oldpw, newpw)

            except ldap.LDAPError, e:
                return 'An Error Occurred (AD)'
            l.unbind_s()



        else:
            # searchFilter = "(&(uid=%s)(objectClass=posixAccount))" % uid
            # searchAttribute = ["cn"]
            # searchScope = ldap.SCOPE_SUBTREE
            l = ldap.initialize(ldapconfig.ldaphost)
            l.protocol_version = ldap.VERSION3
            try:
                l.simple_bind_s(ldapconfig.username, ldapconfig.password)
            except Exception, error:
                print error

            try:
                l.passwd_s(uid, oldpw, newpw)

            except ldap.LDAPError, e:
                return 'An Error Occurred (AD)'
            l.unbind_s()




        # self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        # todo:
        return True
        # return bcrypt.check_password_hash(self._password, plaintext)

