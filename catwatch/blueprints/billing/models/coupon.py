# -*- coding: utf-8 -*-

import datetime
from collections import OrderedDict
from string import maketrans
from os import urandom
from binascii import hexlify

from sqlalchemy import or_, and_

from sqlalchemy.ext.hybrid import hybrid_property

from catwatch.lib.util_sqlalchemy import ResourceMixin
from catwatch.lib.money import cents_to_dollars, dollars_to_cents
from catwatch.extensions import db
from catwatch.blueprints.billing.gateways.stripecom import \
    Coupon as PaymentCoupon


class Coupon(ResourceMixin, db.Model):
    DURATION = OrderedDict([
        ('forever', 'Forever'),
        ('once', 'Once'),
        ('repeating', 'Repeating')
    ])

    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)

    # Coupon details.
    code = db.Column(db.String(32), index=True, unique=True)
    duration = db.Column(db.Enum(*DURATION, name='duration_types'),
                         index=True, nullable=False, server_default='forever')
    amount_off = db.Column(db.Integer())
    percent_off = db.Column(db.Integer())
    currency = db.Column(db.String(8))
    duration_in_months = db.Column(db.Integer())
    max_redemptions = db.Column(db.Integer(), index=True)
    redeem_by = db.Column(db.DateTime(), index=True)
    times_redeemed = db.Column(db.Integer(), index=True,
                               nullable=False, default=0)
    valid = db.Column(db.Boolean(), nullable=False, server_default='1')

    def __init__(self, **kwargs):
        if self.code:
            self.code = self.code.upper()
        else:
            self.code = Coupon.random_coupon_code()

        # Call Flask-SQLAlchemy's constructor.
        super(Coupon, self).__init__(**kwargs)

    @hybrid_property
    def redeemable(self):
        """
        Return coupons that are still redeemable. Coupons will become invalid
        once they run out on save. We want to explicitly do a date check to
        avoid having to hit Stripe's API to get back potentially valid codes.

        :return: SQLAlchemy query object
        """
        is_redeemable = or_(self.redeem_by.is_(None),
                            self.redeem_by >= datetime.datetime.utcnow())

        return and_(self.valid, is_redeemable)

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)

        return or_(Coupon.code.ilike(search_query))

    @classmethod
    def random_coupon_code(cls):
        """
        Create a human readable random coupon code.

        Inspired by:
          http://stackoverflow.com/a/22333563

        :return: str
        """
        random_string = hexlify(urandom(20))
        long_code = random_string.translate(maketrans('0123456789abcdefghij',
                                                      '234679QWERTYUPADFGHX'))

        short_code = '{0}-{1}-{2}'.format(long_code[0:4],
                                          long_code[5:9],
                                          long_code[10:14])

        return short_code

    @classmethod
    def expire_old_coupons(cls, compare_datetime=None):
        """
        Invalidate coupons that are past their redeem date.

        :param compare_datetime: Time to compare at
        :type compare_datetime: date
        :return: The result of updating the records
        """
        if compare_datetime is None:
            compare_datetime = datetime.datetime.today()

        condition = Coupon.redeem_by <= compare_datetime
        Coupon.query.filter(condition) \
            .update({Coupon.valid: not Coupon.valid})

        return db.session.commit()

    @classmethod
    def create(cls, params):
        """
        Return whether or not the coupon was created successfully.

        :return: bool
        """
        payment_params = params

        if payment_params.get('amount_off'):
            payment_params['amount_off'] = \
                dollars_to_cents(payment_params['amount_off'])

        PaymentCoupon.create(payment_params)

        if 'id' in payment_params:
            payment_params['code'] = payment_params['id']
            del payment_params['id']

        coupon = Coupon(**payment_params)

        db.session.add(coupon)
        db.session.commit()

        return True

    @classmethod
    def bulk_delete(cls, ids):
        """
        Override the general bulk_delete method because we need to delete them
        one at a time while also deleting them on Stripe.

        :param ids: List of ids to be deleted
        :type ids: list
        :return: int
        """
        delete_count = 0

        for id in ids:
            coupon = Coupon.query.get(id)

            if coupon is None:
                return 0

            # Delete on Stripe.
            stripe_response = PaymentCoupon.delete(coupon.code)

            # If successful, delete it locally.
            if stripe_response.get('deleted'):
                coupon.delete()
                delete_count += 1

        return delete_count

    @classmethod
    def find_by_code(cls, code):
        """
        Find a coupon by its code.

        :param code: Coupon code to find
        :type code: str
        :return: Coupon instance
        """
        formatted_code = code.upper()
        coupon = Coupon.query.filter(Coupon.redeemable,
                                     Coupon.code == formatted_code).first()

        return coupon

    def redeem(self):
        """
        Update the redeem stats for this coupon.

        :return: Result of saving the record
        """
        self.times_redeemed += 1

        if self.max_redemptions:
            if self.times_redeemed >= self.max_redemptions:
                self.valid = False

        return db.session.commit()

    def serialize(self):
        """
        Return JSON fields to render the coupon code status.

        :return: dict
        """
        params = {
            'duration': self.duration,
            'duration_in_months': self.duration_in_months,
        }

        if self.amount_off:
            params['amount_off'] = cents_to_dollars(self.amount_off)

        if self.percent_off:
            params['percent_off'] = self.percent_off,

        return params


