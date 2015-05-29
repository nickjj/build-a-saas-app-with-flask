import datetime

from catwatch.extensions import db


class ResourceMixin(object):
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow(),
                           onupdate=datetime.datetime.utcnow())

    @classmethod
    def sort_by(cls, field, direction):
        """
        Sort a resource by a specific field and direction.

        :param field: Field name
        :type field: str
        :param direction: Direction
        :type direction: str
        :return: The field and direction
        """
        if field not in cls.__table__.columns:
            field = 'created_on'

        if direction not in ('asc', 'desc'):
            direction = 'asc'

        return field, direction

    @classmethod
    def get_bulk_action_ids(cls, scope, ids, omit_ids=[],
                            query='', query_fields=()):
        """
        Determine which IDs are to be modified.

        :param scope: Affect all or only a subset of items
        :type scope: str
        :param ids: List of ids to be modified
        :type ids: list
        :param omit_ids: Remove 1 or more IDs from the list
        :type omit_ids: list
        :param query: Search query (if applicable)
        :type query: str
        :param query_fields: Fields to search (if applicable)
        :type query_fields: tuple
        :return: List of ids
        """
        omit_ids = map(str, omit_ids)

        if scope == 'all_search_results':
            # Change the scope to go from selected ids to all search results.
            ids = cls.query.with_entities(cls.id) \
                .filter(cls.search(query, query_fields))

            # SQLAlchemy returns back a list of tuples, we want a list of strs.
            ids = [str(item[0]) for item in ids]

        # Remove 1 or more items from the list, this could be useful in spots
        # where you may want to protect the current user from deleting himself
        # when bulk deleting user accounts.
        if omit_ids:
            ids = [id for id in ids if id not in omit_ids]

        return ids

    @classmethod
    def bulk_delete(cls, ids):
        """
        Delete 1 or more model instances

        :param ids: List of ids to be deleted
        :type ids: list
        :return: Number of deleted instances
        """
        delete_count = cls.query.filter(cls.id.in_(ids)).delete(
            synchronize_session=False)
        db.session.commit()

        return delete_count

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
        db.session.delete(self)
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
