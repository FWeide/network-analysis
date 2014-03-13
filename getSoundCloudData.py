'''
Created on Feb 25, 2014

@author: annajordanous
'''

import random
import soundcloud  # @UnresolvedImport

import clientSettings as client
client = soundcloud.Client(client_id=client.get_client_id())

import sqlite3
import time


# The following global variables represent information about the SoundCloud users in our
# sample set. We only collect data on users in our sample set, discarding other data
# For each set of SoundCloud *objects* (excluding sets of tuples), 
# we maintain a list of ids of members in that set.
# This is to avoid duplicates appearing in the set, due to two identical SoundCloud
# objects not being recognised as being the same object.
  
# users = set of SoundCloud user objects
users = set()
user_ids = list()
# x_follows_y = set of tuples (x, y) representing follow relationships in SoundCloud where x follows y (and x and y are both in "users")
x_follows_y = set()
# tracks = set of SoundCloud track objects where tracks belong to users in "users"
tracks = set()
track_ids = list()
# TODO add the four items below as DB tables
# groups - set of tuples representing SoundCloud groups that a user has joined
groups = set()
# favourites (NB English spelling here, US spelling on SoundCloud) 
#    - set of tuples representing tracks that a user has 'liked'
favourites = set()
# comments - set of SoundCloud comments for a particular track
comments = set()
comment_ids = list()


def printData():
    global users
    print('users (max 10, selected at random from '+str(len(users))+' users)')
    temp_copy = users.copy()
    count=0;
    while (count<10 and len(temp_copy)>0):
        popped = temp_copy.pop()
        print(str(count)+'. user '+str(popped.id)+' '+popped.username)
        count = count+1
    
    global x_follows_y
    print ''
    print('X-follows-Y relationships (max 10 selected at random from '+str(len(x_follows_y))+' follow relationships)')
    temp_copy = x_follows_y.copy()
    count=0;
    while (count<10 and len(temp_copy)>0):
        popped = temp_copy.pop()
        print(str(count)+'. user id: '+str(popped[0])+' follows '+str(popped[1]))
        count = count+1
        
    global tracks
    print ''
    print('tracks (max 10 selected at random from '+str(len(tracks))+' tracks)')
    temp_copy = tracks.copy()
    count=0;
    while (count<10 and len(temp_copy)>0):
        popped = temp_copy.pop()
        try:  # might throw a type error if there are strange characters in the title or genre for a track
            print(str(count)+'. user id: '+str(popped.user_id)+', track id: '+str(popped.id)+', title: '+popped.title+', genre: '+popped.genre)
        except Exception as e:
            print(str(count)+'. user id: '+str(popped.user_id)+', track id: '+str(popped.id)+', title and genre - error in displaying, '+ e.message)
        count = count+1
            
    global groups
    print ''
    print('groups (max 10 selected at random from '+str(len(groups))+' groups)')
    temp_copy = groups.copy()
    count=0;
    while (count<10 and len(temp_copy)>0):
        popped = temp_copy.pop()
        print(str(count)+'. user id: '+str(popped[0])+' is in group id: '+str(popped[1]))
        count = count+1

    global favourites
    print ''
    print('User-favourited tracks (max 10 selected at random from '+str(len(favourites))+' user-favourite-track relationships)')
    temp_copy = favourites.copy()
    count=0;
    while (count<10 and len(temp_copy)>0):
        popped = temp_copy.pop()
        print(str(count)+'. user id: '+str(popped[0])+' follows '+str(popped[1]))
        count = count+1

    global comments
    print ''
    print('User comments (max 10 selected at random from '+str(len(comments))+' comments from all users)')
    temp_copy = comments.copy()
    count=0;
    while (count<10 and len(temp_copy)>0):
        popped = temp_copy.pop()
        print(str(count)+'. user id: '+str(popped.user_id)+' on track '+str(popped.track_id)+': '+popped.body)
        count = count+1


        
def getRandomUser():
    userfound = False
    while userfound == False: # SoundCloud has about 55 million users at this time - return random number between 0 and 200 million
        userId = random.randint(0, 200000000)
        try:
            user = client.get('/users/' + str(userId))
        except Exception:
            pass
        else:
            userfound = True    
    return user


def getXUserIDs(limit=10):
    users = set()
    for i in range(0,limit):
        #print i
        users.add(getRandomUser().id)
    return users


def getAllFollowers(user):
    strUserID = str(user.id)
    followers = clientGet('/users/'+strUserID+'/followers')
    print('Exploring followers of User = '+ strUserID+' with '+str(len(followers))+' followers')
    return followers


