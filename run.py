import unittest
# from lib.HTMLTestReportCN import HTMLTestRunner
from config import config as cf
from lib.send_email import send_email
import pickle
import sys
from test.suite.test_suites import *
import time
from lib.HTMLTestRunner_PY3 import HTMLTestRunner


def discover():
    return unittest.defaultTestLoader.discover(cf.test_case_path)


def save_failures(result, file):
    suite = unittest.TestSuite()
    for case_result in result.failures:
        suite.addTest(case_result[0])

    with open(file, 'wb') as f:
        pickle.dump(suite, f)


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


def makesuite_by_testlist(testlist_file):

    with open(testlist_file) as f:
        testlist = f.readlines()

    testlist = [i.strip() for i in testlist if not i.startswith("#")]

    suite = unittest.TestSuite()
    all_cases = collect()
    for case in all_cases:
        if case._testMethodName in testlist:
            suite.addTest(case)
    return suite


def makesuite_by_tag(tag):
    suite = unittest.TestSuite()
    for case in collect():
        if case._testMethodDoc and tag in case._testMethodDoc:
            suite.addTest(case)

    return suite


# @threads(3)
def run(suite):
    cf.logging.info("================================== 测试开始 ==================================")

    with open(cf.report_file, 'wb') as f:  # 从配置文件中读取
        result = HTMLTestRunner(stream=f, title="Api Test", description="测试描述").run(suite)

    if result.failures:
        save_failures(result, cf.last_fails_file)

    if cf.send_email_after_run:
        send_email(cf.report_file)  # 从配置文件中读取
    cf.logging.info("================================== 测试结束 ==================================")
    # c_suite = testtools.ConcurrentStreamTestSuite(lambda: ((case, None) for case in suite))
    # r=c_suite.run(testtools.StreamResult())
    # print(testtools.StreamResult())
    # unittest.TextTestRunner(verbosity=2).run(suite)
    # runner = unittest.TextTestRunner()
    # from concurrencytest import ConcurrentTestSuite, fork_for_tests
    #
    # concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests(4))
    # runner.run(concurrent_suite)


def collect_only():
    t0 = time.time()
    i = 0
    for case in collect():
        i += 1
        print("{}.{}".format(str(i), case.id()))
    print("----------------------------------------------------------------------")
    print("Collect {} tests is {:.3f}s".format(str(i),time.time()-t0))


def run_all():
    run(discover())


def run_suite(suite_name):
    suite = get_suite(suite_name)
    if isinstance(suite, unittest.TestSuite):
        run(suite)
    else:
        print("TestSuite不存在")


def run_by_testlist():
    run(makesuite_by_testlist(cf.testlist_file))


def run_by_tag(tag):
    run(makesuite_by_tag(tag))


def rerun_fails():
    sys.path.append(cf.test_case_path)
    with open(cf.last_fails_file, 'rb') as f:
        suite = pickle.load(f)
    run(suite)


def main():
    if cf.options.collect_only:
        collect_only()
    elif cf.options.rerun_fails:
        rerun_fails()
    elif cf.options.testlist:
        run(makesuite_by_testlist(cf.testlist_file))
    elif cf.options.testsuite:
        run_suite(cf.options.testsuite)
    elif cf.options.tag:
        run(makesuite_by_tag(cf.options.tag))
    else:
        run_all()


if __name__ == '__main__':
    main()
