import numpy as np
import pandas as pd
import pickle
import warnings
warnings.filterwarnings(action='ignore')

# Data Preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder

# Model Training
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import tensorflow as tf

## Import necessary modules for collaborative filtering
from tensorflow.keras.layers import Input, Embedding, Dot, Flatten, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
#from wordcloud import WordCloud
from collections import defaultdict
from collections import Counter
## Import necessary modules for content-based filtering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from typing import List, Dict, Any
import json
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import random
import os
import time
from sklearn.metrics.pairwise import linear_kernel
from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import bold, code, italic, text
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram import F
from random import randint

import data_manager
import config
from llm import LLM
import data_manager
