import main.iaas.iaas as iaas




iaas.db.create_all()


d=[]
d.append(iaas.DatabaseEngine('mysql+pymysql','MySQL'))
d.append(iaas.DatabaseEngine('postgresql','PostgreSQL'))
d.append(iaas.Group('all_users','All Users'))
d.append(iaas.Group('superusers','Superuser'))
d.append(iaas.Group('it_user','IT'))
d.append(iaas.Group('nextcloud_soge','SOGE Nextcloud User'))

for i in d:
    iaas.db.session.add(i)

iaas.db.session.commit()