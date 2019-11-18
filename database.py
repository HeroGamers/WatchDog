from peewee import SqliteDatabase, Model, CharField, DateTimeField, BooleanField, IntegrityError
import datetime
from Util import logger

db = SqliteDatabase('./WatchDog-Database.db')


# The tables #

class moderators(Model):
    UserID = CharField(unique=True)
    DiscordTag = CharField()
    IsOwner = BooleanField()

    class Meta:
        database = db


class bans(Model):
    UserID = CharField(unique=True)
    DiscordTag = CharField(null=True)
    IsActive = BooleanField()
    Reason = CharField(null=True)
    AvatarURL = CharField(null=True)
    Moderator = CharField(null=True)
    Guild = CharField(null=True)
    Time = DateTimeField()

    class Meta:
        database = db


class banappeals(Model):
    UserID = CharField(unique=True)
    Reason = CharField(null=True)
    AppealMessageID = CharField(null=True)
    Time = DateTimeField()

    class Meta:
        database = db

# The functions #

def newBan(userid, discordtag=None, moderator=None, guild=None, reason=None, avatarurl=None, date=None):
    if date == None:
        date = datetime.datetime.now()
    try:
        bans.create(UserID=userid, AvatarURL=avatarurl, DiscordTag=discordtag, IsActive=True, Moderator=moderator,
                    Reason=reason, Guild=guild, Time=date)
    except IntegrityError as e:
        logger.logDebug("DB Notice: User Already Banned! - " + str(e) + ". Trying to make sure user is banned then!",
                        "WARNING")
        query = bans.update(IsActive=True).where(UserId=userid)
        query.execute()


def invalidateBan(userid):
    query = bans.update(IsActive=False).where(bans.UserID.contains(str(userid)))
    query.execute()


def getBan(userid):
    query = bans.select().where(bans.UserID.contains(str(userid)))
    if query.exists():
        return query[0]
    return None


# Function to check whether an user is a global moderator
def isModerator(userid):
    query = moderators.select().where(moderators.UserID.contains(str(userid)))
    if query.exists():
        return True
    return False


def isBotOwner(userid):
    query = moderators.select().where(moderators.UserID.contains(str(userid)) and moderators.IsOwner is True)
    if query.exists():
        return True
    return False


def isBanned(userid):
    query = bans.select().where(bans.UserID.contains(str(userid)) & bans.IsActive == True)
    if query.exists():
        return True
    return False


def newBanAppeal(userid, reason=None):
    date = datetime.datetime.now()
    try:
        banappeals.create(UserID=userid, Reason=reason, Time=date)
    except IntegrityError as e:
        logger.logDebug("DB Notice: User Already Appealed for a ban! - " + str(e) + ". Trying to make sure reasoning is updated then!",
                        "WARNING")
        query = banappeals.update(Reason=reason).where(UserId=userid)
        query.execute()


def addBanAppealReason(userid, reason):
    query = banappeals.update(Reason=reason).where(UserId=userid)
    query.execute()


def isAppealing(userid):
    query = banappeals.select().where(banappeals.UserID.contains(str(userid)))
    if query.exists():
        return True
    return False


def hasNoAppealReason(userid):
    query = banappeals.select().where(banappeals.UserID.contains(str(userid)) & banappeals.Reason is None)
    if query.exists():
        return True
    return False


def getAppealReason(userid):
    query = banappeals.select().where(banappeals.UserID.contains(str(userid)))
    if query.exists():
        return query[0].Reason
    return None


def getAppealMessage(userid):
    query = banappeals.select().where(banappeals.UserID.contains(str(userid)))
    if query.exists():
        return query[0].AppealMessageID
    return None


def addAppealMessage(userid, messageid):
    query = banappeals.update(AppealMessageID=messageid).where(UserId=userid)
    query.execute()

def getAppealFromMessage(messageid):
    query = banappeals.select().where(banappeals.AppealMessageID.contains(str(messageid)))
    if query.exists():
        return query[0]
    return None


# Setup of tables #


def create_tables():
    with db:
        db.create_tables([moderators, bans, banappeals])


create_tables()
