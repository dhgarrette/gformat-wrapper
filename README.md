# gformat-wrapper

A git-aware wrapper for the google code formatter.

## Setup

Download the google Java formatter from

https://github.com/google/google-java-format/releases

(You will need the "all-deps" version.)

Set its location as the `formatter_jar` variable at the top of the script file.

### Optional

Add the following to your `~/.bash_profile`:

    alias gformat="python path/to/gformat.py"

Then you can just do, e.g., `gformat push`

## Usage

Download this file and run it with:

    python gformat.py OPTIONS

where the `OPTIONS` are what's below.

### Arguments

Exactly one of the following arguments must be specified:

    commit
      Formats all Java files modified since the last commit.
    branch [OTHER_BRANCH]
      Formats all Java files modified since diverging from OTHER_BRANCH.
      Defaults to 'origin/master'.
    all PATHS...
      Formats all Java files within (and below) the specified paths.

### Options

    --dryrun, -d
        Show the files that would be formatted without actually modifying them.

### Examples

Format everything modified on this branch: `gformat.py branch`

Format a single file: `gformat.py all path/to/file.java`

Format everything within directory 'src': `gformat.py all src`
