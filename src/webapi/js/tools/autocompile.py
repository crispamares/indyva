#!/usr/bin/env python
#
# Usage:
#   ./autocompile.py path cmd
#
# Blocks monitoring |path| and its subdirectories for modifications on
# files ending with suffix |extk|. Run |cmd| each time a modification
# is detected. |cmd| is optional and defaults to 'make'.
#
# Example:
#   ./autocompile.py /my-latex-document-dir .tex,.bib "make pdf"
#
# Dependencies:
#   Linux, Python 2.6, Pyinotify
#
import subprocess
import sys
import pyinotify
import os

def recursive_dirs(path):
    dirs = [path]
    for root, sub_dirs, files in os.walk(path):
        for dir in sub_dirs:
            dirs.append(os.path.join(root,dir))
    return dirs


class OnWriteHandler(pyinotify.ProcessEvent):
    def my_init(self, cwd, extension, cmd):
        self.cwd = cwd
        self.extensions = extension.split(',')
        self.cmd = cmd

    def _run_cmd(self):
        print '==> Modification detected'
        subprocess.call(self.cmd.split(' '))

    def process_IN_MODIFY(self, event):
        if all(not event.pathname.endswith(ext) for ext in self.extensions):
            return
        self._run_cmd()

def auto_compile(path, extension, cmd):
    wm = pyinotify.WatchManager()

    handler = OnWriteHandler(cwd=path, extension=extension, cmd=cmd)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(path, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
    print '==> Start monitoring %s (type c^c to exit)' % path
    notifier.loop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "Command line error: missing argument(s)."
        sys.exit(1)

    # Required arguments
    path = sys.argv[1]
    extension = "js"

    # Optional argument
    cmd = 'make'
    if len(sys.argv) == 3:
        cmd = sys.argv[2]

    # Blocks monitoring
    auto_compile(path, extension, cmd)