def getAllFollowings(user):
    strUserID = str(user.id)
    followings = clientGet('/users/'+strUserID+'/followings')
    print('Exploring following activities of User = '+ strUserID+' who follows '+str(len(followings))+' users')
    return followings


def clientGet(request, maxAttempts=10):
    success = False;
    count = 0
    result = None
    timeDelay = 0.5
    
    while(not(success) and (count<maxAttempts)):
        try:
            result = client.get(request)
            success = True
            break
        except Exception as e:
            count = count+1
            time.sleep(timeDelay)
            print('Problem connecting to SoundCloud client, error '+str(e)+'. Trying again... attempt '+str(count)+' of '+str(maxAttempts))
    if (not(success)):
        print('***Unable to retrieve information from SoundCloud for the request: '+request)
    return result
            
            

def getNewSnowballSample(sampleSize=10):
    ''' Generates a new sample of users (set to the specified sample size, default 10), also generating 
    data on those users' tracks and follow relationships between the users in the set 
    N.B. This wipes any previously collected samples that are only stored in local memory '''
    
    global users
    global user_ids
    global tracks
    global track_ids
    global x_follows_y
    global groups
    global favourites
    global comments
    global comment_ids
    users = set() # initialised to empty
    user_ids = list()
    x_follows_y = set() # initialised to empty
    tracks = set() # initialised to empty
    track_ids = list()
    groups = set() # initialised to empty
    favourites = set() # initialised to empty
    comments = set() # initialised to empty
    comment_ids = list()
    print('Generating snowball sample with a sample size of '+str(sampleSize))
    while (len(users)<sampleSize):
        user = getRandomUser() # get a new starting point at random        
        if (not(user.id in user_ids)):
            users.add(user)
            user_ids.append(user.id)
        print('Seed user = '+str(user.id))
        if (len(users)<sampleSize):  #in case adding the new user to our sample brings us to our desired samplesize
            collectUsersFromSeedUser(user,sampleSize)
    # populate the contents of the remaining global variables  with data relating to the new sample of users
    getTracks()
    getFavourites()
    getGroups()
    #getPlaylists()
    getComments()

def collectUsersFromSeedUser(user,sampleSize):
    ''' Populate the users and x_follows_y sets with data sampled from SoundCloud '''
    global users
    global user_ids
    global x_follows_y
    # look for all followers of user    
    followers = getAllFollowers(user)
    # add each follower to users set
    count=0
    while (len(users)<sampleSize and count<len(followers)): # repeat till sample size reached
#         print('length = '+str(len(users))+', sampleSize = '+str(sampleSize)+', count = '+str(count)+', len followers = '+str(len(followers)))
#         print('user '+str(followers[count].id)+' follows '+str(user.id))
        # Add the follower to the set of SC users
        if (not(followers[count].id in user_ids)):
            users.add(followers[count]) 
            user_ids.append(followers[count])
        # Add follows relationships between the follower and this seed user
        x_follows_y.add((followers[count].id, user.id))
        count = count+1
      
    # look for all followings of user (i.e. all users that our seed user follows)    
    followings = getAllFollowings(user)
    # add each follower to users set
    count=0
    while (len(users)<sampleSize and count<len(followings)): # repeat till sample size reached
#         print('length = '+str(len(users))+', sampleSize = '+str(sampleSize)+', count = '+str(count)+', len followings = '+str(len(followings)))
#         print('user '+str(user.id)+' follows '+str(followings[count].id))
        # Add the follower to the set of SC users
        if (not(followings[count].id in user_ids)):       
            users.add(followings[count]) 
            user_ids.append(followings[count])
        # Add follows relationships between the seed user and the user they follow
        x_follows_y.add((user.id, followings[count].id))
        count = count+1
        
    # repeat this step with each follower as the seed user, picking up the results in users
    count = 0
    while (len(users)<sampleSize and count<len(followers)):
        collectUsersFromSeedUser(followers[count],sampleSize)
        count = count+1
        
    # repeat this step with each following (user that the seed user follows) as the seed user, picking up the results in users
    count = 0
    while (len(users)<sampleSize and count<len(followings)):
        collectUsersFromSeedUser(followings[count],sampleSize)
        count = count+1


def getTracks():
    print 'Getting data about users\' tracks...'
    global users
    global tracks
    global track_ids
    for user in users:
        u_id = user.id 
        user_tracks = clientGet('/users/'+str(u_id)+'/tracks')
        for u_track in user_tracks:
            if (not(u_track.id in track_ids)):
                tracks.add(u_track)
                track_ids.append(u_track.id)
    
    
