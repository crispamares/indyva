# See the README for installation instructions.

JS_COMPILER = uglifyjs

JS_FILES = \
	scinfo.js \
	scinfo.bounded.js
all: \
	$(JS_FILES) \
	$(JS_FILES:.js=.min.js)

scinfo.bounded.js: \
	lib/lodash.js \
	lib/autobahn.js \
	scinfo.js

.INTERMEDIATE scinfo.js: \
	scinfo.core.js

scinfo.core.js: \
	src/start.js \
	src/core/core.js \
	src/core/connect.js \
	src/core/dataStore.js \
	src/end.js

%.min.js: %.js Makefile
	@rm -f $@
	$(JS_COMPILER) < $< > $@
	@chmod a-w $@

scinfo.%: Makefile
	@rm -f $@
	cat $(filter %.js,$^) > $@
	@chmod a-w $@

clean:
	rm -f scinfo*.js
