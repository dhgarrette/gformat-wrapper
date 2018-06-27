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

Exactly of the following arguments must be specified:

    commit
      Formats all Java files modified since the last commit.
        DEFAULT
    push
        Formats all Java files modified since the last push to the current branch.
    remote REPO BRANCH
        Formats all Java files modified since the last push to the given branch of
        the given repo. (E.g. `remote origin master`).
    all
        Formats all Java files below the current directory.

### Options

    --dryrun, -d
        Show the files that would be formatted without actually modifying them.