def getGroups():
    print 'Getting data about users\' groups...'
    global users
    global groups
    for user in users:
        u_id = user.id 
        user_groups = clientGet('/users/'+str(u_id)+'/groups')
        for u_group in user_groups:
            if (not(u_group in groups)):
                groups.add((u_id, u_group.id))

        
def getFavourites():
    print 'Getting data about users\' likes...'
    global users
    global favourites
    for user in users:
        u_id = user.id 
        user_favourites = clientGet('/users/'+str(u_id)+'/favorites') # Note US spelling
        for u_favourite in user_favourites:
            favourites.add((u_id, u_favourite.id))    
    
    
def getComments():
    print 'Getting data about comments on users\' tracks...'
    global users
    global comments
    global comment_ids
    for user in users:
        u_id = user.id 
        user_comments = clientGet('/users/'+str(u_id)+'/comments')
        for u_comment in user_comments:
            if (not(u_comment.id in comment_ids)):
                comments.add(u_comment)
                comment_ids.append(u_comment.id)
    
 
#def getPlaylists():
#    print 'Getting data about users\' playlists...'
#    global users
#    global playlists
#    for user in users:
#        u_id = user.id 
#        user_playlists = clientGet('/users/'+str(u_id)+'/playlists') 
#        for u_playlist in user_playlists:
#            for u_track in u_playlist.tracks
#                playlists.add((u_id, u_playlist.id, u_track.id))



def exportDataToSQLite():
    global users
    global x_follows_y
    global tracks
    print '' # for neater display 
    dbFileName='scdb.sqlite'
    try:
        db = sqlite3.connect(dbFileName)
        cursor = db.cursor()
        # Start with fresh database
        cursor.execute('''DROP TABLE IF EXISTS users''')
        cursor.execute('''DROP TABLE IF EXISTS x_follows_y''')
        cursor.execute('''DROP TABLE IF EXISTS tracks''')
        cursor.execute('''DROP TABLE IF EXISTS groups''')
        cursor.execute('''DROP TABLE IF EXISTS favourites''')
        cursor.execute('''DROP TABLE IF EXISTS comments''')
        db.commit()
        print 'Creating users table in DB....'
        # Check if table users does not exist and create it
        cursor.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, 
                             permalink_url TEXT, full_name TEXT, description TEXT,  
                             city TEXT, country TEXT, 
                             track_count INTEGER, playlist_count INTEGER, 
                             followers_count INTEGER, followings_count INTEGER, public_favorites_count INTEGER)''')
        print('Adding data to users table in DB.... Total num of users: '+str(len(users)))
        for user in users:
            try:
                cursor.execute('''INSERT INTO users(id, username,
                             permalink_url, full_name, description,  
                             city, country,
                             track_count, playlist_count, 
                             followers_count, followings_count, public_favorites_count) 
                             VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                             (user.id, user.username, 
                              user.permalink_url, user.full_name, user.description, 
                              user.city, user.country, 
                              user.track_count, user.playlist_count, 
                              user.followers_count, user.followings_count, user.public_favorites_count))
            except Exception as e:
                print('Error adding user '+str(user.id)+' to the database: '+e.message+' '+str(e.args))
        # X FOLLOWS Y set of tuples (follower.id, followed.id) 
        print 'Creating x_follows_y table in DB....'
        cursor.execute('''CREATE TABLE IF NOT EXISTS x_follows_y(follower INTEGER, followed INTEGER, PRIMARY KEY (follower, followed))''')
        print('Adding data to x_follows_y table in DB.... Total num of follows_rels: '+str(len(x_follows_y)))
        for follow in x_follows_y:
