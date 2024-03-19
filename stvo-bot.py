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


def load_comments():
    current_flairs = []
    current_comment_md = ""

    for text_line in wiki[wiki_page_sticky_comment].content_md.splitlines():
        if text_line.strip() == '':
            continue

        if flair_match_line.match(text_line):
            store_comment(current_comment_md, current_flairs)

            current_flairs.clear()
            current_comment_md = ""

            for match in flair_match_ids.findall(text_line):
                current_flairs.append(match)
            continue

        current_comment_md += text_line + "\n"

    store_comment(current_comment_md, current_flairs)


def store_comment(current_comment_md, current_flairs):
    for flair_id in current_flairs:
        predefined_comments[flair_id] = current_comment_md


def check_for_new_wiki_revision(wiki):
    global last_revision_check
    latest_revision = next(wiki[wiki_page_sticky_comment].revisions())
    if latest_revision.revision_date > last_revision_check:
        last_revision_check = latest_revision.revision_date
        predefined_comments.clear()
        load_comments()

def get_file_contents(filename):
    with open(filename, "r") as file:
        return file.read()


numberMatcher = re.compile(r'.*\d+.*')
signMatcher = re.compile(r'.*(?:(?<=.{5}vz|.schild|zeichen)\W?(\d{3,4}[-]?\d{0,3})).*')
lawMatcher = re.compile(r'§\d+')

flair_match_line = re.compile(r'\(((?:[0-9a-f-]{36}[, ]{0,2})+)\)')
flair_match_ids = re.compile(r'[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}')

wiki_page_sticky_comment = "stvo_bot_stickies"

predefined_comments = dict()

last_revision_check = 0

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
        print("Predefined comments page does not exist! Creating it. Please edit it.")
        wiki.create(name=wiki_page_sticky_comment, content=get_file_contents("comment_preset.txt"),
                    reason="Automatically created by u/StVO-Bot")

    latest_revision = wiki[wiki_page_sticky_comment]
    if latest_revision.revision_date > last_revision_check:
        last_revision_check = latest_revision.revision_date
        load_comments()

    for post in sub.stream.submissions(skip_existing=True):
        # check for updated wiki
        latest_revision = wiki[wiki_page_sticky_comment]
        if latest_revision.revision_date > last_revision_check:
            last_revision_check = latest_revision.revision_date
            load_comments()
            print("Comments updated!")

        try:
            if post.link_flair_template_id not in predefined_comments:
                continue
        except AttributeError:
            # When the post has no flair, an AttributeError is thrown. We just continue at this point.
            continue

        reply = post.reply(predefined_comments[post.link_flair_template_id])
        reply.mod.lock()
        reply.mod.distinguish(sticky=True)
