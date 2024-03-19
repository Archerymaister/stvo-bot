# StVO-Bot
This reddit bot manages the [StVO subreddit](https://www.reddit.com/r/StVO) and was created by u/Archerymaister.

# How it works
This code can only moderate one subreddit at a time. Based on the specified user credentials, the first moderated sub is picked to be moderated. If the user isn't a moderator in any subreddit, the code will exit.

The configuration is done via the subreddit wiki.

## Setup
The bot creates any needed wiki pages automatically. There might be adjustments needed for it to work as expected.

## Features
More features might be added in the future!

### Stickied replies
There can be different stickied reply texts based on the submissions flair. The configuration is done in the wiki page 'stvo_bot_stickies' and consists of repeating sections. One sections always starts with a comma separated list of submission flair ids surrounded by brackets. After this, the actual comment text follows in markdown format. This either ends when a new sections starts or the file ends.

```
(01234567-89aa-bbcc-ddee-ffffffffffff, 01234567-89aa-bbcc-ddee-ffffffffffff)
# Handy tip coming along!
A towel, it says, is about the most massively useful thing an interstellar hitchhiker can have.


(01234567-89aa-bbcc-ddee-ffffffffffff)
# Attention please!
Any markdown should be valid!
```