#            print('Inserting '+str(follow[0])+' follows '+str(follow[1])+' into the database. Total num of follows_rels: '+str(len(x_follows_y)))
            try:
                cursor.execute('''INSERT INTO x_follows_y(follower, followed) 
                              VALUES(?, ?)''', 
                              (follow[0], follow[1]))
            except Exception as e:
                print('Error adding ['+str(follow[0])+' follows '+str(follow[1])+'] to the database: '+e.message+' '+str(e.args))
        # TRACKS
        print 'Creating tracks table in DB....'
        cursor.execute('''CREATE TABLE IF NOT EXISTS tracks(
        id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT,   
        permalink_url TEXT,  track_type TEXT, state TEXT, created_at TEXT, 
        original_format TEXT, description TEXT, sharing TEXT,   
        genre TEXT, duration INTEGER, key_signature TEXT, bpm INTEGER, 
        license TEXT, label_id INTEGER, label_name TEXT,
        playback_count INTEGER,  
        favoritings_count INTEGER, 
        streamable TEXT, stream_url TEXT, 
        downloadable TEXT, download_count INTEGER, 
        commentable TEXT, comment_count INTEGER,
        purchase_url TEXT, artwork_url TEXT, video_url TEXT, embeddable_by TEXT,
        release TEXT, release_month INTEGER, release_day INTEGER, release_year INTEGER,  
        tag_list TEXT)''')   
        print('Adding data to tracks table in DB..... Total num of tracks: '+str(len(tracks)))
        for track in tracks:
            try:
                cursor.execute('''INSERT INTO tracks(id, user_id, title,   
        permalink_url,  track_type, state, created_at, 
        original_format, description, sharing,   
        genre, duration, key_signature, bpm, 
        license, label_id, label_name,
        playback_count,  
        favoritings_count, 
        streamable, stream_url, 
        downloadable, download_count, 
        commentable, comment_count,
        purchase_url, artwork_url, video_url, embeddable_by,
        release, release_month, release_day, release_year,  
        tag_list) 
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                   ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                   ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                   ?, ?, ?, ?)''',
                (track.id, track.user_id, track.title,   
                track.permalink_url, track.track_type, track.state, track.created_at, 
                track.original_format, track.description, track.sharing,   
                track.genre, track.duration, track.key_signature, track.bpm, 
                track.license, track.label_id, track.label_name,
                track.playback_count,  
                track.favoritings_count, 
                track.streamable, track.stream_url, 
                track.downloadable, track.download_count, 
                track.commentable, track.comment_count,
                track.purchase_url, track.artwork_url, track.video_url, track.embeddable_by,
                track.release, track.release_month, track.release_day, track.release_year,  
                track.tag_list)) 
            except Exception as e:
                print('Error adding track '+str(track.id)+' to the database: '+e.message+' '+str(e.args))

        # GROUPS information about what groups users belong to 
        print 'Creating groups table in DB....'
        cursor.execute('''CREATE TABLE IF NOT EXISTS groups(user_id INTEGER, group_id INTEGER, PRIMARY KEY (user_id, group_id))''')
        print('Adding data to groups table in DB.... Total num of group memberships: '+str(len(groups)))
        for group in groups:
            try:
                cursor.execute('''INSERT INTO groups(user_id, group_id) 
                              VALUES(?, ?)''', 
                              (group[0], group[1]))
            except Exception as e:
                print('Error adding user '+str(group[0])+' group membership of '+str(group[1])+' to the database: '+e.message+' '+str(e.args))
        # PLAYLISTS information about what tracks users add to playlists 
        # leave this for now
        
        # FAVOURITES information about what tracks a user Likes
        print 'Creating favourites table in DB....'
        cursor.execute('''CREATE TABLE IF NOT EXISTS favourites(user INTEGER, track INTEGER, PRIMARY KEY (user, track))''')
        print('Adding data to favourites table in DB.... Total num of favourite entries: '+str(len(favourites)))
        for favourite in favourites:
            try:
                cursor.execute('''INSERT INTO favourites(user, track) 
                              VALUES(?, ?)''', 
                              (favourite[0], favourite[1]))
            except Exception as e:
                print('Error adding user '+str(favourite[0])+' favouriting track '+str(favourite[1])+' to the database: '+e.message+' '+str(e.args))
        # COMMENTS information about what comments a user makes on tracks
        # (restricted to the tracks produced by users in the sample)
        print 'Creating comments table in DB....'
        cursor.execute('''CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY,
        body TEXT, user_id INTEGER, track_id INTEGER, 
        timestamp INTEGER, created_at TEXT)''')
        print('Adding data to comments table in DB.... Total num of comment entries: '+str(len(comments)))
        for comment in comments:
            try:
                cursor.execute('''INSERT INTO comments(id, body, user_id, track_id, timestamp, created_at) 
                              VALUES(?, ?, ?, ?, ?, ?)''', 
                              (comment.id, comment.body, comment.user_id, comment.track_id, 
                               comment.timestamp, comment.created_at))
            except Exception as e:
                print('Error adding user comment '+str(comment.id)+' to the database: '+e.message+' '+str(e.args))
        print 'Ready to commit DB to file'
        db.commit()
    # Catch the exception
    except Exception as e:
        # Roll back any change if something goes wrong
        db.rollback()
        print 'Exception caught in exportDataToSQLite function'
        print e.message
        print(str(e.args))
        #raise e
    finally:
        # Close the db connection
        db.close()
        print('Data saved in '+dbFileName)

def main(sampleSize = 15): 
    getNewSnowballSample(sampleSize)
    printData() 
    exportDataToSQLite()