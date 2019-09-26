# What does this do?
This is a radicale plugin enabling LDAP users to access shared group calendars.
The plugin  simply checks if a user owns the calendar or is member of the group that owns
the calendar and gives **read** and **write** permissions if the check is successful.

The following configuration is needed:

```
[rights]

type = radicale-rights-ldap

# LDAP server url, with protocol and optionally port.
ldap_url = ldap://ldapserver:389

# LDAP user base path
user_base = ou=People,dc=domain

# LDAP group base path
group_base = ou=Groups,dc=domain

# LDAP user bottom level dn path attribute
user_attribute = uid

# LDAP user bottom level dn path attribute
group_attribute = cn

# LDAP dn for login
ldap_binddn = uid=admin,dc=Domain

# LDAP Password for ldap_binddn
ldap_password = swordfish1234

# LDAP filter for which users get managed by the plugin
ldap_filter = memberOf=cn=radicaleUsers,ou=Groups,dc=Domain

# LDAP scope of the search, default is SUBTREE
ldap_scope = LEVEL
```
