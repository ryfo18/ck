#!/usr/bin/python

"""
Renders a javascript page and returns the html.  There are 2 methods:

  1.) Uses PyQt4
  2.) Uses selenium (slower), but allows to wait for page to load.
"""

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from lxml import html
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

#app = QApplication(sys.argv)

# render cryptokitties page using PyQt4
class Render(QWebPage):
  def __init__(self, url):
    self.app = app
    QWebPage.__init__(self)
    self.loadFinished.connect(self._loadFinished)
    self.mainFrame().load(QUrl(url))
    self.app.exec_()

  def _loadFinished(self, result):
    self.frame = self.mainFrame()
    self.app.quit()

# render cryptokitties page in selenium and return the soup
def selenium_render(url, tag, delay=5):
  browser = webdriver.Firefox()
  browser.get(url)
  try:
    myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, tag)))
  except TimeoutException:
    print 'Loading took too long!'
  html = browser.page_source
  browser.quit()
  return html

