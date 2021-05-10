from otree.api import *

c = Currency

doc = """
Fruit selection game to study language and perspective takings development
"""


class Constants(BaseConstants):
    name_in_url = 'FruitGame'
    players_per_group = 2
    num_rounds = 10
    director_role = 'Director'
    matcher_role = 'Matcher'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    tempcom = models.StringField(initial='')


class Player(BasePlayer):
    pass


class Communications(ExtraModel):
    group = models.Link(Group)
    r = models.IntegerField()
    coms = models.StringField()


# GLOBAL VARIABLES
#global tempcom
#tempcom = ""


# FUNCTIONS
#def addtotemp(group, data):
#    global tempcom
#    tempcom =+ data
#    print(tempcom)


# PAGES
class MainPage(Page):

    @staticmethod
    def js_vars(player):
        return (player.role)

    @staticmethod
    def live_method(player, data):
        group = player.group
        send = []
        #Communications.create(group=group, r=player.round_number, coms="1", )
        #Communications.create(group=group, r=player.round_number, coms="2", )
        #Communications.create(group=group, r=player.round_number, coms="3", )
        #if '1' in data:
        #    print("First load")
        #    return {player.id_in_group: 'Look it worked!'}
        if 'send' in data:
            Communications.create(group=group, r=player.round_number, coms=group.tempcom)
            group.tempcom = ''
            y = Communications.filter(group=group, r=player.round_number)
            for x in y:
                send.append('Director: ' + x.coms)
            send.append('Message: ' + group.tempcom)
            return {0: send}
        elif 'undo' in data:
            group.tempcom = group.tempcom[:-1]
        else:
            group.tempcom = group.tempcom + data
        y = Communications.filter(group=group, r=player.round_number)
        for x in y:
            send.append('Director: ' + x.coms)
            # send = send + 'Director: ' + x.coms + '<br>'
        # send = send + 'Director: ' + group.tempcom
        send.append('Message: ' + group.tempcom)
        print(send)
        return {player.id_in_group: send}


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MainPage, Results]
