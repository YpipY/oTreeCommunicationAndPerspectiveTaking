from otree.api import *
import random
import itertools

c = Currency

doc = """
Fruit selection game to study language and perspective takings development. This is the introduction, training and
personal information gathering part. Personal information is only collected here, use the unique participant code to
tie this to the main game data if needed. (Done so that the datafile does not get too large)
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
    matcherpos = models.IntegerField()
    gridcolorpos = models.IntegerField()

    # saves image
    imga = models.IntegerField()
    imgb = models.IntegerField()
    imgc = models.IntegerField()
    # imgd = models.IntegerField()

    # saves image value (correct, incorrect)
    imgavalue = models.BooleanField()
    imgbvalue = models.BooleanField()
    imgcvalue = models.BooleanField()
    # imgdvalue = models.BooleanField()

    # conditions


class Player(BasePlayer):
    # personal information
    age = models.IntegerField(label="Your age:", min=0)
    gender = models.StringField(label="Your gender:", choices=["Female", "Male", "Other"])
    nativelanguage = models.StringField(label="Your native language(s). Capitalized, written in english and separated "
                                              "by a space. If unsure ask an experiment:")
    nonnativelanguage = models.StringField(label="Your fluent non-native language(s). Capitalized, written in "
                                                 "english and separated by a space. If unsure ask an experiment:",
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
    global permutations
    global switch

    # make all the switching of object, perspective and grid color permutations
    if subsession.round_number == 1:
        switch = [[1] * 20 + [2] * 24 + [3] * 24 + [4] * 28,
                  [1] * 28 + [2] * 20 + [3] * 24 + [4] * 24,
                  [1] * 24 + [2] * 28 + [3] * 24 + [4] * 20]
        switch = list(itertools.permutations(switch, 3))
        random.shuffle(switch)

    # give each player a constant number, 1 or 2 (since group in id_in_group dictates player role)
    n = 1
    for player in subsession.get_players():
        player.number = n
        n += 1
        if n == 3:
            n = 1

    # Flip the roles after x rounds
    # x = Constants.num_rounds/2
    # matrix = subsession.get_group_matrix()
    # if subsession.round_number > x:
    #    for row in matrix:
    #        row.reverse()
    # subsession.set_group_matrix(matrix)

    # flip the roles every round
    matrix = subsession.get_group_matrix()
    if subsession.round_number % 2 == 0:
        for row in matrix:
            row.reverse()
    subsession.set_group_matrix(matrix)

    # setting values for all the groups
    for group in subsession.get_groups():
        # Select the placement of objects ("true" random)
        # imgorder = random.sample([1, 2, 3, 4], k=4)
        # group.imga = imgorder[0]
        # group.imgb = imgorder[1]
        # group.imgc = imgorder[2]
        # group.imgd = imgorder[3]

        group.objects = switch[(group.id_in_subsession - 1) % 5][0][subsession.round_number - 1]
        group.matcherpos = switch[(group.id_in_subsession - 1) % 5][1][subsession.round_number - 1]
        group.gridcolorpos = switch[(group.id_in_subsession - 1) % 5][2][subsession.round_number - 1]

        # make the all permutations of the object ordering (pseudorandom)
        if subsession.round_number == 1:
            permutations = list(itertools.permutations([1, 2, 3, 4], 3))
            random.shuffle(permutations)

        # Select the images form the current image block
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

        # Select the value of the objects
        imgvalue = random.sample([True, False, False], k=3)
        group.imgavalue = imgvalue[0]
        group.imgbvalue = imgvalue[1]
        group.imgcvalue = imgvalue[2]

        # group.imgdvalue = imgvalue[3]
        # potion relative to director. Clockwise starting with 1 = top
        # group.matcherpos = random.choice([1, 2, 3, 4])

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
                    silhouetteother=silhouetteother)
        # image_pathd='FruitGame/{}.jpg'.format(group.imgd))

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
            # elif '4' in data:
            #    group.imgselected = group.imgd
            #    group.imgselectedcorrect = group.imgdvalue
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
    form_fields = ['age', 'gender', 'nativelanguage', 'nonnativelanguage']

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


# Page where introduction to the task is presented (only round 1)
class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        # copies the given information on the first round, into the other rows (seems a little hack)
        if player.round_number != 1:
            player.age = player.in_round(player.round_number - 1).age
            player.gender = player.in_round(player.round_number - 1).gender
            player.nativelanguage = player.in_round(player.round_number - 1).nativelanguage
            player.nonnativelanguage = player.in_round(player.round_number - 1).nonnativelanguage
        return player.round_number == 1


page_sequence = [PersonalInformation, Introduction,
                 StartWaitPage, MainPage, Results]
