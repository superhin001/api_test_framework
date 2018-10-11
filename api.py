# coding:utf-8
from flask import Flask, render_template, request, redirect, url_for
import logging
import unittest

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


def discover():
    return unittest.defaultTestLoader.discover("test/case")


def collect():
    suite = unittest.TestSuite()

    def _collect(tests):
        if isinstance(tests, unittest.TestSuite):
            if tests.countTestCases() != 0:
                for i in tests:
                    _collect(i)
        else:
            suite.addTest(tests)

    _collect(discover())
    return suite


@app.route("/tests", methods=["GET", "POST"])
def get_tests():
    tests = []

    for case in collect():
        tests.append(case.id())

    if request.method == "POST":
        cases = request.form.getlist("cases")
        suite = unittest.defaultTestLoader.loadTestsFromNames(cases)
        unittest.TextTestRunner(verbosity=2).run(suite)

    return render_template('app.html', tests=tests)


if __name__ == '__main__':
    app.run(port="5005", debug=True)

