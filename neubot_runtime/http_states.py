# Part of Neubot <https://neubot.nexacenter.org/>.
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.

''' HTTP states '''

(IDLE, BOUNDED, UNBOUNDED, CHUNK, CHUNK_END, FIRSTLINE,
 HEADER, CHUNK_LENGTH, TRAILER, ERROR) = range(0, 10)
