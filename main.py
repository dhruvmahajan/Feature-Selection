#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import cgi
import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import memcache

token_key = ndb.Key('token', 'default_token')

class Token(ndb.Model):
  word = ndb.StringProperty()
  span_doc_count = ndb.IntegerProperty()
  legitimate_doc_count = ndb.IntegerProperty()
  total_count = ndb.IntegerProperty()


class MainPage(webapp2.RequestHandler):
  def get(self):
    tokens = ndb.gql('SELECT * FROM Token WHERE ANCESTOR IS :1 ', token_key)

    self.response.out.write('<html><body>')

    for token in tokens:
      self.response.out.write(token.word.encode('ascii')+"\n")
      self.response.out.write(token.span_doc_count)
      self.response.out.write("\n")
      self.response.out.write(token.legitimate_doc_count)
      self.response.out.write("\n")
      self.response.out.write(token.total_count)
      self.response.out.write("<br>")


class dell(webapp2.RequestHandler):
  def get(self):
    tokens = ndb.gql('SELECT * FROM Token WHERE ANCESTOR IS :1  ', token_key)
    for token in tokens:
      token.key.delete()
    self.response.out.write('deleted')

class test(webapp2.RequestHandler):
  def get(self):
    import os
    f = open("test_spam.txt", 'r')
    words = f.read().split()
    prob_dict_spam={}
    prob_dict_legitimate={}

    total = ndb.gql('SELECT * FROM Token WHERE ANCESTOR IS :1', token_key)
    c=0
    for t in total:
    	c+=1
    # print c, "total"

    p_spam = 0
    p_legitimate = 0

    for word in words:
	    if word.isalpha():
	    	tokens = ndb.gql('SELECT * FROM Token WHERE  word = :2 AND ANCESTOR IS :1  ', token_key, word )
	    	for token in tokens:
		    	p_spam = p_spam + float(token.span_doc_count+1)/(c+token.total_count)
		    	p_legitimate = p_legitimate + float(token.legitimate_doc_count +1)/(c+token.total_count)

	      
    f.close()
    print p_legitimate, "legitimate"
    print p_spam, "Spam"

class reset(webapp2.RequestHandler):
  def get(self):
    tokens = ndb.gql('SELECT * FROM Token WHERE ANCESTOR IS :1', token_key)
    for token in tokens:
      token.key.delete()
    import os
    src_dir=os.getcwd()+'/spam'	

    N = len(os.listdir(src_dir))

    tokens={}
    spam_tokens={}
    legitimate_tokens={}

    for filename in os.listdir(src_dir):
      filename = os.path.join(src_dir, filename)
      f = open(filename, 'r')
      words = f.read().split()
      for word in words:
        if word.isalpha():
          if word in tokens:
            tokens[word]+=1
          else:
            tokens[word]=1  

          if word in spam_tokens:
            spam_tokens[word]+=1
          else:
            spam_tokens[word]=1
      f.close()


    src_dir=os.getcwd()+'/legitimate'

    N = len(os.listdir(src_dir))

    for filename in os.listdir(src_dir):
      filename = os.path.join(src_dir, filename)
      f = open(filename, 'r');
      words = f.read().split()
      for word in words:
        if word.isalpha():
          if word in tokens:
            tokens[word]+=1
          else:
            tokens[word]=1  

          if word in legitimate_tokens:
            legitimate_tokens[word]+=1
          else:
            legitimate_tokens[word]=1
      f.close()


    for key, value in tokens.items():
      token = Token(parent=token_key)
      token.word=key
      token.total_count=value
      if key in legitimate_tokens:
        token.legitimate_doc_count=legitimate_tokens[key]
      else:
        token.legitimate_doc_count=0

      if key in spam_tokens:
        token.span_doc_count=spam_tokens[key]
      else:
        token.span_doc_count=0
      token.put()

    self.response.out.write('Done reset')

    


app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/reset', reset),
  ('/dell', dell),
  ('/test', test)
], debug=True)
