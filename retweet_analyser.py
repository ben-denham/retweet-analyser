#!/bin/python
from __future__ import print_function
import tweepy
from sys import version_info
import argparse
import matplotlib.pyplot as plt
from textwrap import wrap

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
    auth = tweepy.OAuthHandler(settings.consumer_key, settings.consumer_secret)
    auth.set_access_token(settings.access_token, settings.access_token_secret)
    return tweepy.API(auth)


def get_min_id(tweets):
    if len(tweets) == 0:
        return None

    min_id = tweets[0].id

    for tweet in tweets:
        if tweet.id < min_id:
            min_id = tweet.id

    return min_id


def get_tweets(api, keywords, user):

    kwargs = {
        'contributor_details': False,
        'include_rts': False,
        'userid': user,
        'screen_name': user,
        'count': 200
        }

    tweets = api.user_timeline(**kwargs)
    kwargs['max_id'] = get_min_id(tweets)

    while True:
        new_tweets = api.user_timeline(**kwargs)

        if new_tweets:
            tweets += new_tweets

            cur_max_id = kwargs['max_id']
            kwargs['max_id'] = get_min_id(new_tweets)
            if kwargs['max_id'] == cur_max_id:
                break
        else:
            break

    for keyword in keywords:
        tweets = [tweet for tweet in tweets
                  if keyword.lower() in tweet.text.lower()]

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

        annote = self.annotes[username][x][y]
        self.annotation = plt.annotate('\n'.join(wrap(annote['text'], 40)),
                                       (annote['x'], annote['y']),
                                       bbox = dict(facecolor='white'))
        plt.draw()


def graph(data, title, set_style='-o'):
    plot_args = []
    labels = []
    annotes = {}

    for username, tweets in iteritems(data):
        x_tweet_times = [tweet.created_at for tweet in tweets]
        y_retweet_counts = [tweet.retweet_count for tweet in tweets]
        labels.append(username)

        plot_args += [x_tweet_times, y_retweet_counts, set_style]

        for tweet in tweets:
            if not annotes.get(username):
                annotes[username] = {}
            if not annotes[username].get(tweet.created_at):
                annotes[username][tweet.created_at] = {}

            annotes[username][tweet.created_at][tweet.retweet_count] = dict(
                text=u'"{}" - {} retweets - @{} - {}'.format(tweet.text,
                                                             tweet.retweet_count,
                                                             username,
                                                             tweet.created_at,),
                x=tweet.created_at,
                y=tweet.retweet_count
                )

    lines = plt.plot(*plot_args, picker=5)
    for key, line in enumerate(lines):
        line.set_url(labels[key])
    plt.setp(lines, linewidth=2.0)
    am = AnnotationManager(annotes)
    plt.connect('pick_event', am)

    plt.legend(labels)
    plt.ylabel('Retweet count')
    plt.suptitle(title)
    plt.show()

def main(keywords, users):
    data = {}
    api = get_api()
    for user in users:
        data[user] = get_tweets(api, keywords, user)
    graph(data, 'Retweet counts for tweets containing: "{}"'.format(
            '" ",'.join(keywords)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyse the retweets of '
                                     'twitter users.')
    parser.add_argument('--keywords', '-k', nargs='+')
    parser.add_argument('--users', '-u', nargs='+')

    args = parser.parse_args()
    main(args.keywords, args.users)
