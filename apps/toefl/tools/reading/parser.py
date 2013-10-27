#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import sys
import re

from string import Template


class Question:
  def __init__(self):
    self.description = ""
    self.options = []
    self.answercount = 1
    self.paragraphs = []

  def post_process(self):
    # paragraph 5
    # paragraph 5 and 6
    # paragraph 5 and paragraph 6
    m = re.search('paragraph (\d+)\.*( and( paragraph)? )?(\d+)?', self.description.lower())
    if m:
      self.add_paragraph(m.group(1))
      self.add_paragraph(m.group(4))
    self.paragraphs.sort()
  
  def add_paragraph(self, p):
    if not p: return
    p = int(p)
    if p not in self.paragraphs: self.paragraphs.append(p)

class Article:

  def __init__(self):
    self.name = ""
    self.title = ""
    self.paragraphs = []
    self.questions = []

  def post_process(self):
    for i in xrange(len(self.questions)):
      q = self.questions[i]
      q.post_process()
      if i > 0 and len(q.paragraphs) == 0:
        q.paragraphs = self.questions[i - 1].paragraphs

def output(articles):
  value_index = ['X', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
  paragraph_template = Template('<p>$paragraph</p>\n')
  question_des_template = Template('<span class="description">$description</span>\n')
  option_template = Template('''
   <li class="choice">
      <input type="radio" name="$name" value="$value">
        $option
      </input>
    </li>''')
  options_template = Template('''<ul>$options\n</ul>\n\n''')
  for article in articles:
    with open("reading_" + article.name, "w") as output_file:
      output_file.write(article.title + '\n')
      for paragraph in article.paragraphs:
        output_file.write(paragraph_template.substitute(paragraph = paragraph))

    with open('reading_question_' + article.name, "w") as output_file:
      for question in article.questions:
        output_file.write(question_des_template.substitute(description = question.description))
        options = '';
        answerid = 0;
        for option in question.options:
          answerid = answerid + 1
          options = options + option_template.substitute(option = option, name = 'answer-' + str(answerid), value = value_index[answerid])
        output_file.write(options_template.substitute(options = options))
        

def main(filename):
  article = None
  question = None
  articles = []
  state = "init"
  paragraphs = []
  with open(filename) as input_file:
    for line in input_file.readlines():
      line = line.strip().replace('．', '. ') 
        
      if  re.match('TPO\d+-\d:?', line, re.IGNORECASE):
        if article:
          if question:
            article.questions.append(question)
            question = None
          articles.append(article)
        article = Article()
        article.name = line.replace(':', '').lower()
        state = 'name'
      elif state == 'name':
        article.title = line
        state = 'title'
      elif (line.startswith('○') or line.startswith('O') and len(line) > 4) and state in ['question', 'option', 'ignore']:
        state = 'option'
        question.options.append(line)
      elif '●' in line or ('O ' in line and len(line) < 4):
        question.answercount = question.answercount + 1
      elif 'Look at the four squares' in line and state in ['option', 'ignore', 'paragraph']:
        state = 'intertion-1'
        if question:
          article.questions.append(question)
        question = Question()
        question.paragraphs = paragraphs
        paragraphs = []
        question.description = line
      elif state == 'intertion-1':
        state = 'intertion-2'
        question.description = question.description + line
      elif state == 'intertion-2':
        state = 'option'
        question.description = question.description + line
      elif re.match('Paragraph \d+.*', line):
        state = "ignore"
        paragraphs.append(int(re.search('Paragraph (\d+).*', line).group(1)))
      elif line.isspace():
        state = "ignore"
      elif re.match('\d+[\.].*', line) and state in ['ignore', 'paragraph', 'option', 'intertion-3']:
        state = 'question'
        if question:
          article.questions.append(question)
        question = Question()
        question.paragraphs = paragraphs
        paragraphs = []
        question.description = line
      elif re.match('Paragraph \d+.*', line) or line.isspace():
        state = "ignore"
      elif state == 'question':
        question.description = question.description + line
      elif state == 'title' or state == 'paragraph':
        article.paragraphs.append(line)
        state = 'paragraph'

  if article:
    if question:
      article.questions.append(question)
    articles.append(article)

  [a.post_process() for a in articles]
  output(articles)

if __name__ == '__main__':
  file = sys.argv[1] if len(sys.argv) > 1 else "articles.txt"
  main(file)
