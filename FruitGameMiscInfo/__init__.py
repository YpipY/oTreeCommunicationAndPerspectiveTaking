from otree.api import *
import random
import itertools

c = Currency

doc = """
Fruit selection game to study language and perspective takings development. This is the introduction, practice and
personal information gathering part. The data from this part can be discarded as it is copied over into the main app
"""


# OTREE CLASSES
class Constants(BaseConstants):
    name_in_url = 'FruitGameMiscInfo'
    players_per_group = 2
    num_rounds = 4
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
        x = [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]]
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
            permutations = [[1, 2, 3], [3, 4, 1], [2, 3, 4], [1, 4, 3]]
            #permutations = list(itertools.permutations([1, 2, 3, 4], 3))
            #random.shuffle(permutations)

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
                silhouetteme = 'FruitGame/Player1DirectorMe.png'
                silhouetteother = 'FruitGame/Player2MatcherPartner.png'
            else:
                silhouetteme = 'FruitGame/Player1MatcherMe.png'
                silhouetteother = 'FruitGame/Player2DirectorPartner.png'
        else:
            if player.role == "Director":
                silhouetteme = 'FruitGame/Player2DirectorMe.png'
                silhouetteother = 'FruitGame/Player1MatcherPartner.png'
            else:
                silhouetteme = 'FruitGame/Player2MatcherMe.png'
                silhouetteother = 'FruitGame/Player1DirectorPartner.png'

        return dict(image_patha='FruitGame/p{}.png'.format(group.imga),
                    image_pathb='FruitGame/p{}.png'.format(group.imgb),
                    image_pathc='FruitGame/p{}.png'.format(group.imgc),
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


# Page where personal information is collected (only round 1)
class PersonalInformation(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'genderother',  'nativelanguage', 'nonnativelanguage']

    @staticmethod
    def before_next_page(player, timeout_happened):
        # copies the given information into participant vars, that can be accessed in other apps
        player.participant.age = player.age
        player.participant.gender = player.gender
        player.participant.genderother = player.genderother
        player.participant.nativelanguage = player.nativelanguage
        player.participant.nonnativelanguage = player.nonnativelanguage

    @staticmethod
    def error_message(player, value):
        if value['gender'] == 'Other' and value['genderother'] == '':
            return 'You must specify "other" gender'

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


# Pages where introduction to the task is presented (only round 1)
class Introduction1(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Introduction2(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Introduction3(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Introduction4(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Introduction5(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


page_sequence = [PersonalInformation,
                 Introduction1, Introduction2, Introduction3, Introduction4, Introduction5,
                 StartWaitPage, MainPage, Results]
