import praw
import re
import secrets


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


def wiki_page_exists(sub_wiki, wiki_page_name):
    for wiki_page in sub_wiki:
        if str(wiki_page.name) == str(wiki_page_name):
            return True
    return False


numberMatcher = re.compile(r'.*\d+.*')
signMatcher = re.compile(r'.*(?:(?<=.{5}vz|.schild|zeichen)\W?(\d{3,4}[-]?\d{0,3})).*')
lawMatcher = re.compile(r'§\d+')

wiki_page_sticky_comment = "sticky_comment"
wiki_page_sticky_comment_flairs = "sticky_comment_flairs"

if __name__ == "__main__":
    print("Starting bot...")

    reddit = praw.Reddit(
        client_id=secrets.client_id,
        client_secret=secrets.client_secret,
        user_agent=secrets.user_agent,
        username=secrets.username,
        password=secrets.password,
    )

    try:
        sub = next(reddit.user.moderator_subreddits(limit=None))
    except StopIteration:
        print("User does not moderate any subreddits! Exiting!")
        exit(1)

    print("Moderating community r/" + sub.display_name)

    wiki = sub.wiki

    if not wiki_page_exists(wiki, wiki_page_sticky_comment):
        print("Predefined comment does not exist!")
        exit(2)

    if not wiki_page_exists(wiki, wiki_page_sticky_comment_flairs):
        print("Flairs for sticky comment do not exist!")
        exit(3)

    whitelisted_flairs = []
    for line in wiki[wiki_page_sticky_comment_flairs].content_md.splitlines():
        if line.startswith("#"):
            continue
        whitelisted_flairs.append(line)

    for post in sub.stream.submissions(skip_existing=True):
        try:
            if post.link_flair_template_id not in whitelisted_flairs:
                print("Kein Kommentar!")
                continue
        except AttributeError:
            # When the post has no flair, an AttributeError is thrown. We just continue at this point.
            continue

        print("Kommentar!")
        reply = post.reply(wiki[wiki_page_sticky_comment].content_md)
        reply.mod.lock()
        reply.mod.distinguish(sticky=True)
