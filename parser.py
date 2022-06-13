#!/usr/bin/python3

import sys, getopt
import os.path
import argparse
import bs4
import asyncio
import aiohttp
import logging
#import psycopg2
import glob
import json
from aiohttp import ClientSession
from pathlib import Path
from urllib.parse import urlparse


logger = logging.getLogger('asyncio')
logging.basicConfig(filename='example.log',level=logging.INFO)
console = logging.StreamHandler()
logger.addHandler(console)


def track_and_album_processor(soup):
    # track and album pages contain json+ld-string which theoretically contains track information. 
    # unfortunately broken on bandcamp's side: only ever contains the last track, repeating
    jsonblob = soup.find("script", {"type": "application/ld+json"})
    if jsonblob is None:
        jsonblob = soup.find("script", {"type": "application/json+ld"})
    jsoncontents = "".join(jsonblob.contents)
    jsonld = json.loads(jsoncontents)
    if verbose is True:
        print('json+ld: ',jsonld)
        print('-------------------------------------------------------------------')

    # "h2 class trackTitle" is the definitive title of a track or album
    titletag = soup.find("h2", {"class": "trackTitle"})
    title = titletag.getText()
    strippedtitle = title.strip()
    print("h2_trackTitle: ", strippedtitle)

    # get tags embedded in html
    meta_title =        soup.find("meta", {"property": "og:title"}).get("content").strip()
    meta_type =         soup.find("meta", {"property": "og:type"}).get("content").strip()
    meta_site_name =    soup.find("meta", {"property": "og:site_name"}).get("content").strip()
    meta_description =  soup.find("meta", {"property": "og:description"}).get("content").strip()
    meta_image =        soup.find("meta", {"property": "og:image"}).get("content").strip()

    print("og:meta_title = ",meta_title)
    print("og:meta_type = ",meta_type)
    print("og:meta_site_name = ",meta_site_name)
    print("og:meta_description = ",meta_description)
    print("og:meta_image = ",meta_image)

    # get tags embedded in javascript script "data-tralbum-collect-info" 
    js_tralbum = soup.find("script", {"data-tralbum-collect-info":True}) 
    #print(js_tralbum)

    # get dictionaries from data-tralbum-collect-info 
    js_data_band = js_tralbum['data-band']
    js_data_embed = js_tralbum['data-embed']
    js_data_tralbum = js_tralbum['data-tralbum']

    js_data_band_dict = json.loads(js_data_band)
    js_data_embed_dict = json.loads(js_data_embed)
    js_data_tralbum_dict = json.loads(js_data_tralbum)

    # unused available tags in js-data-tralbum-collect-info:
    '''
    data-cart
    data-site
    data-fan
    data-band-follow-info
    data-payment
    '''

    print('-----js_data_band_dict-----')
    # js_data_band_dict contains:
    # key:value
    for key in js_data_band_dict:
        #print(key, type(js_data_band_dict[key]))
        if verbose is True:
            print(key,(js_data_band_dict[key]))
        else:
            pass
            

    print('-----js_data_embed_dict-----')
    # js_data_embed_dict contains:
    # key:value
    # key:dict
    for key in js_data_embed_dict:
        #print(key, type(js_data_embed_dict[key]))
        if type(js_data_embed_dict[key]) is dict:
            for key2 in js_data_embed_dict[key]:
                #print(key, key2, type(js_data_embed_dict[key][key2]))

                # some of those dicts contain dicts
                if type(js_data_embed_dict[key][key2]) is dict:
                    for key3 in js_data_embed_dict[key][key2]:
                        if verbose is True:
                            print(key,key2,js_data_embed_dict[key][key2][key3])
                        else:
                            pass

                else:
                    if verbose is True:
                        print(key,key2,js_data_embed_dict[key][key2])
                    else:
                        pass
        else:
            if verbose is True:
                print(key, (js_data_embed_dict[key]))
            else:
                pass   
                

    print('-----js_data_tralbum_dict-----')
    # js_data_tralbum_dict contains:
    # key:value
    for key in js_data_tralbum_dict:
        #print(key, type(js_data_tralbum_dict[key]))
        if type(js_data_tralbum_dict[key]) is dict:
            # get dicts "play_cap_data" and "current"
            # these contain only dicts
            for key2 in js_data_tralbum_dict[key]:
                if verbose is True:
                    print(key,key2,js_data_tralbum_dict[key][key2])
                else:
                    pass

        elif type(js_data_tralbum_dict[key]) is list:
            i = 0
            # get lists  "packages" and "trackinfo"
            #print(key, type(js_data_tralbum_dict[key]))

            # these lists contain only dicts 
            for listelem in js_data_tralbum_dict[key]:
                i +=1
                #print('listelem ',i)
                #print(key, listelem)
                if key == 'trackinfo':
                    tracknumber_from_dict = listelem['track_num']
                    if verbose is True:
                        print('number', tracknumber_from_dict)
                        print("it's a track")
                elif key == 'packages':
                    print("it's a package")
                    packagenumber = i
                    print('number',i)
                else:
                    # this should not happen:
                    print("it's neither track nor package but:",key, listelem)
                j = 0
                for key2 in listelem:
                    #print(key,key2,type(listelem[key2]))
                    if type(listelem[key2]) is dict:
                        # get dict "trackinfo file"
                        for key3 in listelem[key2]:
                            if verbose is True:
                                print(key,key2,key3,listelem[key2][key3])
                            else:
                                pass
                    
                    elif type(listelem[key2]) is list:
                        # get lists "packages origins", "packages arts", "packages options"
                        for key3 in listelem[key2]:
                            j += 1
                            print('ANOTHER LISTITEM INSIDE A LIST, nr ',j)
                            #print(key,key2,type(listelem[key2]))
                            # these contain lists
                            for elem in listelem[key2]:
                                #print(key,key2,elem)
                                #which contain dicts
                                for key3 in elem:
                                    if verbose is True:
                                        print(key,key2,key3,elem[key3])
                                    else:
                                        pass
                    else:
                        if verbose is True:
                            print(key,key2,listelem[key2])
                        else:
                            pass
    
        else:
            if verbose is True:
                print(key, js_data_tralbum_dict[key])
            else:
                pass
    js_name = js_data_band_dict['name']
    js_artist_id = js_data_band_dict['id']
    #print(js_name, js_artist_id)


