from os import environ

SESSION_CONFIGS = [
    dict(
        name='Communications_Game',
        app_sequence=['FruitGameMiscInfo', 'FruitGame'],
        num_demo_participants=2,
        avatarvisable=True,
        seqrandom=True,
        seq0=False,
        seq1=False,
        seq2=False,
        seq3=False,
        seq4=False,
        seq5=False,
        doc="""
            | seq0:[[20, 24, 24, 28]], [[28, 20, 24, 24]], [[24, 28, 24, 20]] 
            | seq1:[[20, 24, 24, 28]], [[24, 28, 24, 20]], [[28, 20, 24, 24]] 
            | seq2:[[28, 20, 24, 24]], [[20, 24, 24, 28]], [[24, 28, 24, 20]] 
            | seq3:[[28, 20, 24, 24]], [[24, 28, 24, 20]], [[20, 24, 24, 28]] 
            | seq4:[[24, 28, 24, 20]], [[20, 24, 24, 28]], [[28, 20, 24, 24]] 
            | seq5:[[24, 28, 24, 20]], [[28, 20, 24, 24]], [[20, 24, 24, 28]] 
            """
    ),
]

ROOMS = [
    dict(
        name='exp',
        display_name='Communications Game'
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['temptime', 'starttimer', 'truestarttimer', 'age', 'gender', 'genderother',  'nativelanguage', 'nonnativelanguage']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '2623070546888'
