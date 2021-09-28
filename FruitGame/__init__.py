from otree.api import *
import random
c = Currency

doc = """
Fruit selection game to study language and perspective takings development
"""


# OTREE CLASSES
class Constants(BaseConstants):
    name_in_url = 'FruitGame'
    players_per_group = 2
    num_rounds = 10
    director_role = 'Director'
    matcher_role = 'Matcher'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    tempcom = models.StringField(label='communication', initial='')
    imgselected = models.IntegerField(label='selected_fruit')
    imgselectedcorrect = models.BooleanField(label='selected_correct_fruit')

    imga = models.IntegerField()
    imgb = models.IntegerField()
    imgc = models.IntegerField()
    imgd = models.IntegerField()

    imgavalue = models.BooleanField()
    imgbvalue = models.BooleanField()
    imgcvalue = models.BooleanField()
    imgdvalue = models.BooleanField()

    condition3d = models.BooleanField()
    silhouette_corner = models.BooleanField()


class Player(BasePlayer):
    pass


class Communications(ExtraModel):
    group = models.Link(Group)
    r = models.IntegerField()
    coms = models.StringField()


# FUNCTIONS
def creating_session(subsession):
    # Flip the roles after x rounds
    x = 5
    matrix = subsession.get_group_matrix()
    if subsession.round_number > x:
        for row in matrix:
            row.reverse()
    subsession.set_group_matrix(matrix)

    for group in subsession.get_groups():
        # Select the placement of fruits
        imgorder = random.sample([1, 2, 3, 4], k=4)
        group.imga = imgorder[0]
        group.imgb = imgorder[1]
        group.imgc = imgorder[2]
        group.imgd = imgorder[3]

        # Select the value of the fruits
        imgvalue = random.sample([True, False, False, False], k=4)
        group.imgavalue = imgvalue[0]
        group.imgbvalue = imgvalue[1]
        group.imgcvalue = imgvalue[2]
        group.imgdvalue = imgvalue[3]
        group.condition3d = subsession.session.config['condition3d']
        group.silhouette_corner = subsession.session.config['silhouette_corner']


# PAGES
class MainPage(Page):
    # For finding the image path for each image placement
    @staticmethod
    def vars_for_template(player):
        group = player.group
        return dict(image_patha='FruitGame/{}.jpg'.format(group.imga),
                    image_pathb='FruitGame/{}.jpg'.format(group.imgb),
                    image_pathc='FruitGame/{}.jpg'.format(group.imgc),
                    image_pathd='FruitGame/{}.jpg'.format(group.imgd))

    # Returns player role for javascript functions
    @staticmethod
    def js_vars(player):
        return (player.role)

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
            elif '4' in data:
                group.imgselected = group.imgd
                group.imgselectedcorrect = group.imgdvalue
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
        else: # Add to the unsent message
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


page_sequence = [StartWaitPage, MainPage, Results]