class Currency(object):
    TYPES = OrderedDict([
        ('usd', u'United States Dollar'),
        ('aed', u'United Arab Emirates Dirham'),
        ('afn', u'Afghan Afghani'),
        ('all', u'Albanian Lek'),
        ('amd', u'Armenian Dram'),
        ('ang', u'Netherlands Antillean Gulden'),
        ('aoa', u'Angolan Kwanza'),
        ('ars', u'Argentine Peso'),
        ('aud', u'Australian Dollar'),
        ('awg', u'Aruban Florin'),
        ('azn', u'Azerbaijani Manat'),
        ('bam', u'Bosnia & Herzegovina Convertible Mark'),
        ('bbd', u'Barbadian Dollar'),
        ('bdt', u'Bangladeshi Taka'),
        ('bgn', u'Bulgarian Lev'),
        ('bif', u'Burundian Franc'),
        ('bmd', u'Bermudian Dollar'),
        ('bnd', u'Brunei Dollar'),
        ('bob', u'Bolivian Boliviano'),
        ('brl', u'Brazilian Real'),
        ('bsd', u'Bahamian Dollar'),
        ('bwp', u'Botswana Pula'),
        ('bzd', u'Belize Dollar'),
        ('cad', u'Canadian Dollar'),
        ('cdf', u'Congolese Franc'),
        ('chf', u'Swiss Franc'),
        ('clp', u'Chilean Peso'),
        ('cny', u'Chinese Renminbi Yuan'),
        ('cop', u'Colombian Peso'),
        ('crc', u'Costa Rican Colón'),
        ('cve', u'Cape Verdean Escudo'),
        ('czk', u'Czech Koruna'),
        ('djf', u'Djiboutian Franc'),
        ('dkk', u'Danish Krone'),
        ('dop', u'Dominican Peso'),
        ('dzd', u'Algerian Dinar'),
        ('eek', u'Estonian Kroon'),
        ('egp', u'Egyptian Pound'),
        ('etb', u'Ethiopian Birr'),
        ('eur', u'Euro'),
        ('fjd', u'Fijian Dollar'),
        ('fkp', u'Falkland Islands Pound'),
        ('gbp', u'British Pound'),
        ('gel', u'Georgian Lari'),
        ('gip', u'Gibraltar Pound'),
        ('gmd', u'Gambian Dalasi'),
        ('gnf', u'Guinean Franc'),
        ('gtq', u'Guatemalan Quetzal'),
        ('gyd', u'Guyanese Dollar'),
        ('hkd', u'Hong Kong Dollar'),
        ('hnl', u'Honduran Lempira'),
        ('hrk', u'Croatian Kuna'),
        ('htg', u'Haitian Gourde'),
        ('huf', u'Hungarian Forint'),
        ('idr', u'Indonesian Rupiah'),
        ('ils', u'Israeli New Sheqel'),
        ('inr', u'Indian Rupee'),
        ('isk', u'Icelandic Króna'),
        ('jmd', u'Jamaican Dollar'),
        ('jpy', u'Japanese Yen'),
        ('kes', u'Kenyan Shilling'),
        ('kgs', u'Kyrgyzstani Som'),
        ('khr', u'Cambodian Riel'),
        ('kmf', u'Comorian Franc'),
        ('krw', u'South Korean Won'),
        ('kyd', u'Cayman Islands Dollar'),
        ('kzt', u'Kazakhstani Tenge'),
        ('lak', u'Lao Kip'),
        ('lbp', u'Lebanese Pound'),
        ('lkr', u'Sri Lankan Rupee'),
        ('lrd', u'Liberian Dollar'),
        ('lsl', u'Lesotho Loti'),
        ('ltl', u'Lithuanian Litas'),
        ('lvl', u'Latvian Lats'),
        ('mad', u'Moroccan Dirham'),
        ('mdl', u'Moldovan Leu'),
        ('mga', u'Malagasy Ariary'),
        ('mkd', u'Macedonian Denar'),
        ('mnt', u'Mongolian Tögrög'),
        ('mop', u'Macanese Pataca'),
        ('mro', u'Mauritanian Ouguiya'),
        ('mur', u'Mauritian Rupee'),
        ('mvr', u'Maldivian Rufiyaa'),
        ('mwk', u'Malawian Kwacha'),
        ('mxn', u'Mexican Peso'),
        ('myr', u'Malaysian Ringgit'),
        ('mzn', u'Mozambican Metical'),
        ('nad', u'Namibian Dollar'),
        ('ngn', u'Nigerian Naira'),
        ('nio', u'Nicaraguan Córdoba'),
        ('nok', u'Norwegian Krone'),
        ('npr', u'Nepalese Rupee'),
        ('nzd', u'New Zealand Dollar'),
        ('pab', u'Panamanian Balboa'),
        ('pen', u'Peruvian Nuevo Sol'),
        ('pgk', u'Papua New Guinean Kina'),
        ('php', u'Philippine Peso'),
        ('pkr', u'Pakistani Rupee'),
        ('pln', u'Polish Złoty'),
        ('pyg', u'Paraguayan Guaraní'),
        ('qar', u'Qatari Riyal'),
        ('ron', u'Romanian Leu'),
        ('rsd', u'Serbian Dinar'),
        ('rub', u'Russian Ruble'),
        ('rwf', u'Rwandan Franc'),
        ('sar', u'Saudi Riyal'),
        ('sbd', u'Solomon Islands Dollar'),
        ('scr', u'Seychellois Rupee'),
        ('sek', u'Swedish Krona'),
        ('sgd', u'Singapore Dollar'),
        ('shp', u'Saint Helenian Pound'),
        ('sll', u'Sierra Leonean Leone'),
        ('sos', u'Somali Shilling'),
        ('srd', u'Surinamese Dollar'),
        ('std', u'São Tomé and Príncipe Dobra'),
        ('svc', u'Salvadoran Colón'),
        ('szl', u'Swazi Lilangeni'),
        ('thb', u'Thai Baht'),
        ('tjs', u'Tajikistani Somoni'),
        ('top', u'Tongan Paʻanga'),
        ('try', u'Turkish Lira'),
        ('ttd', u'Trinidad and Tobago Dollar'),
        ('twd', u'New Taiwan Dollar'),
        ('tzs', u'Tanzanian Shilling'),
        ('uah', u'Ukrainian Hryvnia'),
        ('ugx', u'Ugandan Shilling'),
        ('uyu', u'Uruguayan Peso'),
        ('uzs', u'Uzbekistani Som'),
        ('vef', u'Venezuelan Bolívar'),
        ('vnd', u'Vietnamese Đồng'),
        ('vuv', u'Vanuatu Vatu'),
        ('wst', u'Samoan Tala'),
        ('xaf', u'Central African Cfa Franc'),
        ('xcd', u'East Caribbean Dollar'),
        ('xof', u'West African Cfa Franc'),
        ('xpf', u'Cfp Franc'),
        ('yer', u'Yemeni Rial'),
        ('zar', u'South African Rand'),
        ('zmw', u'Zambian Kwacha')
    ])

    @classmethod
    def lookup(cls, currency_code):
        """
        Return the full currency name.

        :param currency_code: Currency abbreviation
        :type currency_code: str
        :return: str
        """
        return Currency.TYPES[currency_code]
