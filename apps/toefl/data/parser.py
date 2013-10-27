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
    self.answer = None

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

class Answer:
  def __init__(self):
    self.choices = []
    # For Two-classes classification problems.
    self.choices2 = []

  @staticmethod
  def from_string(text):
    text = text[(text.find('.') + 1):]
    if text.endswith(','): text = text[:-1]
    a = Answer()
    if ';' in text:
      text, text2 = text.split(';')
      a.choices2 = [int(c) for c in text2.split(':')]
    a.choices = [int(c) for c in text.split(':')]
    return a

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
  paragraph_template = Template('<p><span class="$questions paragraph-indicator hidden">&#9733;</span>$paragraph</p>\n')
  question_des_template = Template('<span class="description">$description</span>\n')
  option_template = Template('''
   <li class="choice">
      <input type="radio" $right_answer_class name="$name" value="$value">
        $option
      </input>
    </li>''')
  paragraph_indicator_template = Template('')
  options_template = Template('''<ul>$options\n</ul>\n\n''')
  for article in articles:
    with open("reading_" + article.name, "w") as output_file:
      output_file.write(article.title + '\n')
      paragraphidx = 0
      for paragraph in article.paragraphs:
        paragraphidx = paragraphidx + 1 
        questions = ''
        questionidx = 0
        for question in article.questions:
          questionidx = questionidx + 1 
          if paragraphidx in question.paragraphs:
            questions = questions + 'question-' + str(questionidx)
        output_file.write(paragraph_template.substitute(paragraph = paragraph, questions = questions))

    with open('reading_question_' + article.name, "w") as output_file:
      answerid = 0;
      for question in article.questions:
        answerid = answerid + 1
        output_file.write(question_des_template.substitute(description = question.description))
        options = ''
        optionid = 0
        for option in question.options:
          optionid = optionid + 1
          right_answer_class = 'class="right-answer"' if question.answer and optionid in question.answer.choices else ''
          options = options + option_template.substitute(
              option = option, name = 'answer-' + str(answerid), value = value_index[optionid], right_answer_class = right_answer_class)
        output_file.write(options_template.substitute(options = options))
        

def parse_artiles(filename):
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
        line = line.replace('○', '')
        line = re.sub('^O\s*', '', line)
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
        question.description = question.description + '\n<b>' + line + '</b>'
      elif state == 'intertion-2':
        state = 'option'
        question.description = question.description + '\n' + line
      elif re.match('Paragraph \d+.*', line):
        state = "ignore"
        paragraphs.append(int(re.search('Paragraph (\d+).*', line).group(1)))
      elif line.isspace():
        state = "ignore"
      elif re.match('\d+[\.].*', line) and state in ['ignore', 'paragraph', 'option', 'intertion-3']:
        if question:
          article.questions.append(question)
        question = Question()
        question.paragraphs = paragraphs
        paragraphs = []
        if state != 'question':
          line = re.sub('^\d+\.?\s*', '', line)
          print(line)
        question.description = line
        state = 'question'
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
  return articles

def sanity_check_answers(answers):
  idx = 0
  if len(answers) < 13 or len(answers) > 14:
    return False
  for a in answers:
    idx += 1
    if not (a.startswith(str(idx) + '.') or a.startswith(str(idx) + '-')):
      return False
  return True

def parse_answers(filename, articles):
  f = open(filename)
  text = f.read()
  f.close()
  tpos = text.split('TPO')[1:]
  answer_sets = []
  for t in tpos:
    answers = [a for a in t.split('--') if len(a) > 0][:3]
    for a in answers:
      answer_sets.append(a)

  idx = -1
  for answer_set in answer_sets:
    idx += 1
    name = "tpo%d-%d" % ((idx / 3) + 1, idx % 3 + 1)
    answers = [a for a in answer_set.split() if len(a) > 0 and '.' in a]
    assert sanity_check_answers(answers), "Wrong answer format:" + str(answers)
    matches = [a for a in articles if a.name == name]
    if len(matches) == 0:
      print "ERROR: Can't find article for " + name
      continue
    article = matches[0]
    # TODO assert len(article.questions) == len(answers)

    # TODO
    for qid in xrange(min(len(answers), len(article.questions))):
        article.questions[qid].answer = Answer.from_string(answers[qid])

  return articles

if __name__ == '__main__':
  file = sys.argv[1] if len(sys.argv) > 1 else "articles.txt"
  articles = parse_artiles(file)
  articles = parse_answers("answers.txt", articles)
  output(articles)
