# wordplanes

Are many of our word vectors actually expressible as planes in 2D space?

# Setup

`virtualenv .venv`

`. .venv/bin/activate`

`pip install -r requirements.txt`

At the moment, this next requires an Anthropic API key. I used Anthropic because I had some spare credits
that I wanted to use. It walks through wordnet looking for adjectives. Then it asks Claude-3-5-Haiku whether
each adjective could be a way of describing a person.

`python personalityadjectives.py`

That should have created a file called `personality_adjectives.sqlite`

You will need a copy of ollama and the `nomic-embed-text` model; you will also need an OpenAI api key.

`python createembeddings.py`

The CPU intensive part is this:

`python language_plane_finder.py`

You might want to capture information with `--output-directory` (which will create distribution images) and `--fitter`
(which will try to find the distribution most like it).
