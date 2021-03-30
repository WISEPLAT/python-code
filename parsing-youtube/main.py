import urllib.request
import json


def get_all_video_from_channel(channel_id):
    api_key = "AIzaSyAAseOhUtnaN1q7YEdyoMoZ4Vf1qCjhHCk"

    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url + 'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(api_key,
                                                                                                        channel_id)

    video_links = []
    url = first_url
    while True:
        print(url)
        inp = urllib.request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_links.append(base_video_url + i['id']['videoId'])

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break
    return video_links


def get_all_video_with_titles_from_channel(channel_id):
    api_key = "AIzaSyAAseOhUtnaN1q7YEdyoMoZ4Vf1qCjhHCk"

    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url + 'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(api_key,
                                                                                                        channel_id)

    video_links = []
    url = first_url
    while True:
        #print(url)
        inp = urllib.request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_links.append([base_video_url + i['id']['videoId'],
                                    i['id']['videoId'],
                                    i['snippet']['title'],
                                    i['snippet']['publishTime']])

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break
    return video_links


def get_information_from_youtube_video(video_id):
    api_key = "AIzaSyAAseOhUtnaN1q7YEdyoMoZ4Vf1qCjhHCk"

    base_info_url = 'https://www.googleapis.com/youtube/v3/videos?'

    info_url = base_info_url + 'part=statistics&key={}&id={}'.format(api_key, video_id)

    print(info_url)
    inp = urllib.request.urlopen(info_url)
    resp = json.load(inp)

    return resp


# youtube_channel_id = "UC7f5bVxWsm3jlZIPDzOMcAg"
# all_video_links = get_all_video_from_channel(youtube_channel_id)
# for link in all_video_links:
#     print(link)
#     print(link, file=open(youtube_channel_id+"_1.txt", "a"))
#
# print("Total: ",len(all_video_links))

youtube_channel_id = "UC7f5bVxWsm3jlZIPDzOMcAg"
# all_video_links = get_all_video_with_titles_from_channel(youtube_channel_id)
# print(all_video_links)

import pickle
# with open(youtube_channel_id+'_1.data', 'wb') as fp:
#     pickle.dump(all_video_links, fp)

with open(youtube_channel_id+'_1.data', 'rb') as fp:
    all_video_links = pickle.load(fp)
print(all_video_links)

# info_from_video = get_information_from_youtube_video("ZJER0vEtzd0")
# print(info_from_video)
# print(info_from_video['items'][0]['statistics']['viewCount'])


from youtube_dl import YoutubeDL
# video = all_video_links[0]
# video = "https://www.youtube.com/watch?v=ZJER0vEtzd0"

video = all_video_links[0][0]
print("For: ", video)

youtube_dl_opts = {
    'ignoreerrors': True,
    'quiet': True
}

with YoutubeDL(youtube_dl_opts) as ydl:
    info_dict = ydl.extract_info(video, download=False)
    video_id = info_dict.get("id", None)
    video_views = info_dict.get("view_count", None)
    video_date = info_dict.get("upload_date", None)
    video_duration = info_dict.get("duration", None)
    video_title = info_dict.get('title', None)
    print(video_id, video_views, video_date, video_duration, video_title)
