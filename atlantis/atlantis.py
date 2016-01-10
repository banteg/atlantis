import json
from asyncio import sleep
from collections import defaultdict

from aiotg import TgBot

from secrets import token, botan
from atlantis.translations import en, ru


bot = TgBot(token, botan_token=botan)
users = defaultdict(dict)


@bot.command(r'/start')
async def start(chat, match):
    users[chat.id] = Atlantis(chat)
    print('{} joined or started anew, total {}'.format(chat.sender, len(users)))
    await chat.send_text('Choose language / Выберите язык:\n\n/en English\n/ru Русский')
    await users[chat.id].flush()


@bot.command(r'/(en|ru)')
async def set_locale(chat, match):
    if not users[chat.id]:
        return (await start(chat, match))

    locale = match.group(1)
    print('{} changed locale to {}'.format(chat.sender, locale))
    if locale == 'en':
        users[chat.id].locale = en
    elif locale == 'ru':
        users[chat.id].locale = ru

    users[chat.id].goto('Atl_Start')
    await users[chat.id].flush()


@bot.command(r'/(fast|slow)')
async def set_speed(chat, match):
    speed = match.group(1)
    print('{} changed speed to {}'.format(chat.sender, speed))
    if speed == 'fast':
        users[chat.id].fast = True
    else:
        users[chat.id].fast = False


@bot.command(r'.*')
async def choose(chat, match):
    if not users[chat.id]:
        return (await start(chat, match))

    choice = match.group(0)
    print('{} chose {}'.format(chat.sender, choice))
    users[chat.id].choose(choice)
    await users[chat.id].flush()


