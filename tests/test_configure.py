# Run these tests with 'nosetests':
#   install the 'python-nose' package (Fedora/CentOS or Ubuntu)
#   run 'nosetests' in the root of the repository

from cStringIO import StringIO
import glob
import os
import sys
import unittest
from mock import patch

import configure

class BasicTests(unittest.TestCase):
    def test_rewrite_to_distfiles(self):
        res = configure.rewrite_to_distfiles("http://github.com/xenserver/planex") 
	assert res == "file:///distfiles/ocaml2/planex"

    # Decorators are applied bottom up
    @patch('os.path.exists') 
    @patch('configure.call') # We are patching subprocess.call, but because it is imported into configure we must call patch with configure.call
    def test_fetch_url(self, mock_subprocess_call, mock_os_path_exists):
        url = "https://github.com/mirage/ocaml-cohttp/archive/ocaml-cohttp-0.9.8/ocaml-cohttp-0.9.8.tar.gz"
	mock_os_path_exists.return_value = False
	mock_subprocess_call.return_value = 0
        configure.fetch_url(url)
	assert mock_os_path_exists.called
        mock_subprocess_call.assert_called_with(["curl", "-k", "-L", "-o", "planex-build-root/SOURCES/ocaml-cohttp-0.9.8.tar.gz", url])
        
    # Decorators are applied bottom up
    @patch('os.path.exists') 
    @patch('configure.call') 
    def test_fetch_url_existing_file(self, mock_subprocess_call, mock_os_path_exists):
        url = "https://github.com/mirage/ocaml-cohttp/archive/ocaml-cohttp-0.9.8/ocaml-cohttp-0.9.8.tar.gz"
	mock_os_path_exists.return_value = True
	mock_subprocess_call.return_value = 0
        configure.fetch_url(url)
        mock_os_path_exists.assert_called_with("planex-build-root/SOURCES/ocaml-cohttp-0.9.8.tar.gz")
	assert not mock_subprocess_call.called
        
    # Decorators are applied bottom up
    @patch('os.path.exists') 
    @patch('configure.call') 
    def test_fetch_url_with_rewrite(self, mock_subprocess_call, mock_os_path_exists):
        def rewrite(url):
            return "http://rewritten.com/file.tar.gz"

        url = "https://github.com/mirage/ocaml-cohttp/archive/ocaml-cohttp-0.9.8/ocaml-cohttp-0.9.8.tar.gz"
	mock_os_path_exists.return_value = False
	mock_subprocess_call.return_value = 0
        configure.fetch_url(url, rewrite=rewrite)
        mock_os_path_exists.assert_called_with("planex-build-root/SOURCES/file.tar.gz")
        mock_subprocess_call.assert_called_with(["curl", "-k", "-L", "-o", "planex-build-root/SOURCES/file.tar.gz", "http://rewritten.com/file.tar.gz"])
        

    def test_make_extended_git_url(self):
	base_url = "https://github.com/xenserver/planex"
        res = configure.make_extended_git_url(base_url, "1.0.0")
	assert res == "https://github.com/xenserver/planex#1.0.0/%{name}-%{version}.tar.gz"

    # We don't handle 'v1.0.0'

    def test_parse_extended_git_url(self):
	url = "git://github.com/xenserver/planex#1.0.0/%{name}-%{version}.tar.gz"
        res = configure.parse_extended_git_url(url)
	assert res == ("git", "github.com", "/xenserver/planex", "1.0.0", 
                       "%{name}-%{version}.tar.gz")
    
    def test_make_and_parse_extended_git_url(self):
	base_url = "git://github.com/xenserver/planex"
        url = configure.make_extended_git_url(base_url, "1.0.0")
        res = configure.parse_extended_git_url(url)
	assert res == ("git", "github.com", "/xenserver/planex", "1.0.0", 
                       "%{name}-%{version}.tar.gz")
    
    def test_name_from_spec(self):
        res = configure.name_from_spec("tests/data/ocaml-cohttp.spec")
        assert res == "ocaml-cohttp"

    def test_check_spec_name(self):
	# check_spec_name does not exit if the name is correct
        configure.check_spec_name("tests/data/ocaml-cohttp.spec")

    def test_check_spec_name_fail(self):
	# check_spec_name exits if the name is not correct
        # self.assertRaises(SystemExit, configure.check_spec_name("tests/data/bad-name.spec"))
        try:
           configure.check_spec_name("tests/data/bad-name.spec")
           self.fail()
        except SystemExit:
           pass

    def test_sources_from_spec(self):
	res = configure.sources_from_spec("tests/data/ocaml-cohttp.spec")
        assert sorted(res) == sorted(["https://github.com/mirage/ocaml-cohttp/archive/ocaml-cohttp-0.9.8/ocaml-cohttp-0.9.8.tar.gz"])

