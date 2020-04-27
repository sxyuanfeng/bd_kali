from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import pymongo
import json
from pyecharts.charts import Map
from pyecharts import options as opts
import jieba
import re
import os


