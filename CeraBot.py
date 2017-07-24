import discord
import asyncio
import random
import re
import requests
from pytvdbapi import api
import urllib3
import json
from plexapi.myplex import MyPlexAccount


######Global Settings#######################################################
#Plex
plex_username = ''
plex_password = ''
plex_servername = ''
plex_movies = ''
plex_tv = ''

#Discord
client_code = ''
game_list = []


#TVDB.com
tvdb_code = ''

#SickBeard
sickbeard_url = ''
sickbeard_api = ''
#############################################################################

#Connect to Plex Server
account = MyPlexAccount.signin(plex_username,plex_password)
plex = account.resource(plex_servername).connect()

#Connect to TVDB API
db = api.TVDB(tvdb_code)
http = urllib3.PoolManager()

#Global Variables
message_count = 0

#Establish the game Discord Bot is playing
client = discord.Client()
game1= discord.Game()
game1.name = str(game_list[random.randrange(0,len(game_list))])
client.change_presence(game=game1)


#Login to Discord
@client.event
async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print(game1.name)
        print('------')
        await client.change_presence(game=game1)

#Listen to messages
@client.event
async def on_message(message):
        global message_count
        global game_list
        global game1

        #Changes the name of the game being played
        if message_count == 10:
                game1.name = str(game_list[random.randrange(0,len(game_list))])
                await client.change_presence(game=game1)
                message_count = 0
        else:
                message_count = message_count + 1

        #disallows the bot to respond to itself
        if message.author == client.user:
                return

        server = message.server
        channel = message.channel
        user = message.author
        content = message.content


        #Commands
        # %help command
        if re.match('^\%help', content):
                await client.send_message(message.channel, "##### Help for CeraBot #####\n%help - Outputs the commands\n%movie (text) - Allows for search of movies in Plex\n%tv (text) Allows for search of tv shows in Plex\n%shows - List shows currently being downloaded by SickBeard\n%sickbeard - Outputs the total stats for Sickbeard\n%sbping - Pings the Sickbeard server\n%request - Pulls in Request for TV Shows(BROKEN)")

        # %shows command
        elif re.match('^\%shows', content):
                #Pull in JSON entry for all shows (3d Dict)
                shows = requests.get('https://'+sickbeard_url+'/api/'+sickbeard_api+'/?cmd=shows&sort=name', verify=False).json()
                show_list = shows['data']
                tvdbid = show_list.keys()
                tvdbid_keys = list(tvdbid)

                #Define the show list for the loop
                Output_list = list()

                #Loop across the keys and search the dict for 'data' 'tvdbid' and 'show_name'
                for tvdbid_keys_name in tvdbid_keys:
                        show_list = (shows['data'][tvdbid_keys_name]['show_name'])
                        #print(show_list)
                        Output_list.append(show_list)
                await client.send_message(message.channel,"\n".join(Output_list))


        # %request command
        elif re.match('(^%request\s)(.*)', content):
                request_value_regex =  re.match('(^%request\s)(.*)', content)
                request_value = request_value_regex.group(2)
                await client.send_message(message.channel,"Your search: %s" % (request_value))
                result = db.search(request_value, 'en')
                show = result[0]
                await client.send_message(message.channel,"Closest Show: %s" %(show.SeriesName))
                show_proper = show.SeriesName
                #print(show.SeriesName)

                sickbeard_search = requests.get('https://'+sickbeard_url+'/api/'+sickbeard_api+'/?cmd=sb.searchtvdb&name='+show_proper+'&lang=en', verify=False).json()
                #print(sickbeard_search)
                sickbeard_search_list = sickbeard_search['data']['results']
                print(sickbeard_search_list)
                await client.send_message(message.channel, sickbeard_search_list)


                #test_dict = (" ".join(sickbeard_search_list))
                #print(test_dict)

                #tvdbid_search = (sickbeard_search['data']['results']['tvdbid'])
                #print (tvdbid_search)



                #show_id = requests.get('https://api.thetvdb.com/search?name=request_value')
                #await client.send_message(message.channel, show_id)
                #print (show_id)

                #r=http.request(
                #       'POST',
                #       'https://api.thetvdb.com/login?apikey=',
                #       fields={'apikey':''})
                #print (r.data)
                #await client.send_message(message.channel, r.data)

                #tvdbtoken = requests.get('https://api.thetvdb.com/login?apikey=')
                #await client.send_message(message.channel, tvdbtoken)
                #print (tvdbtoken)
                #request = requests.get('https://172.16.1.42:8081/api//?cmd=show&tvdbid=79349', verify=False)
                #await client.send_message(message.channel, request.content)
                #print (request.content)

        #%Movie Search commmand
        elif re.match('(^%movie\s)(.*)', content):
                movie_value_regex =  re.match('(^%movie\s)(.*)', content)
                movie_value = movie_value_regex.group(2)
                #print(movie_value)
                movies = plex.library.section(plex_movies)
                Output_movie_list = list()
                #Test to see if the Movie exists
                try:
                        for video in movies.search(movie_value):
                                movie_list =('%s(%s)' % (video.title, video.TYPE))
                                Output_movie_list.append(movie_list)
                        await client.send_message(message.channel,"\n".join(Output_movie_list))
                #Output if the Movie doesnt exist
                except:
                        await client.send_message(message.channel,"No Movie found")

        #%TV Show Search commmand
        elif re.match('(^%tv\s)(.*)', content):
                tv_value_regex =  re.match('(^%tv\s)(.*)', content)
                tv_value = tv_value_regex.group(2)
                #print(tv_value)
                tv = plex.library.section(plex_tv)
                Output_tv_list = list()
                #test to see if the Tv Show exists
                try:
                        for video in tv.search(tv_value):
                                tv_list =('%s(%s)' % (video.title, video.TYPE))
                                Output_tv_list.append(tv_list)
                        await client.send_message(message.channel,"\n".join(Output_tv_list))
                #Output if the TV Show doesnt exist
                except:
                        await client.send_message(message.channel,"No TV Show found")

        #%sickbeard statistics
        if re.match('^\%sickbeard', content):
                sickbeard = requests.get('https://'+sickbeard_url+'/api/'+sickbeard_api+'/?cmd=shows.stats', verify=False).json()
                sickbeard_ep_downloaded = sickbeard['data']['ep_downloaded']
                sickbeard_ep_snatched = sickbeard['data']['ep_snatched']
                sickbeard_ep_total = sickbeard['data']['ep_total']
                sickbeard_shows_active = sickbeard['data']['shows_active']
                sickbeard_shows_total = sickbeard['data']['shows_total']
                sickbeard_list = [sickbeard_ep_downloaded,
                                  sickbeard_ep_snatched,
                                  sickbeard_ep_total,
                                  sickbeard_shows_active,
                                  sickbeard_shows_total]

                await client.send_message(message.channel,"##### Sickbeard Statistics#####\nEpisodes downloaded: %s\nEpisodes snatched: %s\nEpisode Total: %s\nShows active: %s\nShows Total: %s" % (sickbeard_ep_downloaded, sickbeard_ep_snatched, sickbeard_ep_total, sickbeard_shows_active, sickbeard_shows_total))

        #%sickbeard ping
        if re.match('^\%sbping', content):
                sickbeard_ping = requests.get('https://'+sickbeard_url+'/api/'+sickbeard_api+'/?cmd=sb.ping', verify=False).json()
                sickbeard_ping_response = sickbeard_ping['message']
                print(sickbeard_ping_response)
                await client.send_message(message.channel,"Sickbeard responds with %s" % (sickbeard_ping_response))



client.run(client_code)