class Atlantis:

    'Bot-bound Atlantis story.'

    def __init__(self, bot):
        self.state = {}
        self.options = []
        self.choices = []
        self.messages = []
        self.bot = bot
        self.locale = en
        self.fast = False

    def say(self, text):
        'Enqueue a message.'
        lines = [x for x in self.locale[text].split('\n\n') if x.strip()]
        self.messages.extend(lines)

    async def typing(self, message):
        'Delay based on message length.'
        delay = min(max(1.5, len(message) / 50), 4.0)
        if not self.fast:
            await self.bot.send_chat_action(action='typing')
            await sleep(delay)

    async def flush(self):
        'Send all pending messages and a reply keyboard.'
        queue = list(self.messages)
        self.messages = []
        keyboard = {
            'keyboard': [[choice] for choice in self.choices],
            'resize_keyboard': True,
        }

        while len(queue) > 1:
            message = queue.pop(0)
            await self.typing(message)
            await self.bot.send_text(message)

        if queue:
            message = queue.pop(0)
            await self.typing(message)
            await self.bot.send_text(message, reply_markup=json.dumps(keyboard))

    def choose(self, choice):
        'Advance the story based on a choice.'
        try:
            option = self.options[self.choices.index(choice)]
        except ValueError:
            print('invalid choice "{}" by {}'.format(choice, self.bot.sender))
        else:
            for s in option.get('set', ()):
                self.state[s] = True

            self.goto(option['next'])

    def goto(self, jump):
        'Jump to specific part of the story.'

        if jump == 'Atl_Start':
            self.say('Ln0016.0.text.FAREWELLATLANTISAStoryOf')
            self.state = {}
            self.options = [
                {'next': 'Atl_Begin', 'text': 'Ln0037.0.option.Begin', 'short': 'Ln0037.0.short.Begin'},
                {'next': 'Atl_Credits', 'text': 'TermDlg.Common.Credits', 'short': 'TermDlg.Common.Credits2'},
                {'next': 'MessageBoardInterface_On', 'text': 'Ln0039.0.option.IOpenMyEyes', 'short': 'TermDlg.Common.ExitBrackets'},
            ]

        if jump == 'Atl_Credits':
            self.say('Ln0044.0.text.WrittenByLilithDedicatedTo')
            self.options = [
                {'next': 'Atl_Begin', 'text': 'Ln0037.0.option.Begin', 'short': 'Ln0037.0.short.Begin'},
                {'next': 'MessageBoardInterface_On', 'text': 'Ln0039.0.option.IOpenMyEyes', 'short': 'Ln0053.0.short.Quit'},
            ]

        if jump == 'Atl_Begin':
            self.say('Ln0058.0.text.ChooseYourCharacterClass')
            self.options = [
                {'set': ['ClassPoet'], 'next': 'Atl_Poet', 'text': 'Ln0063.0.option.Poet'},
                {'set': ['ClassPhysician'], 'next': 'Atl_Physician', 'text': 'Ln0064.0.option.Physician'},
                {'set': ['ClassFarmer'], 'next': 'Atl_Farmer', 'text': 'Ln0065.0.option.Farmer'},
                {'set': ['ClassScientist'], 'next': 'Atl_Scientist', 'text': 'Ln0066.0.option.Scientist'},
                {'set': ['ClassMagician'], 'next': 'Atl_Magician', 'text': 'Ln0067.0.option.Magician'},
            ]

        # POET

        if jump == 'Atl_Poet':
            self.say('Ln0074.0.text.YouAreSittingUponA')
            self.options = [
                {'next': 'Atl_PoetWork', 'text': 'Ln0079.0.option.WorkOnPoetry'},
                {'next': 'Atl_PoetObserve', 'text': 'Ln0080.0.option.ObserveTheChildren'},
                {'next': 'Atl_PoetPlay', 'text': 'Ln0081.0.option.PlayWithTheChildren'},
            ]

        if jump == 'Atl_PoetWork':
            self.say('Ln0086.0.text.YouCloseYourEyesFocusing')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0093.0.option.TalkToTheMessenger'},
            ]

        if jump == 'Atl_PoetObserve':
            self.say('Ln0098.0.text.YouObserveThePlayingChildren')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0093.0.option.TalkToTheMessenger'},
            ]

        if jump == 'Atl_PoetPlay':
            self.say('Ln0112.0.text.YouGoDownToThe')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0093.0.option.TalkToTheMessenger'},
            ]

        # PHYSICIAN

        if jump == 'Atl_Physician':
            self.say('Ln0128.0.text.YoureInTheGreatHall')
            self.options = [
                {'next': 'Atl_Approach', 'text': 'Ln0135.0.option.Approach'},
            ]

        if jump == 'Atl_Approach':
            self.say('Ln0140.0.text.AsYouApproachYouSee')
            self.options = [
                {'next': 'Atl_Sit', 'text': 'Ln0147.0.option.SitWithTheMan'},
                {'next': 'Atl_Offer', 'text': 'Ln0148.0.option.OfferHimSleepSnakePoison'},
            ]

        if jump == 'Atl_Sit':
            self.say('Ln0153.0.text.YouSitForTheMan')
            self.options = [
                {'next': 'Atl_Pray', 'text': 'Ln0162.0.option.SayAPrayer'},
                {'next': 'Atl_Pray', 'text': 'Ln0163.0.option.CloseHisEyes'},
            ]

        if jump == 'Atl_Pray':
            self.say('Ln0168.0.text.YouGetUpAndApproach')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0093.0.option.TalkToTheMessenger'},
            ]

        if jump == 'Atl_Offer':
            self.say('Ln0180.0.text.TheManConsidersThisFor')
            self.options = [
                {'next': 'Atl_Pray', 'text': 'Ln0162.0.option.SayAPrayer'},
                {'next': 'Atl_Pray', 'text': 'Ln0163.0.option.CloseHisEyes'},
            ]

        # FARMER

        if jump == 'Atl_Farmer':
            self.say('Ln0197.0.text.YoureOutsideOnYourFarm')
            self.options = [
                {'next': 'Atl_Dig', 'text': 'Ln0202.0.option.DigItUp'},
                {'next': 'Atl_LeaveIt', 'text': 'Ln0203.0.option.LeaveItAlone'},
            ]

        if jump == 'Atl_Dig':
            self.say('Ln0208.0.text.ItsNotJustAStone')
            self.options = [
                {'next': 'Atl_KeepDigging', 'text': 'Ln0213.0.option.KeepDigging'},
            ]

        if jump == 'Atl_KeepDigging':
            self.say('Ln0218.0.text.NoYouBeginToRealize')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0093.0.option.TalkToTheMessenger'},
            ]

        if jump == 'Atl_LeaveIt':
            self.say('Ln0234.0.text.YouLeaveItButIt')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0093.0.option.TalkToTheMessenger'},
            ]

        # SCIENTIST

        if jump == 'Atl_Scientist':
            self.say('Ln0252.0.text.YoureInTheTempleOf')
            self.options = [
                {'next': 'Atl_Experiment', 'text': 'Ln0257.0.option.StartTheExperiment'},
            ]

        if jump == 'Atl_Experiment':
            self.say('Ln0262.0.text.TheGearsOfTheMachine')
            self.options = [
                {'next': 'Atl_ApproachMachine', 'text': 'Ln0269.0.option.ApproachTheMachine'},
                {'next': 'Atl_ShutDown', 'text': 'Ln0270.0.option.ShutItDown'},
                {'next': 'Atl_KeepRunning', 'text': 'Ln0271.0.option.KeepItRunning'},
            ]

        if jump == 'Atl_ApproachMachine':
            self.say('Ln0276.0.text.YouStepCloserToThe')
            self.options = [
                {'next': 'Atl_Investigate', 'text': 'Ln0283.0.option.Investigate'},
            ]

        if jump == 'Atl_Investigate':
            self.say('Ln0288.0.text.ItsACityYouCan')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0297.0.option.TalkToTheMessenger'},
            ]

        if jump == 'Atl_ShutDown':
            self.say('Ln0302.0.text.NoThatsWrongTheLight')
            self.options = [
                {'next': 'Atl_ApproachMachine', 'text': 'Ln0307.0.option.ApproachTheLight'},
            ]

        if jump == 'Atl_KeepRunning':
            self.say('Ln0312.0.text.TheLightGrowsStrongerAnd')
            self.options = [
                {'next': 'Atl_ApproachMachine', 'text': 'Ln0307.0.option.ApproachTheLight'},
            ]

        # MAGICIAN

        if jump == 'Atl_Magician':
            self.say('Ln0323.0.text.YouAreInYourTower')
            self.options = [
                {'next': 'Atl_SeekAnswers', 'text': 'Ln0330.0.option.SeekAnswers'},
                {'next': 'Atl_LetItGo', 'text': 'Ln0331.0.option.LetItGo'},
            ]

        if jump == 'Atl_SeekAnswers':
            self.say('Ln0336.0.text.YouGoDownTheStairs')
            self.options = [
                {'next': 'Atl_TryTheSpell', 'text': 'Ln0341.0.option.TryTheSpell'},
                {'next': 'Atl_LetItGo', 'text': 'Ln0331.0.option.LetItGo'},
            ]

        if jump == 'Atl_TryTheSpell':
            self.say('Ln0347.0.text.YouReturnToTheTop')
            self.options = [
                {'next': 'Atl_LookCloser', 'text': 'Ln0352.0.option.LookCloser'},
            ]

        if jump == 'Atl_LookCloser':
            self.say('Ln0357.0.text.ItsACityACity')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0297.0.option.TalkToTheMessenger'},
            ]

        if jump == 'Atl_LetItGo':
            self.say('Ln0371.0.text.YouDecideToLetIt')
            self.options = [
                {'next': 'Atl_Messenger', 'text': 'Ln0297.0.option.TalkToTheMessenger'},
            ]

        # MESSENGER

        if jump == 'Atl_Messenger':
            self.say('Ln0387.0.text.TheMessengerIsIndeedA')
            self.options = [
                {'set': ['AtlantisDelay1'], 'next': 'Atl_AskAbout', 'text': 'Ln0396.0.option.AskWhatThisIsAbout'},
                {'next': 'Atl_City', 'text': 'Ln0397.0.option.FollowTheMessenger'},
            ]

        if jump == 'Atl_AskAbout':
            self.say('Ln0402.0.text.IAmSorryTheMessenger')
            self.options = [
                {'next': 'Atl_City', 'text': 'Ln0397.0.option.FollowTheMessenger'},
            ]

        if jump == 'Atl_City':
            self.say('Ln0412.0.text.TheMessengerTakesYouTo')
            self.options = [
                {'next': 'Atl_Throne', 'text': 'Ln0419.0.option.EnterTheThroneRoom'},
            ]

        # MEETING THE KING

        if jump == 'Atl_Throne':
            self.say('Ln0426.0.text.YouEnterTheThroneRoom')
            self.options = [
                {'set': ['AtlantisDelay2'], 'next': 'Atl_Mosaic', 'text': 'Ln0431.0.option.ExamineTheMosaic'},
                {'next': 'Atl_LookKing', 'text': 'Ln0432.0.option.LookForTheKing'},
            ]

        if jump == 'Atl_LookKing':
            self.say('Ln0437.0.text.InAllThisSplendourThe')
            self.options = [
                {'next': 'Atl_Bow', 'text': 'Ln0444.0.option.BowBeforeTheKing'},
            ]

        if jump == 'Atl_Mosaic':
            self.say('Ln0449.0.text.TheSheerAmountOfWork')
            self.options = [
                {'next': 'Atl_Bow', 'text': 'Ln0444.0.option.BowBeforeTheKing'},
            ]

        if jump == 'Atl_Bow':
            if 'ClassFarmer' in self.state:
                self.say('Ln0461.0.text.NoDoNotBowMy')

            if 'ClassMagician' in self.state:
                self.say('Ln0473.0.text.NoDoNotBowMy')

            if 'ClassPhysician' in self.state:
                self.say('Ln0485.0.text.NoDoNotBowMy')

            if 'ClassPoet' in self.state:
                self.say('Ln0497.0.text.NoDoNotBowMy')

            if 'ClassScientist' in self.state:
                self.say('Ln0509.0.text.NoDoNotBowMy')

            self.options = [
                {'next': 'Atl_Scroll', 'text': 'Ln0468.0.option.ReadScroll'},
            ]

        if jump == 'Atl_Scroll':
            if 'ClassFarmer' in self.state:
                self.say('Ln0521.0.text.YouReadTheScrollWith')

            if 'ClassMagician' in self.state:
                self.say('Ln0533.0.text.YouReadTheScrollWith')

            if 'ClassPhysician' in self.state:
                self.say('Ln0545.0.text.YouReadTheScrollWith')

            if 'ClassPoet' in self.state:
                self.say('Ln0557.0.text.YouReadTheScrollWith')

            if 'ClassScientist' in self.state:
                self.say('Ln0569.0.text.YouReadTheScrollWith')

            self.options = [
                {'next': 'Atl_Confirm', 'text': 'Ln0528.0.option.ConfirmTheTruth'},
            ]

        if jump == 'Atl_Confirm':
            self.say('Ln0581.0.text.TheKingSighsIWas')
            self.options = [
                {'next': 'Atl_AskDone', 'text': 'Ln0588.0.option.AskWhatCanBeDone'},
                {'next': 'Atl_Despair', 'text': 'Ln0589.0.option.SayThereIsNoHope'},
                {'next': 'Atl_Curse', 'text': 'Ln0590.0.option.CurseTheGods'},
            ]

        if jump == 'Atl_Despair':
            self.say('Ln0595.0.text.MyFriendPoseidonasSaysDo')
            self.options = [
                {'next': 'Atl_AskDone', 'text': 'Ln0588.0.option.AskWhatCanBeDone'},
            ]

        if jump == 'Atl_Curse':
            self.say('Ln0605.0.text.MyFriendPoseidonasSaysYou')
            self.options = [
                {'next': 'Atl_AskDone', 'text': 'Ln0588.0.option.AskWhatCanBeDone'},
            ]

        if jump == 'Atl_AskDone':
            self.say('Ln0615.0.text.TellMeWhatIsThe')
            self.options = [
                {'set': ['AtlantisArt'], 'next': 'Atl_Art', 'text': 'Ln0620.0.option.Art', 'short': 'Ln0620.0.short.ChooseArt'},
                {'set': ['AtlantisPeople'], 'next': 'Atl_People', 'text': 'Ln0621.0.option.ThePeople', 'short': 'Ln0621.0.short.ChooseThePeople'},
                {'set': ['AtlantisKnowledge'], 'next': 'Atl_Knowledge', 'text': 'Ln0622.0.option.Knowledge', 'short': 'Ln0622.0.short.ChooseKnowledge'},
            ]

        if jump == 'Atl_Art':
            self.say('Ln0627.0.text.TheHeartOfAtlantisIs')
            self.options = [
                {'next': 'Atl_How', 'text': 'Ln0636.0.option.How'},
            ]

        if jump == 'Atl_People':
            self.say('Ln0641.0.text.TheHeartOfAtlantisIs')
            self.options = [
                {'next': 'Atl_How', 'text': 'Ln0636.0.option.How'},
            ]

        if jump == 'Atl_Knowledge':
            self.say('Ln0653.0.text.TheHeartOfAtlantisIs')
            self.options = [
                {'next': 'Atl_How', 'text': 'Ln0636.0.option.How'},
            ]

        if jump == 'Atl_How':
            self.say('Ln0667.0.text.ThereIsNotMuchTime')
            self.options = [
                {'set': ['AtlantisDelay3'], 'next': 'Atl_WhyMe', 'text': 'Ln0676.0.option.WhyMe'},
                {'next': 'Atl_YesMyLord', 'text': 'Ln0677.0.option.YesMyLord'},
            ]

        if jump == 'Atl_WhyMe':
            self.say('Ln0682.0.text.WhyNotYouWhyA')
            self.options = [
                {'next': 'Atl_YesMyLord', 'text': 'Ln0677.0.option.YesMyLord'},
            ]

        if jump == 'Atl_YesMyLord':
            self.say('Ln0692.0.text.PoseidonasLaughsIAmNot')
            self.options = [
                {'next': 'Atl_GoHarbour', 'text': 'Ln0699.0.option.HeadForTheHarbour'},
            ]

        # GOING TO THE HARBOUR

        if jump == 'Atl_GoHarbour':
            self.say('Ln0706.0.text.EscortedByTheSameMessenger')
            self.options = [
                {'next': 'Atl_GoChariot', 'text': 'Ln0711.0.option.TakeTheChariotToGet'},
                {'set': ['AtlantisDelay4'], 'next': 'Atl_GoWalk', 'text': 'Ln0712.0.option.WalkToSeeTheCity'},
            ]

        if jump == 'Atl_GoWalk':
            self.say('Ln0717.0.text.YouDecideToTakeThe')
            self.options = [
                {'set': ['AtlantisMessengerYes'], 'next': 'Atl_Hurry', 'text': 'Ln0726.0.option.Hurry'},
            ]

        if jump == 'Atl_GoChariot':
            self.say('Ln0731.0.text.YouGetOnTheChariot')
            self.options = [
                {'next': 'Atl_GetUp', 'text': 'Ln0738.0.option.GetUp'},
                {'next': 'Atl_Examine', 'text': 'Ln0739.0.option.ExamineTheMessenger'},
            ]

        if jump == 'Atl_GetUp':
            self.say('Ln0744.0.text.YouGetUpTheMessenger')
            self.options = [
                {'next': 'Atl_NoTime', 'text': 'Ln0749.0.option.KeepGoing'},
                {'next': 'Atl_Examine', 'text': 'Ln0739.0.option.ExamineTheMessenger'},
            ]

        if jump == 'Atl_Examine' and 'ClassPhysician' in self.state:
            self.say('Ln0755.0.text.HeHasTwistedHisLeg')
            self.options = [
                {'set': ['AtlantisMessengerYes'], 'next': 'Atl_Hurry', 'text': 'Ln0726.0.option.Hurry'},
            ]

        if jump == 'Atl_Examine' and 'ClassPhysician' not in self.state:
            self.say('Ln0765.0.text.TheMessengerSeemsBadlyInjured')
            self.options = [
                {'next': 'Atl_CallHelp', 'text': 'Ln0770.0.option.CallForHelp'},
                {'next': 'Atl_NoTime', 'text': 'Ln0771.0.option.LeaveHimBehind'},
            ]

        if jump == 'Atl_CallHelp':
            self.say('Ln0776.0.text.YouCallForHelpAnd')
            self.options = [
                {'set': ['AtlantisMessengerNo', 'AtlantisDelay4'], 'next': 'Atl_Hurry', 'text': 'Ln0726.0.option.Hurry'},
            ]

        if jump == 'Atl_NoTime':
            self.say('Ln0789.0.text.YouJustDontHaveThe')
            self.options = [
                {'set': ['AtlantisMessengerNo'], 'next': 'Atl_Hurry', 'text': 'Ln0726.0.option.Hurry'},
            ]

        # IN THE HARBOUR

        if jump == 'Atl_Hurry':
            if 'AtlantisMessengerYes' in self.state:
                self.say('Ln0803.0.text.HurryingAsMuchAsPossible')

            if 'AtlantisMessengerNo' in self.state:
                self.say('Ln0814.0.text.HurryingAsMuchAsPossible')

            self.options = [
                {'next': 'Atl_Speech', 'text': 'Ln0808.0.option.SpeakToTheCaptains'},
                {'next': 'Atl_LoadShips', 'text': 'Ln0809.0.option.LoadTheShips'},
            ]

        if jump == 'Atl_Speech':
            self.say('Ln0825.0.text.YouSpeakBrieflyButWith')
            self.options = [
                {'next': 'Atl_LoadShips', 'text': 'Ln0809.0.option.LoadTheShips'},
            ]

        if jump == 'Atl_LoadShips' and 'AtlantisArt' in self.state:
            self.say('Ln0835.0.text.YouGiveTheOrderTo')
            self.options = [
                {'next': 'Atl_SaveSculptures', 'text': 'Ln0842.0.option.MostlySculptures'},
                {'next': 'Atl_SaveBooks', 'text': 'Ln0843.0.option.MostlyBooks'},
                {'next': 'Atl_SavePaintings', 'text': 'Ln0844.0.option.MostlyPaintings'},
                {'next': 'Atl_SaveBalance', 'text': 'Ln0845.0.option.AnEvenBalance'},
            ]

        if jump == 'Atl_SaveSculptures':
            self.say('Ln0850.0.text.AhTheSculpturalMasterpiecesOf')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_SaveBooks':
            self.say('Ln0862.0.text.FromTheAncientMythsOf')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_SavePaintings':
            self.say('Ln0874.0.text.AtlanteanPaintingBeganOnCave')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_SaveBalance':
            self.say('Ln0886.0.text.YouTryToSaveA')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_LoadShips' and 'AtlantisPeople' in self.state:
            self.say('Ln0898.0.text.YouWantToSaveThe')
            self.options = [
                {'next': 'Atl_SaveFamilies', 'text': 'Ln0905.0.option.TheSailorsFamilies'},
                {'next': 'Atl_SaveCelebs', 'text': 'Ln0906.0.option.FamousIndividuals'},
                {'next': 'Atl_SaveRandom', 'text': 'Ln0907.0.option.WhoeverIsClosest'},
            ]

        if jump == 'Atl_SaveFamilies':
            self.say('Ln0912.0.text.YouTellTheSailorsTo')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_SaveCelebs':
            self.say('Ln0924.0.text.YouSendOutSailorsTo')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_SaveRandom':
            self.say('Ln0936.0.text.YouHaveToBePractical')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_LoadShips' and 'AtlantisKnowledge' in self.state:
            self.say('Ln0948.0.text.ThePeopleOfAtlantisAre')
            self.options = [
                {'next': 'Atl_SaveFamiliesTwo', 'text': 'Ln0957.0.option.OfCourse'},
                {'next': 'Atl_InsaneCruelBastard', 'text': 'TermDlg.Common.No2'},
            ]

        if jump == 'Atl_SaveFamiliesTwo':
            self.say('Ln0963.0.text.TheSailorsAreOverjoyedAnd')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_InsaneCruelBastard':
            self.say('Ln0977.0.text.YouSpeakOfTheImportance')
            self.options = [
                {'next': 'Atl_Sail', 'text': 'Ln0857.0.option.GetReadyToSetSail'},
            ]

        if jump == 'Atl_Sail' and 'AtlantisMessengerYes' in self.state:
            self.say('Ln0991.0.text.TheShipsAreReadyThe')
            self.options = [
                {'next': 'Atl_StayBehind', 'text': 'Ln1000.0.option.StayBehindSoHeCan'},
                {'next': 'Atl_GoodbyeMessenger', 'text': 'Ln1001.0.option.SayGoodbye'},
            ]

        if jump == 'Atl_GoodbyeMessenger':
            self.say('Ln1006.0.text.HeavyHeartedYouSayGoodbye')
            self.options = [
                {'next': 'Atl_SetSail', 'text': 'Ln1015.0.option.SetSail'},
            ]

        if jump == 'Atl_StayBehind':
            self.say('Ln1020.0.text.ItIsNotEasyTo')
            self.options = [
                {'next': 'Atl_Watch', 'text': 'Ln1027.0.option.WatchingTheShipsTakeOff'},
                {'next': 'Atl_Tavern', 'text': 'Ln1028.0.option.InATavern'},
                {'next': 'Atl_Palace', 'text': 'Ln1029.0.option.InThePalace'},
            ]

        if jump == 'Atl_Watch':
            self.say('Ln1034.0.text.YouSitInTheHarbour')
            self.options = [
                {'next': 'MessageBoardInterface_On', 'text': 'Ln0039.0.option.IOpenMyEyes', 'short': 'Ln1047.0.short.End'},
            ]

        if jump == 'Atl_Tavern':
            self.say('Ln1052.0.text.YouSitDownInA')
            self.options = [
                {'next': 'MessageBoardInterface_On', 'text': 'Ln0039.0.option.IOpenMyEyes', 'short': 'Ln1047.0.short.End'},
            ]

        if jump == 'Atl_Palace':
            self.say('Ln1072.0.text.PoseidonasGreetsYouLikeAn')
            self.options = [
                {'next': 'MessageBoardInterface_On', 'text': 'Ln0039.0.option.IOpenMyEyes', 'short': 'Ln1047.0.short.End'},
            ]

        if jump == 'Atl_Sail' and 'AtlantisMessengerNo' in self.state:
            self.say('Ln1088.0.text.TheShipsAreReadyOne')
            self.options = [
                {'next': 'Atl_SetSail', 'text': 'Ln1015.0.option.SetSail'},
            ]

        if jump == 'Atl_SetSail':
            self.say('Ln1100.0.text.TheTimeHasComeYou')
            self.options = [
                {'next': 'Atl_LookLand', 'text': 'Ln1107.0.option.SailOnward'},
            ]

        if jump == 'Atl_LookLand':
            self.say('Ln1112.0.text.DaysPassTerribleWavesShake')
            self.options = [
                {'next': 'Atl_Land', 'text': 'Ln1119.0.option.FindANewHome'},
            ]

        if jump == 'Atl_Land':
            if 'ClassFarmer' in self.state:
                self.say('Ln1124.0.text.OneDayYouComeUpon')

            if 'ClassMagician' in self.state:
                self.say('Ln1142.0.text.OneDayYouComeUpon')

            if 'ClassPhysician' in self.state:
                self.say('Ln1160.0.text.OneDayYouComeUpon')

            if 'ClassPoet' in self.state:
                self.say('Ln1178.0.text.OneDayYouComeUpon')

            if 'ClassScientist' in self.state:
                self.say('Ln1196.0.text.OneDayYouComeUpon')

            self.options = [
                {'next': 'MessageBoardInterface_On', 'text': 'Ln0039.0.option.IOpenMyEyes', 'short': 'Ln1047.0.short.End'},
            ]

        if jump == 'MessageBoardInterface_On':
            self.goto('Atl_Start')
            return

        self.choices = [self.locale[o.get('short', o['text'])] for o in self.options]


if __name__ == '__main__':
    bot.run()
