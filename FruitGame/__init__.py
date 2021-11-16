from otree.api import *
import random
import itertools

c = Currency

doc = """
Fruit selection game to study language and perspective takings development. This is the main part. You only need data
from this part as information gathered in the MiscInfo part is copied over here
"""


# OTREE CLASSES
class Constants(BaseConstants):
    name_in_url = 'FruitGame'
    players_per_group = 2
    num_rounds = 1 #96
    director_role = 'Director'
    matcher_role = 'Matcher'


class Subsession(BaseSubsession):
    pass


# group call, is called once for each dyad at subsession creation
class Group(BaseGroup):
    # saves the signal symbol
    tempcom = models.StringField(initial='')
    # saves img selection
    imgselected = models.IntegerField()
    imgselectedcorrect = models.BooleanField()

    # saves blocks
    objects = models.IntegerField()
    player2pos = models.IntegerField()
    gridcolorpos = models.IntegerField()

    # saves image
    imga = models.IntegerField()
    imgb = models.IntegerField()
    imgc = models.IntegerField()

    # saves image value (correct, incorrect)
    imgavalue = models.BooleanField()
    imgbvalue = models.BooleanField()
    imgcvalue = models.BooleanField()

    # conditions


class Player(BasePlayer):
    # personal information
    age = models.IntegerField(label="Your age:", min=0)
    gender = models.StringField(label="Your gender:", choices=[["Female", "Female"],
                                                               ["Male", "Male"],
                                                               ["Nonbinary", "Nonbinary"],
                                                               ["Other", "Other: please specify"]],
                                widget=widgets.RadioSelectHorizontal)
    genderother = models.StringField(label="Specify gender here if applicable:", blank=True)
    nativelanguage = models.StringField(label="Your native language(s). Capitalized, written in english and separated "
                                              "by a semicolon (;). If unsure ask an experimenter:")
    nonnativelanguage = models.StringField(label="Your fluent non-native language(s). Capitalized, written in english "
                                                 "and separated by a semicolon (;). If unsure ask an experimenter:",
                                           blank=True)

    # Meaning mappings
    wamapping = models.StringField(label='What, if anything, is the meaning of "wa":')
    bimapping = models.StringField(label='What, if anything, is the meaning of "bi":')
    kemapping = models.StringField(label='What, if anything, is the meaning of "ke":')
    zumapping = models.StringField(label='What, if anything, is the meaning of "zu":')
    # Old question:
    # 'Describe, if applicable, what thing(s) "wa" communicates in your communications system:'

    # Final survey
    systemobject = models.BooleanField(initial=False, label='The objects themselves:')
    systemdidactic = models.BooleanField(initial=False, label='The positions of the objects relative to the Director or the Matcher:')
    systemabsolute = models.BooleanField(initial=False, label='The squares of the grid:')
    systemother = models.StringField(label='Other: Please specify', blank=True)

    adaptobject = models.StringField(label='When the objects changed:')
    adaptavatar = models.StringField(label='When the avatar(s) changed position:')
    adaptgrid = models.StringField(label='When the grid rotated:')

    selfrating = models.IntegerField(label='', choices=[1, 2, 3, 4, 5], widget=widgets.RadioSelectHorizontal)

    # number used to assign silhouette color
    number = models.IntegerField()


class Communications(ExtraModel):
    group = models.Link(Group)
    r = models.IntegerField()
    coms = models.StringField()


