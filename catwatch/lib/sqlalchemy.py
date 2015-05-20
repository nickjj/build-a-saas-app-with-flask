import datetime

from catwatch.extensions import db


class ResourceMixin(object):
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow(),
                           onupdate=datetime.datetime.utcnow())

    def save(self):
        """
        Save a model instance.

        :return: Model instance
        """
        db.session.add(self)
        db.session.commit()

        return self

    def delete(self):
        """
        Delete a model instance.

        :return: db.session.commit()'s result
        """
        db.session.add(self)
        return db.session.commit()

    def __str__(self):
        """
        Create a human readable version of a class instance.

        :return:
        """
        obj_id = hex(id(self))
        columns = self.__table__.c.keys()

        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in columns)
        return '<%s %s(%s)>' % (obj_id, self.__class__.__name__, values)
