# This file is NOT licensed under the GPLv3, which is the license for the rest
# of YouCompleteMe.
#
# Here's the license text for this file:
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import os
import re
import shutil
import subprocess
import ycm_core

DIR_OF_THIS_SCRIPT = os.path.abspath(os.path.dirname(__file__))
SOURCE_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.c', '.m', '.mm']

# These are the compilation flags that will be used in case there's no
# compilation database set (by default, one is not set).
# CHANGE THIS LIST OF FLAGS. YES, THIS IS THE DROID YOU HAVE BEEN LOOKING FOR.
flags = [
    '-Wall',
    '-Wextra',
    # For a C project, you would set this to something like 'c99' instead of
    # 'c++11'.
    '-std=c99',
    # THIS IS IMPORTANT! Without the '-x' flag, Clang won't know which
    # language to use when compiling headers. So it will guess. Badly. So C++
    # headers will be compiled as C headers. You don't want that so ALWAYS
    # specify the '-x' flag. For a C project, you would set this to 'c'
    # instead of 'c++'.
    '-x', 'c',
    '-I', '.',
]


# Set this to the absolute path to the folder (NOT the file!) containing the
# compile_commands.json file to use that instead of 'flags'. See here for
# more details: http://clang.llvm.org/docs/JSONCompilationDatabase.html

# You can get CMake to generate this file for you by adding:
#   set( CMAKE_EXPORT_COMPILE_COMMANDS 1 )
# to your CMakeLists.txt file.
#
# Most projects will NOT need to set this to anything; you can just change the
# 'flags' list of compilation flags. Notice that YCM itself uses that approach.
compilation_database_folder = ''

if os.path.exists(compilation_database_folder):
    database = ycm_core.CompilationDatabase(compilation_database_folder)
else:
    database = None


def IsHeaderFile(filename):
    extension = os.path.splitext(filename)[1]
    return extension in ['.h', '.hxx', '.hpp', '.hh']


def FindCorrespondingSourceFile(filename):
    if IsHeaderFile(filename):
        basename = os.path.splitext(filename)[0]
        for extension in SOURCE_EXTENSIONS:
            replacement_file = basename + extension
            if os.path.exists(replacement_file):
                return replacement_file
    return filename


def LoadSystemIncludes():
    regex = re.compile(r'(?:\#include \<...\> search starts here\:)'
                       r'(?P<list>.*?)(?:End of search list)', re.DOTALL)
    if shutil.which('clang') is not None:
        cmd_args = ['clang', '-v', '-E', '-x', 'c++', '-']
    elif shutil.which('gcc') is not None:
        cmd_args = ['gcc', '-E', '-Wp,-v', '-x', 'c++', '-']
    else:
        return None
    process = subprocess.Popen(cmd_args, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_out, process_err = process.communicate('')
    output = process_out + process_err
    output = output.decode('utf-8')
    includes = []
    for p in regex.search(output).group('list').split('\n'):
        p = p.strip()
        if len(p) > 0 and p.find('(framework directory)') < 0:
            includes.append('-isystem')
            includes.append(p)
    return includes


def Settings(**kwargs):
    if kwargs['language'] == 'cfamily':
        # If the file is a header, try to find the corresponding source file
        # and retrieve its flags from the compilation database if using one.
        # This is necessary since compilation databases don't have entries
        # for header files. In addition, use this source file as the
        # translation unit. This makes it possible to jump from a declaration
        # in the header file to its definition in the corresponding source
        # file.
        filename = FindCorrespondingSourceFile(kwargs['filename'])

        final_flags = flags
        # Enable this if ycm uses incorrect system include paths
        # final_flags += LoadSystemIncludes()

        if not database:
            return {
                'flags': final_flags,
                'include_paths_relative_to_dir': DIR_OF_THIS_SCRIPT,
                'override_filename': filename
            }

        compilation_info = database.GetCompilationInfoForFile(filename)
        if not compilation_info.compiler_flags_:
            return {}

        # Bear in mind that compilation_info.compiler_flags_ does NOT return a
        # python list, but a "list-like" StringVec object.
        final_flags = list(compilation_info.compiler_flags_)

        return {
            'flags': final_flags,
            'include_paths_relative_to_dir':
                compilation_info.compiler_working_dir_,
            'override_filename': filename
        }
    return {}
