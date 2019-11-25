from peewee import SqliteDatabase, Model, CharField, DateTimeField, BooleanField, IntegrityError
import datetime
from Util import logger

db = SqliteDatabase('./WatchDog-Database.db')

snowflake_max_length = 20  # It is currently 18, but max size of uint64 is 20 chars
discordtag_max_length = 37  # Max length of usernames are 32 characters, added # and the discrim gives 37
guildname_max_length = 100  # For some weird reason guild names can be up to 100 chars... whatevs lol


# ------------------------------------------------ GLOBAL MODERATORS ------------------------------------------------- #

# The Global Moderators Table
class moderators(Model):
    UserID = CharField(unique=True, max_length=snowflake_max_length)
    DiscordTag = CharField(max_length=discordtag_max_length)
    IsOwner = BooleanField()

    class Meta:
        database = db


# Function to check whether an user is a global moderator
def isModerator(userid):
    query = moderators.select().where(moderators.UserID.contains(str(userid)))
    if query.exists():
        return True
    return False


# Is the user an owner of the bot (there can be multiple)
def isBotOwner(userid):
    query = moderators.select().where((moderators.UserID.contains(str(userid))) and (moderators.IsOwner == True))
    if query.exists():
        return True
    return False


# --------------------------------------------------- GLOBAL BANS ---------------------------------------------------- #


# The Global Bans Table
class bans(Model):
    UserID = CharField(unique=True, max_length=snowflake_max_length)
    DiscordTag = CharField(null=True, max_length=discordtag_max_length)
    IsActive = BooleanField()
    Reason = CharField(null=True)
    AvatarURL = CharField(null=True)
    Moderator = CharField(null=True, max_length=snowflake_max_length)
    Guild = CharField(null=True, max_length=snowflake_max_length)
    Time = DateTimeField()

    class Meta:
        database = db


# Adding new bans to the DB
def newBan(userid, discordtag=None, moderator=None, guild=None, reason=None, avatarurl=None, date=None):
    if date == None:
        date = datetime.datetime.now()
    try:
        bans.create(UserID=userid, AvatarURL=avatarurl, DiscordTag=discordtag, IsActive=True, Moderator=moderator,
                    Reason=reason, Guild=guild, Time=date)
    except IntegrityError:
        if reason is None:
            query = bans.update(IsActive=True).where(bans.UserID.contains(str(userid)))
        else:
            query = bans.update(IsActive=True, Reason=reason).where(bans.UserID.contains(str(userid)))
        query.execute()


# Basically for "unbanning", we want to keep the user in the DB though
def invalidateBan(userid):
    query = bans.update(IsActive=False).where(bans.UserID.contains(str(userid)))
    query.execute()


# Gets a ban from the DB
def getBan(userid):
    query = bans.select().where(bans.UserID.contains(str(userid)))
    if query.exists():
        return query[0]
    return None


# Is the user banned?
def isBanned(userid):
    query = bans.select().where((bans.UserID.contains(str(userid))) & (bans.IsActive == True))
    if query.exists():
        return True
    return False


# --------------------------------------------------- BAN APPEALS ---------------------------------------------------- #


# Table for the ban appeals
class banappeals(Model):
    UserID = CharField(unique=True, max_length=snowflake_max_length)
    Reason = CharField(null=True)
    AppealMessageID = CharField(null=True, max_length=snowflake_max_length)
    Accepted = BooleanField(null=True)
    DecidedBy = CharField(null=True, max_length=snowflake_max_length)
    Time = DateTimeField()

    class Meta:
        database = db


# Create a new ban appeal
def newBanAppeal(userid, reason=None):
    date = datetime.datetime.now()
    try:
        banappeals.create(UserID=userid, Reason=reason, Time=date)
    except IntegrityError as e:
        logger.logDebug("DB Notice: User Already Appealed for a ban! - " + str(
            e) + ". Trying to make sure reasoning is updated then!",
                        "WARNING")
        query = banappeals.update(Reason=reason, Accepted=None).where(banappeals.UserID.contains(str(userid)))
        query.execute()


# Add a reason to the ban appeal
def addBanAppealReason(userid, reason):
    query = banappeals.update(Reason=reason).where(banappeals.UserID.contains(str(userid)))
    query.execute()


