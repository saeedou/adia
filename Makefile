PIP = pip3
TEST_DIR = tests
PRJ = dial
PYTEST_FLAGS = -v


.PHONY: test
test:
	pytest $(PYTEST_FLAGS) $(TEST_DIR)

.PHONY: cover
cover:
	pytest $(PYTEST_FLAGS) --cov=$(PRJ) $(TEST_DIR)

.PHONY: lint
lint:
	pylama

.PHONY: env
env:
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .


# WWW

WWW = www
WWWDIST = $(shell readlink -f $(WWW)/build)
DIAL = dial

$(WWWDIST)/dial.js:
	brython pack \
		--package-directory $(DIAL) \
		--output-directory $(WWWDIST) \
		dial
	
$(WWWDIST)/stdlib.min.js:
	- mkdir -p $(WWWDIST)
	brython pack-dependencies \
		--output-directory $(WWWDIST) \
		--search-directory $(DIAL) \
		--stdlib-directory $(WWW) \
		--filename stdlib.min.js

$(WWWDIST)/stdlib.full.js:
	- cp $(WWW)/brython_stdlib.js $(WWWDIST)/stdlib.full.js

.PHONY: www
www: $(WWWDIST)/stdlib.min.js $(WWWDIST)/dial.js
	- cp $(WWW)/brython.js $(WWWDIST)/runtime.js
	- ln -s $(shell readlink -f $(WWW))/main.html $(WWWDIST)/index.html

.PHONY: serve
serve: www
	brython -C$(WWWDIST) serve

.PHONY: clear
clean::
	- rm \
		$(WWWDIST)/runtime.js \
		$(WWWDIST)/stdlib.*.js \
		$(WWWDIST)/dial.js \
		$(WWWDIST)/index.html
