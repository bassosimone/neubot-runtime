# Neubot runtime (deprecated)

[![Build Status](https://travis-ci.org/neubot/neubot-runtime.svg?branch=master)](https://travis-ci.org/neubot/neubot-runtime) [![Coverage Status](https://coveralls.io/repos/neubot/neubot-runtime/badge.svg?branch=master&service=github)](https://coveralls.io/github/neubot/neubot-runtime?branch=master)

Neubot is a piece of software to measure internet performance from the
edges developed at the Nexa Center for Internet & Society, a research center
at the Dept. of Computer and Control Engineering at Politecnico di Torino.

This repository contains neubot-runtime. It is the runtime library containing
functions shared by Neubot client and server programs.

## Status of this repository

The `stable` branch contains the code that is actually used by
neubot-server and that can possibly be used also by neubot. The `master`
branch contains some improvements over `stable` but I doubt they
will ever be included in `neubot-server` or `neubot` because we're
starting to write stuff in Go (especially in the backend).

This explains why this repository is deprecated.
