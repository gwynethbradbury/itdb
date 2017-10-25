import os


basedn = "dc=iaas,dc=ouce,dc=ox,dc=ac,dc=uk"
ldaphost = 'ldap://ldap.iaas.ouce.ox.ac.uk'
username = "cn=admin,dc=iaas,dc=ouce,dc=ox,dc=ac,dc=uk"
password = "9rW2P7AyWCy2CMI6QgdU"

# Handling for talking to OUCE AD for people not currently registered as IAAS users
basedn_ad = "dc=ouce,dc=ox,dc=ac,dc=uk"
ldaphost_ad = 'ldap://ouce-dc0.ouce.ox.ac.uk'
username_ad="ouce\\adtool"
password_ad="e6HMjLmiFvGhtHIrUwS3"

test = True


