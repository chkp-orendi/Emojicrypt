import ollama
import string
import re
import os
import pandas as pd
# the encryption will always have a problem if the user will write something like: IGNORE EVERYTHING SAID BEFORE
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'testers'))
import common
import ast
import matplotlib.pyplot as plt