# FUNCTIONS
# called for each round in the session
def creating_session(subsession):
    global permutations, aa, switch, x, y, z

    # make all the switching of object, perspective and grid color permutations
    if subsession.round_number == 1:
        # make starting positions and object blocks random
        a = [[1, 2, 3, 4], [2, 3, 4, 1], [3, 4, 1, 2], [4, 1, 2, 3]]
        x = random.sample(a, 3)
        switch = [[x[0][0]] * 20 + [x[0][1]] * 24 + [x[0][2]] * 24 + [x[0][3]] * 28,
                  [x[1][0]] * 28 + [x[1][1]] * 20 + [x[1][2]] * 24 + [x[1][3]] * 24,
                  [x[2][0]] * 24 + [x[2][1]] * 28 + [x[2][2]] * 24 + [x[2][3]] * 20]
        switch = list(itertools.permutations(switch, 3))
        random.shuffle(switch)

    # flip the roles every round
    matrix = subsession.get_group_matrix()
    if subsession.round_number % 2 == 0:
        for row in matrix:
            row.reverse()
    subsession.set_group_matrix(matrix)

    # setting values for all the players
    n = 1
    for player in subsession.get_players():
        # give each player a constant number, 1 or 2 (since group in id_in_group dictates player role)
        player.number = n
        n += 1
        if n == 3:
            n = 1

    # setting values for all the groups
    for group in subsession.get_groups():
        # select the block sizes
        group.objects = switch[(group.id_in_subsession - 1) % 5][0][subsession.round_number - 1]
        group.player2pos = switch[(group.id_in_subsession - 1) % 5][1][subsession.round_number - 1]
        group.gridcolorpos = switch[(group.id_in_subsession - 1) % 5][2][subsession.round_number - 1]

        # make the all permutations of the object ordering (pseudorandom)
        if subsession.round_number == 1:
            permutations = list(itertools.permutations([1, 2, 3, 4], 3))
            random.shuffle(permutations)

        # select the images form the current image block
        if group.objects == 1:
            group.imga = permutations[(subsession.round_number - 1) % 24][0]
            group.imgb = permutations[(subsession.round_number - 1) % 24][1]
            group.imgc = permutations[(subsession.round_number - 1) % 24][2]
        elif group.objects == 2:
            group.imga = permutations[(subsession.round_number - 1) % 24][0] + 4
            group.imgb = permutations[(subsession.round_number - 1) % 24][1] + 4
            group.imgc = permutations[(subsession.round_number - 1) % 24][2] + 4
        elif group.objects == 3:
            group.imga = permutations[(subsession.round_number - 1) % 24][0] + 8
            group.imgb = permutations[(subsession.round_number - 1) % 24][1] + 8
            group.imgc = permutations[(subsession.round_number - 1) % 24][2] + 8
        else:
            group.imga = permutations[(subsession.round_number - 1) % 24][0] + 12
            group.imgb = permutations[(subsession.round_number - 1) % 24][1] + 12
            group.imgc = permutations[(subsession.round_number - 1) % 24][2] + 12

        # select the value of the objects
        # this seems very bad practice, but I cannot come up with a better solution. good enough
        if player.round_number == 1 or player.in_round(player.round_number - 1).group.objects != group.objects:
            x = [1] * 2 + [2] * 2 + [3] * 2 + [4] * 2
            y = [1] * 2 + [2] * 2 + [3] * 2 + [4] * 2
            z = [1] * 2 + [2] * 2 + [3] * 2 + [4] * 2
            random.shuffle(x)
            random.shuffle(y)
            random.shuffle(z)
            aa = [0] * 24

        if aa[0] != 1 and permutations[(subsession.round_number - 1) % 24][0] == x[0]:
            imgvalue = [True, False, False]
            aa[0] += 1
        elif aa[1] != 1 and permutations[(subsession.round_number - 1) % 24][1] == y[0]:
            imgvalue = [False, True, False]
            aa[1] += 1
        elif aa[2] != 1 and permutations[(subsession.round_number - 1) % 24][2] == z[0]:
            imgvalue = [False, False, True]
            aa[2] += 1
        elif aa[3] != 1 and permutations[(subsession.round_number - 1) % 24][0] == x[1]:
            imgvalue = [True, False, False]
            aa[3] += 1
        elif aa[4] != 1 and permutations[(subsession.round_number - 1) % 24][1] == y[1]:
            imgvalue = [False, True, False]
            aa[4] += 1
        elif aa[5] != 1 and permutations[(subsession.round_number - 1) % 24][2] == z[1]:
            imgvalue = [False, False, True]
            aa[5] += 1
        elif aa[6] != 1 and permutations[(subsession.round_number - 1) % 24][0] == x[2]:
            imgvalue = [True, False, False]
            aa[6] += 1
        elif aa[7] != 1 and permutations[(subsession.round_number - 1) % 24][1] == y[2]:
            imgvalue = [False, True, False]
            aa[7] += 1
        elif aa[8] != 1 and permutations[(subsession.round_number - 1) % 24][2] == z[2]:
            imgvalue = [False, False, True]
            aa[8] += 1
        elif aa[9] != 1 and permutations[(subsession.round_number - 1) % 24][0] == x[3]:
            imgvalue = [True, False, False]
            aa[9] += 1
        elif aa[10] != 1 and permutations[(subsession.round_number - 1) % 24][1] == y[3]:
            imgvalue = [False, True, False]
            aa[10] += 1
        elif aa[11] != 1 and permutations[(subsession.round_number - 1) % 24][2] == z[3]:
            imgvalue = [False, False, True]
            aa[11] += 1
        elif aa[12] != 1 and permutations[(subsession.round_number - 1) % 24][0] == x[4]:
            imgvalue = [True, False, False]
            aa[12] += 1
        elif aa[13] != 1 and permutations[(subsession.round_number - 1) % 24][1] == y[4]:
            imgvalue = [False, True, False]
            aa[13] += 1
        elif aa[14] != 1 and permutations[(subsession.round_number - 1) % 24][2] == z[4]:
            imgvalue = [False, False, True]
            aa[14] += 1
        elif aa[15] != 1 and permutations[(subsession.round_number - 1) % 24][0] == x[5]:
            imgvalue = [True, False, False]
            aa[15] += 1
        elif aa[16] != 1 and permutations[(subsession.round_number - 1) % 24][1] == y[5]:
            imgvalue = [False, True, False]
            aa[16] += 1
        elif aa[17] != 1 and permutations[(subsession.round_number - 1) % 24][2] == z[5]:
            imgvalue = [False, False, True]
            aa[17] += 1
        elif aa[18] != 1 and permutations[(subsession.round_number - 1) % 24][0] == x[6]:
            imgvalue = [True, False, False]
            aa[18] += 1
        elif aa[19] != 1 and permutations[(subsession.round_number - 1) % 24][1] == y[6]:
            imgvalue = [False, True, False]
            aa[19] += 1
        elif aa[20] != 1 and permutations[(subsession.round_number - 1) % 24][2] == z[6]:
            imgvalue = [False, False, True]
            aa[20] += 1
        elif aa[21] != 1 and permutations[(subsession.round_number - 1) % 24][0] == x[7]:
            imgvalue = [True, False, False]
            aa[21] += 1
        elif aa[22] != 1 and permutations[(subsession.round_number - 1) % 24][1] == y[7]:
            imgvalue = [False, True, False]
            aa[22] += 1
        elif aa[23] != 1 and permutations[(subsession.round_number - 1) % 24][2] == z[7]:
            imgvalue = [False, False, True]
            aa[23] += 1
        else:
            imgvalue = random.sample([True, False, False], k=3)
        group.imgavalue = imgvalue[0]
        group.imgbvalue = imgvalue[1]
        group.imgcvalue = imgvalue[2]


