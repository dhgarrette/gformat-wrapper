from __future__ import print_function

# Point this to your location of the jar downloaded from:
#   https://github.com/google/google-java-format/releases
formatter_jar = '/u/dhg/google-java-format-1.7-all-deps.jar'



import glob
import hashlib
from optparse import OptionParser
import os
import re
import subprocess
import sys

usage = """Exactly one of the following arguments must be specified:
  commit
    Formats all Java files modified since the last commit.
  branch [OTHER_BRANCH]
    Formats all Java files modified since diverging from OTHER_BRANCH.
    Defaults to 'origin/master'.
  all PATHS...
    Formats all Java files within (and below) the specified paths.

Examples:
  Format everything modified on this branch: gformat.py branch
  Format a single file: gformat.py all path/to/file.java
  Format everything within directory 'src': gformat.py all src"""
parser = OptionParser(usage=usage)
parser.add_option('-d', '--dryrun', action='store_true', dest='dryrun',
                  help='Show the files that would be formatted without actually modifying them.')
parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                  help='For debugging: Prints all of the git commands that are executed along with their results.')
(options, args) = parser.parse_args()

if not args:
  parser.print_help()
  exit()
elif args[0] == 'commit':
  assert(len(args) == 1)
elif args[0] == 'branch':
  assert(1 <= len(args) <= 2)
elif args[0] == 'all':
  assert(len(args) >= 1)
else:
  print('invalid argument: %s' % (' '.join(args[0])))
  parser.print_help()
  exit()


def generate_hash(filename):
  return hashlib.md5(open(filename, 'rb').read()).hexdigest()

def run_command(command_parts):
  return subprocess.check_output(command_parts, universal_newlines=True)

def run_git_command(command_line_args):
  result = run_command(['git'] + command_line_args)
  if options.verbose:
    print('$ git %s\n%s' % (' '.join(command_line_args), result))
  return result

def parse_porcelain(command_line_args):
  return_list = []
  for line in run_git_command(command_line_args).splitlines():
    split = line.strip().split()
    if len(split) == 2 and not (set(split[0]) - set(['M', 'A'])) and split[1].endswith('.java'):
      return_list.append(split[1])
  return return_list

def branch_name():
  for line in run_git_command(['branch']).splitlines():
    if line.startswith('*'):
      return line[1:].strip()
  assert False

def oldest_common_ancestor(branch1, branch2):
  revs1 = set(run_git_command(['rev-list', '--first-parent', branch1]).splitlines())
  revs2 = run_git_command(['rev-list', '--first-parent', branch2]).splitlines()
  for rev in revs2:
    if rev in revs1:
      return rev.strip()
  assert False


files_to_check = set()

if args[0] == 'commit':
  files_to_check.update(parse_porcelain(['status', '--porcelain']))

elif args[0] == 'branch':
  head_sha = run_git_command(['rev-parse', 'HEAD']).strip()
  prev_sha = oldest_common_ancestor(branch_name(), 'master' if len(args) == 1 else args[1])
  files_to_check.update(parse_porcelain(['diff', '--name-status', prev_sha, head_sha]))

elif args[0] == 'all':
  unglobbed = set()
  for arg in args[1:]:
    unglobbed.update(glob.glob(arg))
  if not unglobbed:
    unglobbed.add('.')
  if options.verbose:
    print('unglobbed:')
    for path in sorted(unglobbed):
      print('  %s' % (path))

  files_to_check.update(unglobbed)

  for path in sorted(unglobbed):
    for root, dirs, files in os.walk(path):
      if root == '.':
        dirs.remove('target')
      hidden_files = [d for d in dirs if d.startswith('.')]
      for h in hidden_files:
        dirs.remove(h)
      for f in files:
        files_to_check.add(os.path.join(root, f))


print('files_to_check:')
for path in sorted(files_to_check):
  print('  %s' % (path))

unchanged = []
changed = []

for filename in files_to_check:
  if not os.path.isfile(filename): continue
  if not filename.endswith('.java'): continue

  hash_before = generate_hash(filename)
  print('checking', filename)
  if options.dryrun:
    hash_after = hashlib.md5(run_command(['java', '-jar', formatter_jar, filename])).hexdigest()
  else:
    subprocess.call(['java', '-jar', formatter_jar, '--replace', filename])
    hash_after = generate_hash(filename)
  (unchanged if hash_before == hash_after else changed).append(filename)

print()
for (label, files) in [('Unchanged', unchanged),
                       ('Changed', changed)]:
  print(label, 'files'+(' (dry run)' if options.dryrun else '')+':')
  for filename in files:
    print('   ', filename)
  print()
