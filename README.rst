licorice
========

This program's aim is analysing files for licensing information, and presenting
this information to the user in a readable and concise way. It does a lot of
guessing, so it should not be taken as legal advice, and the author makes no
guarantees or claims of accuracy with respect to this program. Licorice may
make your licensing work easier, but it is ultimately your own responsibility
to check if what you do is in compliance with applicable licences and the law.

If you are reading this, you are looking at a very early prototype of a
rewritten version of licorice, which uses `python-Levenshtein` and `fuzzywuzzy`
for text matching. Using these libraries, licorice can reasonably quickly match
texts with non-trivial differences and output a numerical coefficient (0-100)
of similarity of such texts, so in theory, it should be much better at picking
up licences that the previous version didn't.

Tomas Radej, `<tradej@redhat.com>`
