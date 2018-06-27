# Point this to your location of the jar downloaded from:
#   https://github.com/google/google-java-format/releases
formatter_jar = '/Users/dhg/google-java-format-1.6-all-deps.jar'



import hashlib
from optparse import OptionParser
import os
import re
import subprocess
import sys

parser = OptionParser()
parser.add_option('-d', '--dryrun', action="store_true", dest="dryrun")
(options, args) = parser.parse_args()

if not args:
  args = ['commit']
elif args[0] == 'commit':
  assert(len(args) == 1)
elif args[0] == 'push':
  assert(len(args) == 1)
elif args[0] == 'remote':
  assert(len(args) == 3)
elif args[0] == 'all':
  assert(len(args) == 1)
else:
  assert('invalid argument')


def generate_hash(filename):
  return hashlib.md5(open(filename, 'rb').read()).hexdigest()

def parse_porcelain(command_line_args):
  return_list = []
  for line in subprocess.check_output(['git'] + command_line_args).splitlines():
    split = line.strip().split()
    if len(split) == 2 and not (set(split[0]) - set(['M', 'A'])) and split[1].endswith('.java'):
      return_list.append(split[1])
  return return_list


files_to_check = []

if args[0] == 'commit':
  files_to_check.extend(parse_porcelain(['status', '--porcelain']))

if args[0] == 'push':
  head_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
  branch_line, = [line.strip()
                      for line in subprocess.check_output(['git', 'branch', '-vv']).splitlines()
                      if line.startswith('*')]
  remote_branch = re.match(r'\*\s+\S+\s+[\da-f]{7} \[([^\]:]+)[\]:].*', branch_line).group(1)
  remote_sha = subprocess.check_output(['git', 'rev-parse', remote_branch]).strip()
  files_to_check.extend(parse_porcelain(['diff', '--name-status', head_sha, remote_sha]))

if args[0] == 'remote':
  head_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
  remote_branch = '/'.join(args[1:3])
  remote_sha = subprocess.check_output(['git', 'rev-parse', remote_branch]).strip()
  files_to_check.extend(parse_porcelain(['diff', '--name-status', head_sha, remote_sha]))

if args[0] == 'all':
  for root, dirs, files in os.walk('.'):
    if root == '.':
      dirs.remove('target')
    hidden_files = [d for d in dirs if d.startswith('.')]
    for h in hidden_files:
      dirs.remove(h)

    for f in files:
      if f.endswith('.java'):
        files_to_check.append(os.path.join(root, f))


unchanged = []
changed = []

for filename in files_to_check:
  if not os.path.isfile(filename): continue

  hash_before = generate_hash(filename)
  print 'checking', filename
  if options.dryrun:
    hash_after = hashlib.md5(subprocess.check_output(['java', '-jar', formatter_jar, filename])).hexdigest()
  else:
    subprocess.call(['java', '-jar', formatter_jar, '--replace', filename])
    hash_after = generate_hash(filename)
  (unchanged if hash_before == hash_after else changed).append(filename)

print ''
for (label, files) in [('Unchanged', unchanged),
                       ('Changed', changed)]:
  print label, 'files'+(' (dry run)' if options.dryrun else '')+':'
  for filename in files:
    print '   ', filename
  print ''
