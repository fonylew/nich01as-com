#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import sys
import re


class Question:
  def __init__(self):
    self.description = ""
    self.options = []
    self.answercount = 1

class Article:

  def __init__(self):
    self.name = ""
    self.title = ""
    self.paragraphs = []
    self.questions = []

def output(articles):
  for article in articles:
    with open("reading_" + article.name, "w") as output_file:
      output_file.write(article.title)
      for paragraph in article.paragraphs:
        output_file.write(paragraph)

    with open('reading_question' + article.name, "w") as output_file:
      for question in article.questions:
        output_file.write(question.description)
        for option in question.options:
          output_file.write(option)
        output_file.write('\n\n')
        

def main(filename):
  article = None
  question = None
  articles = []
  state = "init"
  with open(filename) as input_file:
    for line in input_file.readlines():
      line = line.strip().replace('．', '. ') + '\n'
      if article and 'TPO20-2' in article.name and state != 'paragraph':
        print(line)
        
      if  re.match('TPO\d+-\d:?', line):
        if article:
          if question:
            article.questions.append(question)
            question = None
          articles.append(article)
        article = Article()
        article.name = line[0: len(line)-1].replace(':', '')
        print(line)
        state = 'name'
      elif state == 'name':
        article.title = line
        state = 'title'
      elif '●' in line or ('O ' in line and len(line) < 2):
        question.answercount = question.answercount + 1
      elif 'Look at the four squares' in line and state in ['option', 'ignore', 'paragraph']:
        state = 'intertion-1'
        if question:
          article.questions.append(question)
        question = Question()
        question.description = line
      elif state == 'intertion-1':
        state = 'intertion-2'
        question.description = question.description + line
      elif state == 'intertion-2':
        state = 'option'
        question.description = question.description + line
      elif (line.startswith('○') or 'O ' in line) and state in ['question', 'option', 'ignore']:
        state = 'option'
        print(line)
        question.options.append(line)
      elif re.match('Paragraph \d+.*', line) or line.isspace():
        state = "ignore"
      elif re.match('\d+[\.].*', line) and state in ['ignore', 'paragraph', 'option', 'intertion-3']:
        state = 'question'
        if question:
          article.questions.append(question)
        question = Question()
        question.description = line
      elif state == 'question':
        question.description = question.description + line
      elif state == 'title' or state == 'paragraph':
        article.paragraphs.append(line)
        state = 'paragraph'

  if article:
    if question:
      article.questions.append(question)
    articles.append(article)

  output(articles)

if __name__ == '__main__':
  main("articles.txt")