def run(content):
    pagetype = ''
    releases = ''
    soup = bs4.BeautifulSoup(content,features="html.parser")
    #print(soup.find("a", href=True))
    og_url_tag = soup.find("meta", {"property": "og:url"})
    if og_url_tag is None:
        print('ERROR this does not seem to be bandcamp page')
    else:
        og_url = og_url_tag.get("content")

        div_album = soup.find("div", {"keytype": "http://schema.org/MusicAlbum"})
        div_track = soup.find("div", {"keytype": "http://schema.org/MusicRecording"})
        
        print('meta og:url: ',og_url)
        print('-------------------------------------------------------------------')

        # og_url contains information to decide page type 
        if (og_url == "https://bandcamp.com"):
            print("Artist seems gone")

        elif "/track/" in og_url:
            pagetype = 'track'
            track_and_album_processor(soup)
            
        elif "/album/" in og_url:
            pagetype = 'album'
            track_and_album_processor(soup)
        elif og_url.endswith("com/subscribe"):
            pagetype = 'subscribe'
              
        else:
            # should be releaselist if neither track nor album
            if (not div_album and not div_track):
                musicgrid = soup.find("ol", {"id": "music-grid"})
                # 'music' is releaselist under /music/
                pagetype = 'music'
                releases = musicgrid.find_all('li')
                for release in releases:
                    link = release.find("a", href=True)
                    if verbose is True:
                        print(link.get('href'))
                    else:
                        pass

                labellink = soup.find("a", {"class":"back-to-label-link"})
                if labellink:
                    if verbose is True:
                        print('labellink: ',labellink.get('href'))
                    else:
                        pass
            else:
                print("Unknown Page Type", og_url)

async def main(loop):
    session = ClientSession()
    url = 'https://luke-vibert.bandcamp.com/album/ila020-valvable-digital'
    async with session as s:
        async with s.get(url) as r:
            content = await r.text()
            print(content)
    soup = bs4.BeautifulSoup(content, features="lxml")
    jsonblob = soup.find("script", {"type": "application/ld+json"})
    jsoncontents = "".join(jsonblob.contents)
    jsonld = json.loads(jsoncontents)
    print(jsonld)
    
            
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))