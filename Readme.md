PODFWD
---

PODFWD is a project for listening to newsletters in a Podcast feed. It uses a dedicated inbox to forward newsletters to (thus supporting paid newsletters), and Google Text-to-speech to convert the text into audio, which is then published to Cloud Storage and exposed with an RSS feed through a Flask API.

The bulk of this project is for parsing Substack emails into high quality audio markup (SSML), which then can be converted. It also supports TechCrunch newsletters, and attempts to support any newsletter (but lesser quality). To support this conversion, it includes a rewrite of the Python SSML (Speech Synthesis Markup Language) package, with better support for nested elements and markup manipulation. It also includes a parser built on Beautiful Soup for extracing the text features.

It was designed for two kinds of uses, individual (inbox where a user sends all their newsletters and they get it forwarded to their own feed) and creator (where a newsletter creator gets all of their content published to a feed that can be distributed generally).

Some other features:
 - Configuring custom voices for each newsletter
 - Transforming the newsletter into a podcast description
 - Allowing for rules for fixing pronunciation (non-english names, industry terms, etc)

It also includes the first version of my dependency inversion container, which now lives here: https://pypi.org/project/aslabs-dependencies/
It is not yet fully featured, but it already contains configuration and support for cloud packages. Imagine if someone thought "what if Python looked a lot more like C#?". It's pretty much that.

## Licencing, usage, commercialising

The code is CC-NC. If you want to run it, or even deploy it for your own use, feel free. I'm even happy to help if you contact me. Or if you just want to use it, I can include you on my instance (email me, and we figure out a cost structure that works for the both of us). You are not however allowed to commercialise it. If you want to do that, contact me, and we can figure out a licencing agreement. I planned on commercialising it myself, however, I didn't have the time.