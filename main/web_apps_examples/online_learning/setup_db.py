import main.web_apps_examples.online_learning as online_learning




online_learning.onlinelearningdb.create_all()

d=[]
# GIS Machine Learning Python Flask Linux Image Processing
d.append(online_learning.models.topic('GIS'))
d.append(online_learning.models.topic('Machine Learning'))
d.append(online_learning.models.topic('Python'))
d.append(online_learning.models.topic('Flask'))
d.append(online_learning.models.topic('Linux'))
d.append(online_learning.models.topic('Image Processing'))


d.append(online_learning.models.tag())
for i in d:
    online_learning.onlinelearningdb.session.add(i)
online_learning.onlinelearningdb.session.commit()

p=online_learning.models.page()
p.tags=online_learning.models.tag.query.all()
p.topics=online_learning.models.topic.query.all()
online_learning.onlinelearningdb.session.add(p)
online_learning.onlinelearningdb.session.commit()
p = online_learning.models.page.query.first()

d=[]
d.append(online_learning.models.comment(page_inst=p))
d.append(online_learning.models.video(page_inst=p))
for i in d:
    online_learning.onlinelearningdb.session.add(i)
online_learning.onlinelearningdb.session.commit()