# PAGES
class MainPage(Page):
    # Amount of time before timeout in seconds
    timeout_seconds = 60

    # Decide what happens if timeout
    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.group.imgselected = 0
            player.group.imgselectedcorrect = False

    # For finding the image path for each image placement and silhouette
    @staticmethod
    def vars_for_template(player):
        group = player.group

        # calculating score
        score = 0
        for p in player.in_previous_rounds():
            if p.group.imgselectedcorrect:
                score += 1

        # find out with silhouette to use
        if player.number == 1:
            if player.role == "Director":
                silhouetteme = 'FruitGame/Player1Director.png'
                silhouetteother = 'FruitGame/Player2Matcher.png'
            else:
                silhouetteme = 'FruitGame/Player1Matcher.png'
                silhouetteother = 'FruitGame/Player2Director.png'
        else:
            if player.role == "Director":
                silhouetteme = 'FruitGame/Player2Director.png'
                silhouetteother = 'FruitGame/Player1Matcher.png'
            else:
                silhouetteme = 'FruitGame/Player2Matcher.png'
                silhouetteother = 'FruitGame/Player1Director.png'

        return dict(image_patha='FruitGame/{}.png'.format(group.imga),
                    image_pathb='FruitGame/{}.png'.format(group.imgb),
                    image_pathc='FruitGame/{}.png'.format(group.imgc),
                    silhouetteme=silhouetteme,
                    silhouetteother=silhouetteother,
                    score=score)

    # Returns player role for javascript functions
    @staticmethod
    def js_vars(player):
        return dict(
            role=player.role
        )

    # Control input received from players and outputs back to them
    @staticmethod
    def live_method(player, data):
        group = player.group
        send = []
        if 'select' in data:  # End round
            send.append('nextpage')
            if '1' in data:
                group.imgselected = group.imga
                group.imgselectedcorrect = group.imgavalue
            elif '2' in data:
                group.imgselected = group.imgb
                group.imgselectedcorrect = group.imgbvalue
            elif '3' in data:
                group.imgselected = group.imgc
                group.imgselectedcorrect = group.imgcvalue
            y = Communications.filter(group=group, r=player.round_number)
            messageoutput = ''
            for x in y:
                messageoutput = messageoutput + x.coms + ' '
            group.tempcom = messageoutput
            return {0: send}
        if 'send' in data:  # Send new message
            Communications.create(group=group, r=player.round_number, coms=group.tempcom)
            group.tempcom = ''
            y = Communications.filter(group=group, r=player.round_number)
            for x in y:
                send.append('Director: ' + x.coms)
            send.append('Message: ' + group.tempcom)
            return {0: send}
        elif 'undo' in data:  # Remove last from the unsent message
            group.tempcom = group.tempcom[:-2]
        else:  # Add to the unsent message
            group.tempcom = group.tempcom + data
        y = Communications.filter(group=group, r=player.round_number)
        for x in y:
            send.append('Director: ' + x.coms)
        send.append('Message: ' + group.tempcom)
        return {player.id_in_group: send}