# Is the user appealing?
def isAppealing(userid):
    query = banappeals.select().where(
        (banappeals.UserID.is_null(False) & banappeals.UserID.contains(str(userid))) & (
                (banappeals.Accepted.is_null(True)) |
                (banappeals.Accepted != True)
        )
    )
    if query.exists():
        return True
    return False


# Is there no ban appeal reason?
def hasNoAppealReason(userid):
    query = banappeals.select().where((banappeals.UserID.contains(str(userid))) & (banappeals.Reason == None))
    if query.exists():
        return True
    return False


# Get the ban appeal reason
def getAppealReason(userid):
    query = banappeals.select().where(banappeals.UserID.contains(str(userid)))
    if query.exists():
        return query[0].Reason
    return None


# Get the message ID for the appeal (the appeal message is in the appeal channel. We store it to be able to update
# it, and take action on it)
def getAppealMessage(userid):
    query = banappeals.select().where(banappeals.UserID.contains(str(userid)))
    if query.exists():
        return query[0].AppealMessageID
    return None


# Adds an ID for an appeal message to the DB
def addAppealMessage(userid, messageid):
    query = banappeals.update(AppealMessageID=messageid).where(banappeals.UserID.contains(str(userid)))
    query.execute()


# Gets the appeal entry in the DB from an appeal message id
def getAppealFromMessage(messageid):
    query = banappeals.select().where(banappeals.AppealMessageID.contains(str(messageid)))
    if query.exists():
        return query[0]
    return None


# Gets the appeal entry in the DB from userid
def getAppeal(userid):
    query = banappeals.select().where(banappeals.UserID.contains(str(userid)))
    if query.exists():
        return query[0]
    return None


# Appprove ban appeal
def updateBanAppealStatus(userid, boolean, moderator):
    query = banappeals.update(Accepted=boolean, DecidedBy=moderator).where(banappeals.UserID.contains(str(userid)))
    query.execute()


# ------------------------------------------------------ GUILDS ------------------------------------------------------ #


# Table for the servers where instant ban-sync is enabled
class guilds(Model):
    GuildID = CharField(unique=True, max_length=snowflake_max_length)
    GuildName = CharField(null=True, max_length=guildname_max_length)
    OwnerID = CharField(null=True, max_length=snowflake_max_length)
    OwnerTag = CharField(null=True, max_length=discordtag_max_length)
    HasActiveSync = BooleanField()
    Time = DateTimeField()

    class Meta:
        database = db


# Add a guild
def addBanSyncGuild(guildid, guildname=None, ownerid=None, ownertag=None):
    date = datetime.datetime.now()
    try:
        guilds.create(GuildID=guildid, GuildName=guildname, OwnerID=ownerid, OwnerTag=ownertag, HasActiveSync=True,
                      Time=date)
    except IntegrityError as e:
        logger.logDebug("DB Notice: Guild Already Added To Sync List! - " + str(
            e) + ".", "WARNING")


# Toggle active sync from a ban-sync guild
def toggleActiveSync(guildid):
    if isBanSyncGuild(guildid):
        query = guilds.update(HasActiveSync=False).where(guilds.GuildID.contains(str(guildid)))
        query.execute()
    else:
        query = guilds.update(HasActiveSync=True).where(guilds.GuildID.contains(str(guildid)))
        query.execute()


# Get list of guilds to ban-sync to
def getBanSyncGuilds():
    query = guilds.select().where(guilds.HasActiveSync == True)
    if query.exists():
        return query
    return []


# Is the guild on the list of guilds to ban-sync to?
def isBanSyncGuild(guildid):
    query = guilds.select().where((guilds.GuildID.contains(str(guildid))) & (guilds.HasActiveSync == True))
    if query.exists():
        return True
    return False


# Is the guild in the db?
def isGuildInDB(guildid):
    query = guilds.select().where(guilds.GuildID.contains(str(guildid)))
    if query.exists():
        return True
    return False


# -------------------------------------------------- SETUP OF TABLES ------------------------------------------------- #


def create_tables():
    with db:
        db.create_tables([moderators, bans, banappeals, guilds])


create_tables()
