# -*- coding: utf-8 -*-

from collections import OrderedDict
import datetime
from string import maketrans
from os import urandom
from binascii import hexlify

from sqlalchemy.ext.hybrid import hybrid_property

from catwatch.lib.util_sqlalchemy import ResourceMixin
from catwatch.extensions import db
from catwatch.blueprints.billing.models.credit_card import Money


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
        is_redeemable = self.redeem_by is None or \
            self.redeem_by >= datetime.datetime.utcnow()

        return self.valid and is_redeemable

    @classmethod
    def random_coupon_code(cls):
        """
        Create a human readable random coupon code.

        Inspired by:
          http://stackoverflow.com/a/22333563

        :return: Random coupon code
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
        Coupon.query.filter(condition)\
            .update({Coupon.valid: not Coupon.valid})

        return db.session.commit()

    def create(self):
        """
        Return whether or not the coupon was created successfully.

        :return: bool
        """
        return True

    def redeem(self):
        """
        Update the redeem stats for this coupon.

        :return: The result of saving the record
        """
        self.times_redeemed += 1

        if self.max_redemptions:
            if self.times_redeemed >= self.max_redemptions:
                self.valid = False

        return db.session.commit()

    def serialize(self):
        """
        Return JSON fields to render the coupon code status.

        :return: Coupon fields
        """
        params = {
            'duration': self.duration,
            'duration_in_months': self.duration_in_months,
        }

        if self.amount_off:
            params['amount_off'] = Money.cents_to_dollars(self.amount_off)

        if self.percent_off:
            params['percent_off'] = self.percent_off,

        return params


class Currency(object):
    TYPES = {
        'usd': 'United States Dollar',
        'aed': 'United Arab Emirates Dirham',
        'afn': 'Afghan Afghani',
        'all': 'Albanian Lek',
        'amd': 'Armenian Dram',
        'ang': 'Netherlands Antillean Gulden',
        'aoa': 'Angolan Kwanza',
        'ars': 'Argentine Peso',
        'aud': 'Australian Dollar',
        'awg': 'Aruban Florin',
        'azn': 'Azerbaijani Manat',
        'bam': 'Bosnia & Herzegovina Convertible Mark',
        'bbd': 'Barbadian Dollar',
        'bdt': 'Bangladeshi Taka',
        'bgn': 'Bulgarian Lev',
        'bif': 'Burundian Franc',
        'bmd': 'Bermudian Dollar',
        'bnd': 'Brunei Dollar',
        'bob': 'Bolivian Boliviano',
        'brl': 'Brazilian Real',
        'bsd': 'Bahamian Dollar',
        'bwp': 'Botswana Pula',
        'bzd': 'Belize Dollar',
        'cad': 'Canadian Dollar',
        'cdf': 'Congolese Franc',
        'chf': 'Swiss Franc',
        'clp': 'Chilean Peso',
        'cny': 'Chinese Renminbi Yuan',
        'cop': 'Colombian Peso',
        'crc': 'Costa Rican Colón',
        'cve': 'Cape Verdean Escudo',
        'czk': 'Czech Koruna',
        'djf': 'Djiboutian Franc',
        'dkk': 'Danish Krone',
        'dop': 'Dominican Peso',
        'dzd': 'Algerian Dinar',
        'eek': 'Estonian Kroon',
        'egp': 'Egyptian Pound',
        'etb': 'Ethiopian Birr',
        'eur': 'Euro',
        'fjd': 'Fijian Dollar',
        'fkp': 'Falkland Islands Pound',
        'gbp': 'British Pound',
        'gel': 'Georgian Lari',
        'gip': 'Gibraltar Pound',
        'gmd': 'Gambian Dalasi',
        'gnf': 'Guinean Franc',
        'gtq': 'Guatemalan Quetzal',
        'gyd': 'Guyanese Dollar',
        'hkd': 'Hong Kong Dollar',
        'hnl': 'Honduran Lempira',
        'hrk': 'Croatian Kuna',
        'htg': 'Haitian Gourde',
        'huf': 'Hungarian Forint',
        'idr': 'Indonesian Rupiah',
        'ils': 'Israeli New Sheqel',
        'inr': 'Indian Rupee',
        'isk': 'Icelandic Króna',
        'jmd': 'Jamaican Dollar',
        'jpy': 'Japanese Yen',
        'kes': 'Kenyan Shilling',
        'kgs': 'Kyrgyzstani Som',
        'khr': 'Cambodian Riel',
        'kmf': 'Comorian Franc',
        'krw': 'South Korean Won',
        'kyd': 'Cayman Islands Dollar',
        'kzt': 'Kazakhstani Tenge',
        'lak': 'Lao Kip',
        'lbp': 'Lebanese Pound',
        'lkr': 'Sri Lankan Rupee',
        'lrd': 'Liberian Dollar',
        'lsl': 'Lesotho Loti',
        'ltl': 'Lithuanian Litas',
        'lvl': 'Latvian Lats',
        'mad': 'Moroccan Dirham',
        'mdl': 'Moldovan Leu',
        'mga': 'Malagasy Ariary',
        'mkd': 'Macedonian Denar',
        'mnt': 'Mongolian Tögrög',
        'mop': 'Macanese Pataca',
        'mro': 'Mauritanian Ouguiya',
        'mur': 'Mauritian Rupee',
        'mvr': 'Maldivian Rufiyaa',
        'mwk': 'Malawian Kwacha',
        'mxn': 'Mexican Peso',
        'myr': 'Malaysian Ringgit',
        'mzn': 'Mozambican Metical',
        'nad': 'Namibian Dollar',
        'ngn': 'Nigerian Naira',
        'nio': 'Nicaraguan Córdoba',
        'nok': 'Norwegian Krone',
        'npr': 'Nepalese Rupee',
        'nzd': 'New Zealand Dollar',
        'pab': 'Panamanian Balboa',
        'pen': 'Peruvian Nuevo Sol',
        'pgk': 'Papua New Guinean Kina',
        'php': 'Philippine Peso',
        'pkr': 'Pakistani Rupee',
        'pln': 'Polish Złoty',
        'pyg': 'Paraguayan Guaraní',
        'qar': 'Qatari Riyal',
        'ron': 'Romanian Leu',
        'rsd': 'Serbian Dinar',
        'rub': 'Russian Ruble',
        'rwf': 'Rwandan Franc',
        'sar': 'Saudi Riyal',
        'sbd': 'Solomon Islands Dollar',
        'scr': 'Seychellois Rupee',
        'sek': 'Swedish Krona',
        'sgd': 'Singapore Dollar',
        'shp': 'Saint Helenian Pound',
        'sll': 'Sierra Leonean Leone',
        'sos': 'Somali Shilling',
        'srd': 'Surinamese Dollar',
        'std': 'São Tomé and Príncipe Dobra',
        'svc': 'Salvadoran Colón',
        'szl': 'Swazi Lilangeni',
        'thb': 'Thai Baht',
        'tjs': 'Tajikistani Somoni',
        'top': 'Tongan Paʻanga',
        'try': 'Turkish Lira',
        'ttd': 'Trinidad and Tobago Dollar',
        'twd': 'New Taiwan Dollar',
        'tzs': 'Tanzanian Shilling',
        'uah': 'Ukrainian Hryvnia',
        'ugx': 'Ugandan Shilling',
        'uyu': 'Uruguayan Peso',
        'uzs': 'Uzbekistani Som',
        'vef': 'Venezuelan Bolívar',
        'vnd': 'Vietnamese Đồng',
        'vuv': 'Vanuatu Vatu',
        'wst': 'Samoan Tala',
        'xaf': 'Central African Cfa Franc',
        'xcd': 'East Caribbean Dollar',
        'xof': 'West African Cfa Franc',
        'xpf': 'Cfp Franc',
        'yer': 'Yemeni Rial',
        'zar': 'South African Rand',
        'zmw': 'Zambian Kwacha'
    }

    @classmethod
    def lookup(cls, currency_code):
        """
        Return the full currency name.

        :param currency_code: Currency abbreviation
        :type currency_code: str
        :return: Full currency name
        """
        return Currency.TYPES[currency_code]
