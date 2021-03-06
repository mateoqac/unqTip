import sys
import os
import os.path
import importlib
import inspect
from test_logger import log
from test_utils import read_file_lines, is_module, parent_dir, module_dir, run_cmd, delete_files_in_dir, dir_has_tests
import autotests

def cleanup():
    clean_dir = os.path.join(parent_dir(__file__), "examples")
    delete_files_in_dir(clean_dir, ["README"])

def run_gobstones(filename, board_file):    
    result = os.popen("./run_gobstones.sh %s %s" % (filename, board_file)).read()        
    result = result.split('\n')
    while len(result) > 0 and result[-1] == '': result = result[:-1]
    if len(result) == 0 or result[-1] != 'OK':
        log("\n".join(result))
        return 'ERROR', {}
    else:
        result = result[:-1]
        dic = []
        var, val = "", ""
        for res in result:
            if res.count("->") > 0:
                dic.append((var.strip(' \t\r\n'), val.strip(' \t\r\n')))
                var, val = res.split('->')                
            else:
                val += "\n" + res
        dic.append((var.strip(' \t\r\n'), val.strip(' \t\r\n')))
        if len(dic) > 1:
            dic = dic[1:]
        else:
            dic = []
        return 'OK', dic

class TestException(Exception):
    pass


class AnnotationException(TestException):
    pass


class AnnotationBuilder(object):
    
    def build(self, s):        
        self.check_malformed(s)
        splitted = s.split(Annotation.ANNOTATION_SEQ)[1].split("=")
        if len(splitted) == 1:
            return Annotation(splitted[0])
        else:
            return Annotation(splitted[0], splitted[1])        
        
    def check_malformed(self, s):
        if not s.startswith(Annotation.ANNOTATION_SEQ):
            raise AnnotationException() 


class Annotation(object):

    ANNOTATION_SEQ = "#!"
    
    def __init__(self, key, value=None):
        self.key = key
        self.value = value


class GobstonesTest(object):
    pass


class GobstonesFileTest(object):
    
    def __init__(self, filename):
        lines = read_file_lines(filename)
        self.filename = filename
        self.annotations, self.code = self.extract_annotations(lines)    
    
    def name(self):
        return self.filename
    
    def extract_annotations(self, lines):
        annotations = {}
        code = []
        for l in lines:
            if Annotation.ANNOTATION_SEQ in l.strip():
                annotation = AnnotationBuilder().build(l.strip())
                annotations.update({annotation.key:annotation})
            else:
                code.append(l)
        return (annotations, code)
    
    def annotation_present(self, annotation_name):
        return annotation_name in self.annotations.keys()
    
    def check_assert(self, results):
        passed = 0
        failed = 0
        for res in results:
            if res[1] == "True":
                passed += 1
            elif res[1] ==  "False":
                failed += 1
        return passed, failed
    
    def run(self):
        if "board" in self.annotations.keys():
            if not self.annotations["board"].value is None:
                board = os.path.join(module_dir(self), self.annotations["board"].value)
            else:
                board = os.path.join(module_dir(self), self.filename[:-4] + ".gbb") 
        else:
            board = os.path.join(parent_dir(__file__), "boards/empty.gbb")
        results = run_gobstones(self.filename, board)
        if results[0] == "OK":            
            if self.annotation_present("assert"):
                passed, failed = self.check_assert(results[1])
            else:
                res = dict(results[1])
                passed, failed = int(res["passed"]), int(res["failed"]) 
            
            return (passed, failed, 0, passed + failed)
        else:
            return (0, 0, 1, 1)
        
        def check_assert(self, results):
            pass
                   
def sum_tuples(a,b): return tuple(map(lambda (x,y): x+y, zip(a,b)))
                    
                
class TestCase(object):
    
    def __init__(self, testcase_name):
        self.name = testcase_name
        self.passed = 0
        self.failed = 0
        self.errors = 0    
        self.result = (0, 0, 0, 0)

    def __repr__(self):
        output = "TestCase: %s, " % self.name
        if self.errors > 0:
            output += "ERROR."
        elif self.failed > 0:
            output += "FAILED."
        else:
            output += "OK."
        return output + " (passed: %s, failed: %s, errors: %s, total: %s)" % self.result
    
    def run(self):
        tests = self.get_gobstones_tests()
        for test in tests:
            self.setup()
            self.result = sum_tuples(self.result, test.run())
            if self.result[1] > 0:
                print "Failed test '%s'" % (test.name(),)
            if self.result[2] > 0:
                print "Error while running test '%s'" % (test.name(),) 
            self.teardown()
        
        self.passed = self.result[0]
        self.failed = self.result[1]
        self.error = self.result[2]
        self.total = self.result[3]

    def setup(self):
        pass
        
    def teardown(self):
        pass

class FileTestCase(TestCase):
        
    def get_gobstones_tests(self):
        PATH = os.path.join(parent_dir(__file__), self.name)
        return [ GobstonesFileTest(os.path.join(PATH, f)) for f in os.listdir(PATH) if ".gbs" in f and self.is_test_file(PATH, f)]        
    
    def is_test_file(self, path, filename):
        return os.path.isfile(os.path.join(path, filename)) and filename.startswith("test")
            

class Tester(object):
    
    def test(self):
        test_cases = self.get_test_cases()
        
        passed = 0
        failed = 0
        errors = 0
        total = 0
        for test_case in test_cases:
            test_case.run()
            print repr(test_case)
            passed += test_case.passed
            failed += test_case.failed
            errors += test_case.errors
            total += test_case.total
            
        print "Total:\n--passed: %s\n--failed: %s\n--errors: %s\n--count: %s\n" % (passed, failed, errors, total)
        cleanup()
        
    def get_test_cases(self):
        return self.get_file_test_cases() + [autotests.AutoTestCase()]
        
    def get_file_test_cases(self):
        PATH = os.path.split(os.path.realpath(__file__))[0]
        return [self.get_module_testcase(f) for f in os.listdir(PATH) if not os.path.isfile(os.path.join(PATH, f)) and is_module(f) and dir_has_tests(f)]

    def get_module_testcase(self, m):
        return FileTestCase(m)
#         module = importlib.import_module(m)
#         for name, obj in inspect.getmembers(module):
#             if inspect.isclass(obj) and issubclass(obj, TestCase):
#                 return obj

if __name__ == "__main__":
    Tester().test()            