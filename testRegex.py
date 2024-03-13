import praw
import re
import secrets

numberMatcher = re.compile(r'\d+')
signMatcher = re.compile(r'(?:(?<=.{5}vz|.schild|zeichen)\W?(\d{3,4}[-]?\d{0,3}))', re.I)
lawMatcher = re.compile(r'§\d+')


def post_contains_sign(post):
    if signMatcher.search(post.title + '\n' + post.selftext):
        return True
    return False


def get_signs_from_post(post):
    signs = []
    for match in signMatcher.findall(post.title + '\n' + post.selftext):
        if match not in signs:
            signs.append(match)
    return signs


def process_comment(comment, indent=0):
    # print('  ' * indent + comment.body)

    signs = []
    if comment.author is not None and comment.author.name != "AutoModerator":
        for match in signMatcher.findall(comment.body):
            if match not in signs:
                signs.append(match)

    for reply in comment.replies:
        signs.extend(process_comment(reply, indent + 1))
    return signs


reddit = praw.Reddit(
        client_id=secrets.client_id,
        client_secret=secrets.client_secret,
        user_agent=secrets.user_agent,
        username=secrets.username,
        password=secrets.password,
    )

sub = reddit.subreddit("stvo")

singleComment = reddit.comment("jjkhl9v")
for sign in process_comment(singleComment):
    print("    Found VZ " + sign + " in comments")

#exit()
for post in sub.new(limit=5):
    print("Testing post " + post.id + ": " + post.url)
    for sign in get_signs_from_post(post):
        print("  Found VZ " + sign + " in original submission")
    post.comments.replace_more(limit=None)
    for comment in post.comments.list():
        #print("  Testing comment " + comment.id + ": https://reddit.com" + comment.permalink)
        for sign in process_comment(comment):
            print("    Found VZ " + sign + " in comments")
