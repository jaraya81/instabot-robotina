import threading
import time
import schedule
import random
import yaml
import os
import instabot


def your_turn(difficult = 3):
    return random.randrange(difficult) == 0

def is_activate(action):
    if config is None:
        raise Exception("Config not exist")
    if (action not in config) or ("enabled" not in config[action]):
        return False
    return config[action]['enabled']

def refresh_tray_feed():
    if(bot.api.get_reels_tray_feed(reason='pull_to_refresh')):
        bot.logger.info("Refrescando")

def get_users_by_hashtag():
    hashtags = []
    if 'hashtags' in config and 'enabled' in config['hashtags'] and config['hashtags']['enabled'] and 'list' in config['hashtags']:
        hashtags = config['hashtags']['list']
    random.shuffle(hashtags)

    max = config['hashtags']['max'] if 'hashtags' in config and config['hashtags']['max'] else 3
       
    users = []
    for hashtag in hashtags[:max if len(hashtags) > max else len(hashtags)]:
        users.extend(bot.get_hashtag_users(hashtag))

    return users

def likes():
    if your_turn(difficult = 3) and is_activate("likes"):
        print("likes")
        average = config['likes']['average'] if 'likes' in config and config['likes']['average'] else 2
        average = 2 if average < 2 else average

        users = get_users_by_hashtag()
        random.shuffle(users)

        max_users = random.randrange(average - 1, average + 1)
        print("max_users %d" % max_users)
        counter = 0
        for user_id in users:
            if bot.like_user(user_id, amount=1, filtration=True) is not False:
                counter = counter + 1
                if counter >= max_users:
                    break
            
def follows():
    if your_turn(difficult = 2) and is_activate("follows"):
        print("follows")
        average = config['follows']['average'] if 'follows' in config and config['follows']['average'] else 5
        average = 2 if average < 2 else average

        users = get_users_by_hashtag()
        random.shuffle(users)

        max_users = random.randrange(average - 2, average + 2)
        print("max_users: %d" % max_users)
        
        followed = []
        counter = 0
        for user_id in users:
            if bot.follow(user_id, check_user=True) is not False:
                counter = counter + 1
                followed.append(user_id)
                if counter >= max_users:
                    break
         

        refresh_tray_feed()
        for x in followed:
            bot.watch_users_reels(x)

def view_my_following_histories():
    if your_turn(difficult = 2) and is_activate("view_my_following_histories"):
        print("init view_my_following_histories")
        average = config['view_my_following_histories']['average'] if 'view_my_following_histories' in config and config['view_my_following_histories']['average'] else 70
        average = 25 if average < 25 else average
        count_users = random.randrange(average - 25, average + 25)
        user_id = bot.api.user_id

        refresh_tray_feed()

        users = bot.api.get_total_followers_or_followings(
            user_id=user_id,
            usernames=False,
            which='followings'
        )

        stories_viewed = bot.total["stories_viewed"]
        stories_viewed_begin = bot.total["stories_viewed"]

        random.shuffle(users)
        for user in users[:count_users if len(users) > count_users else len(users)]:
            bot.logger.info(user['username'])
            if bot.watch_users_reels(user['pk']) and (bot.total["stories_viewed"] - stories_viewed) != 0:
                bot.logger.info("Stories viewed: %d" % (bot.total["stories_viewed"] - stories_viewed))
                stories_viewed = bot.total["stories_viewed"]

        bot.logger.info("Usuarios: %d" % len(users))
        bot.logger.info("New stories viewed: %d" % (bot.total["stories_viewed"] - stories_viewed_begin))
        bot.logger.info("Total stories viewed: %d" % bot.total["stories_viewed"])

def view_ht_histories():
    if your_turn(difficult = 2) and is_activate("view_ht_histories"):
        print("init view_ht_histories")

        average = config['view_ht_histories']['average'] if 'view_ht_histories' in config and config['view_ht_histories']['average'] else 70
        average = 25 if average < 25 else average

        stories_viewed = bot.total["stories_viewed"]
        stories_viewed_begin = bot.total["stories_viewed"]

        users = get_users_by_hashtag()
        random.shuffle(users)
        for user in list(dict.fromkeys(users))[:random.randrange(average - 20, average + 20)]:
            if bot.watch_users_reels(user):
                bot.logger.info("Stories viewed: %d" % (bot.total["stories_viewed"] - stories_viewed))

        bot.logger.info("New stories viewed: %d" % (bot.total["stories_viewed"] - stories_viewed_begin))

def unfollows():
    if your_turn(difficult = 3) and is_activate("unfollows"):
        print("unfollows")
        average = config['unfollows']['average'] if 'unfollows' in config and config['unfollows']['average'] else 5
        average = 2 if average < 2 else average

        seguidos = bot.following
        random.shuffle(seguidos)

        max_users = random.randrange(average - 2, average + 2)
        print("max_users: %d" % max_users)
        bot.unfollow_users(seguidos[:max_users])
        pass

def unlikes():
    if your_turn(difficult = 4) and is_activate("unlikes"):
        print("unlikes")
    pass

def is_sleeping():
    result = time.localtime(time.time())
    return result.tm_hour > 1 and result.tm_hour < 10

def check_config():
    if config is None:
        raise Exception("Config not found")
    if "username" not in config:
        raise Exception("username is not in config file")
    return True

def run_bot():
    if is_sleeping():
        print("Bot sleep")
        return

    print("Starting bot in thread %s" % threading.current_thread())
    
    follows()
    unfollows()
    view_ht_histories()
    view_my_following_histories()
    likes()
    unlikes()

    
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def init_bot():
    proxy = config['proxy']['url'] if 'proxy' in config and 'url' in config['proxy'] else None
    print(proxy)
    bot = instabot.Bot(filter_business_accounts=True,
        filter_verified_accounts=False,
        max_followers_to_follow=10000,
        max_following_to_follow=5000,
        filter_users_without_profile_photo=True,

    )
    bot.login(
        username=config['username'],
        proxy=proxy)
    
    return bot

def test():
    import json
    user_id = bot.get_user_id_from_username("robotina.services")

    users = bot.api.get_total_followers_or_followings(
        user_id=user_id,
        usernames=False,
        which='followings',
        to_file='followings.txt'
    )

    print("%d" % len(users))
    pass

def test2():
    bot.send_message("Holi", bot.get_user_id_from_username("julian.araya.r"))
    pass


config = []
with open("config.yaml") as file_config:
    config = yaml.full_load(file_config)

check_config()
bot = init_bot()

# Descomentar para probar directo
run_bot()
schedule.every(60).to(74).minutes.do(run_threaded, run_bot)

while 1:
    schedule.run_pending()
    time.sleep(1)