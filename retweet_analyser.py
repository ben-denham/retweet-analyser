#!/bin/python
from __future__ import print_function
import twitter
from sys import version_info
import argparse
import matplotlib.pyplot as plt
from textwrap import wrap
from datetime import datetime

python3 = version_info.major >= 3
if python3:
    iteritems = lambda d: d.iteritems()
else:
    iteritems = lambda d: iter(d.items())

def get_api():
    try:
        import settings as settings
    except:
        print("You have not created your 'settings.py' file. Please copy "
              "'settings.py.sample' to 'settings.py', and set values for "
              "the variables.")
        exit(1)
    auth = twitter.OAuth(settings.access_token,
                         settings.access_token_secret,
                         settings.consumer_key,
                         settings.consumer_secret)
    api = twitter.Twitter(auth=auth)
    return api


def get_min_id(tweets):
    if len(tweets) == 0:
        return None

    min_id = int(tweets[0]['id'])

    for tweet in tweets:
        if int(tweet['id']) < min_id:
            min_id = int(tweet['id'])

    return min_id


def get_tweets(api, keywords, user):

    keywords = [keyword.lower() for keyword in keywords]
    kwargs = {
        'contributor_details': False,
        'include_rts': False,
        'userid': user,
        'screen_name': user,
        'count': 200
        }

    tweets = api.statuses.user_timeline(**kwargs)
    kwargs['max_id'] = get_min_id(tweets)

    while True:
        new_tweets = api.statuses.user_timeline(**kwargs)

        if new_tweets:
            tweets += new_tweets

            cur_max_id = kwargs['max_id']
            kwargs['max_id'] = get_min_id(new_tweets)
            if kwargs['max_id'] == cur_max_id:
                break
        else:
            break

    # Iterate over a copy so that we can remove items.
    for tweet in tweets[:]:
        tweet_text = tweet['text'].lower()
        keyword_found = False
        for keyword in keywords:
            if keyword in tweet_text:
                keyword_found = True
                break
        if not keyword_found:
            tweets.remove(tweet)

        tweet['created_at'] = datetime.strptime(tweet['created_at'],
                                                '%a %b %d %H:%M:%S +0000 %Y')

    return tweets


class AnnotationManager(object):
    annotation = None

    def __init__(self, annotes):
        self.annotes = annotes

    def __call__(self, event):
        try:
            self.annotation.remove()
        except:
            pass

        line = event.artist
        ind = event.ind[0]
        username = line.get_url()
        x = line.get_xdata()[ind]
        y = line.get_ydata()[ind]

        try:
            annote = self.annotes[username][x][y]
        except:
            return
        self.annotation = plt.annotate('\n'.join(wrap(annote['text'], 40)),
                                       (annote['x'], annote['y']),
                                       bbox = dict(facecolor='white'))
        plt.draw()


def graph(data, title, set_style='o'):
    plot_args = []
    labels = []
    annotes = {}

    for username, tweets in iteritems(data):
        x_tweet_times = [tweet['created_at'] for tweet in tweets]
        y_retweet_counts = [tweet['retweet_count'] for tweet in tweets]
        labels.append(username)

        plot_args += [x_tweet_times, y_retweet_counts, set_style]

        for tweet in tweets:
            if not annotes.get(username):
                annotes[username] = {}
            if not annotes[username].get(tweet['created_at']):
                annotes[username][tweet['created_at']] = {}

            annotes[username][tweet['created_at']][tweet['retweet_count']] = dict(
                text=u'"{}" - {} retweets - @{} - {} UTC'.format(tweet['text'],
                                                                 tweet['retweet_count'],
                                                                 username,
                                                                 tweet['created_at'],),
                x=tweet['created_at'],
                y=tweet['retweet_count']
                )

    lines = plt.plot(*plot_args, picker=5)
    for key, line in enumerate(lines):
        line.set_url(labels[key])

    plt.setp(lines, linewidth=2.0)

    am = AnnotationManager(annotes)
    plt.connect('pick_event', am)

    leg = plt.legend(labels)
    leg.set_title('Click on a dot to toggle display')
    lined = {}
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)
        lined[legline] = origline

    def leg_onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        try:
            origline = lined[legline]
        except:
            return
        vis = not origline.get_visible()
        origline.set_visible(vis)
        plt.draw()
    plt.connect('pick_event', leg_onpick)

    plt.ylabel('Retweet count')
    plt.suptitle(title)
    plt.show()

def main(keywords, users):
    data = {}
    api = get_api()
    for user in users:
        data[user] = get_tweets(api, keywords, user)
    graph(data, 'Retweet counts for tweets containing: "{}"'.format(
            '", "'.join(keywords)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyse the retweets of '
                                     'twitter users.')
    parser.add_argument('--keywords', '-k', nargs='+')
    parser.add_argument('--users', '-u', nargs='+')

    args = parser.parse_args()
    main(args.keywords, args.users)