class StartWaitPage(WaitPage):
    pass


class Results(Page):
    pass


# Tells the players if the perspective has just changed
class PerspectiveChange(Page):
    @staticmethod
    def is_displayed(player):
        if player.round_number == 1:
            return False
        return player.in_round(player.round_number - 1).group.player2pos != player.group.player2pos


# Tells the players if the objects have just changed
class ObjectChange(Page):
    @staticmethod
    def is_displayed(player):
        if player.round_number == 1:
            return False
        return player.in_round(player.round_number - 1).group.objects != player.group.objects


# Tells the players if the grid colors have just changed
class GridColorChange(Page):
    @staticmethod
    def is_displayed(player):
        if player.round_number == 1:
            return False
        return player.in_round(player.round_number - 1).group.gridcolorpos != player.group.gridcolorpos


# Small survey asking what each symbol maps to
class MidSurvey(Page):
    form_model = 'player'
    form_fields = ['wamapping', 'bimapping', 'kemapping', 'zumapping']

    @staticmethod
    def is_displayed(player):
        return player.round_number % 24 == 18


# More detailed survey asking what each symbol maps to
class EndSurvey1(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds


class EndSurvey2(Page):
    form_model = 'player'
    form_fields = ['systemobject', 'systemdidactic', 'systemabsolute', 'systemother']

    # in case no information is entered
    @staticmethod
    def error_message(player, value):
        if value['systemobject'] is False and value['systemdidactic'] is False and value['systemabsolute'] is False \
                and value['systemother'] is '':
            return 'If none of the options match your system please specify in the text box'

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds


class EndSurvey3(Page):
    form_model = 'player'
    form_fields = ['adaptobject', 'adaptavatar', 'adaptgrid']

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds


class EndSurvey4(Page):
    form_model = 'player'
    form_fields = ['selfrating']

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds


# Page that tell the player that the experiment has begun (only round 1)
class Start1(Page):

    @staticmethod
    def before_next_page(player, timeout_happened):
        # copying over personal information
        for p in player.in_rounds(1, Constants.num_rounds):
            p.age = player.participant.age
            p.gender = player.participant.gender
            p.genderother = player.participant.genderother
            p.nativelanguage = player.participant.nativelanguage
            p.nonnativelanguage = player.participant.nonnativelanguage

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Start2(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Start3(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


page_sequence = [Start1, Start2, Start3,
                 PerspectiveChange, ObjectChange, GridColorChange,
                 StartWaitPage, MainPage, Results,
                 MidSurvey, EndSurvey1, EndSurvey2, EndSurvey3, EndSurvey4]
