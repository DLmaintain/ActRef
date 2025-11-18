# ActRef
This is the replication package of paper "ActRef: Enhancing the Understanding of Python Code Refactoring with Action-Based Analysis"

## Requirements
- python = 3.8
- GumTree <https://figshare.com/s/984c7a39266137e29c37>
- Jpype1
- difflib
- JDK >= 15
  
## Usage
1. Please download the 'commits.zip' and 'gumtree.jar' from Figshare<https://figshare.com/s/984c7a39266137e29c37>
2. Unzip 'commits.zip' and put 'gumtree.jar' into 'lib/'
3. Prepare pythonparser:
     - cd pythonparser
     - pip install -r requirement.txt
     - cp pythonparser /tmp
     - PATH=$PATH:/tmp
4. Run main.py

## Notice
ActRef requires the 'Before' and 'After' files, which have been modified during a commit, we offer all the commits used in our experiment, if you want to detect other commits, please add them into the 'commits/' directory.
The result will be saved as 'results.csv', consist of SHA, refactoring operation name, refactored element name, changed element name, old element type, old element location, old module location, and new module location.

