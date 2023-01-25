.PHONY: style
style:
	black --target-version=py311 \
	      --line-length=120 \
		  --skip-string-normalization \
		  theme testapp setup.py

.PHONY: style_check
style_check:
	black --target-version=py311 \
	      --line-length=120 \
		  --skip-string-normalization \
		  --check \
		  theme testapp setup.py

test:
	testapp/manage.py test $${TEST_ARGS:-testapp}

coverage:
	PYTHONPATH="testapp" \
		python -b -W always -m coverage run testapp/manage.py test $${TEST_ARGS:-testapp}
	coverage report
