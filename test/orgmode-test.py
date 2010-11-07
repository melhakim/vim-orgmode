#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode import ORGMODE
from orgmode.heading import Heading

ORGMODE.debug = True

START = True
END = False

def set_visual_selection(visualmode, line_start, line_end, col_start=1, col_end=1, cursor_pos=START):
	if visualmode not in ('', 'V', 'v'):
		raise ValueError('Illegal value for visualmode, must be in , V, v')

	vim.EVALRESULTS['visualmode()'] = visualmode

	# getpos results [bufnum, lnum, col, off]
	vim.EVALRESULTS['getpos("\'<")'] = ('', '%d' % line_start, '%d' % col_start, '')
	vim.EVALRESULTS['getpos("\'>")'] = ('', '%d' % line_end, '%d' % col_end, '')
	if cursor_pos == START:
		vim.current.window.cursor = (line_start, col_start)
	else:
		vim.current.window.cursor = (line_end, col_end)

class EditStructureTestCase(unittest.TestCase):
	def setUp(self):
		vim.EVALRESULTS = {
				'exists("g:orgmode_plugins")': True,
				"g:orgmode_plugins": ['Todo'],
				"v:count": 0
				}

	def test_editstructure(self):
		vim.current.buffer = """
* Überschrift 1
Text 1

Bla bla
** Überschrift 1.1
Text 2

Bla Bla bla
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split('\n')
		ORGMODE.register_plugin('EditStructure')
		editstructure = ORGMODE.plugins['EditStructure']

class NavigatorTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALRESULTS = {
				'exists("g:orgmode_plugins")': True,
				"g:orgmode_plugins": [],
				"v:count": 0
				}
		vim.current.buffer = """
* Überschrift 1
Text 1

Bla bla
** Überschrift 1.1
Text 2

Bla Bla bla
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split('\n')

		if not ORGMODE.plugins.has_key('Navigator'):
			ORGMODE.register_plugin('Navigator')
		self.navigator = ORGMODE.plugins['Navigator']

	def test_movement(self):
		# test movement outside any heading
		vim.current.window.cursor = (0, 0)
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (0, 0))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (2, 3))

	def test_forward_movement(self):
		# test forward movement
		vim.current.window.cursor = (2, 0)
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (6, 4))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (10, 4))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (13, 6))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (16, 5))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (17, 3))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (18, 3))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (18, 3))

		## don't move cursor if last heading is already focussed
		vim.current.window.cursor = (19, 6)
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (19, 6))

		## test movement with count
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS["v:count"] = -1
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (6, 4))

		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS["v:count"] = 0
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (6, 4))

		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS["v:count"] = 1
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (6, 4))
		vim.EVALRESULTS["v:count"] = 3
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (16, 5))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (18, 3))
		self.navigator.next()
		self.assertEqual(vim.current.window.cursor, (18, 3))
		vim.EVALRESULTS["v:count"] = 0

	def test_backward_movement(self):
		# test backward movement
		vim.current.window.cursor = (19, 6)
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (18, 3))
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (17, 3))
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (16, 5))
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (13, 6))
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (10, 4))
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (6, 4))
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (2, 3))

		## test movement with count
		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS["v:count"] = -1
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (18, 3))

		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS["v:count"] = 0
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (18, 3))

		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS["v:count"] = 3
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (16, 5))
		vim.EVALRESULTS["v:count"] = 4
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (2, 3))
		vim.EVALRESULTS["v:count"] = 4
		self.navigator.previous()
		self.assertEqual(vim.current.window.cursor, (2, 3))

	def test_parent_movement(self):
		# test movement to parent
		vim.current.window.cursor = (2, 0)
		self.assertEqual(self.navigator.parent(), None)
		self.assertEqual(vim.current.window.cursor, (2, 0))

		vim.current.window.cursor = (3, 4)
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (3, 4))

		vim.current.window.cursor = (16, 4)
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (10, 4))
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (2, 3))

		vim.current.window.cursor = (15, 6)
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (10, 4))
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (2, 3))

		## test movement with count
		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = -1
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (10, 4))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = 0
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (10, 4))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = 1
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (10, 4))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = 2
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (2, 3))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = 3
		self.navigator.parent()
		self.assertEqual(vim.current.window.cursor, (2, 3))

	def test_forward_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor poistion: |

		# << text
		# text| >>
		# text
		# heading
		set_visual_selection('V', 2, 4, cursor_pos=END)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV5gg')

		# << text
		# text
		# text| >>
		# heading
		set_visual_selection('V', 2, 5, cursor_pos=END)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV9gg')

		# << text
		# x. heading
		# text| >>
		# heading
		set_visual_selection('V', 12, 14, cursor_pos=END)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV15gg')

		set_visual_selection('V', 12, 15, cursor_pos=END)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV16gg')

		set_visual_selection('V', 12, 16, cursor_pos=END)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV17gg')

		# << text
		# text
		# text| >>
		# heading
		# EOF
		set_visual_selection('V', 15, 17, cursor_pos=END)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 15ggV20gg')

		# << text >>
		# heading
		set_visual_selection('V', 1, 1, cursor_pos=START)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 1ggV5gg')

		# << text >>
		# heading
		set_visual_selection('V', 1, 1, cursor_pos=END)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 1ggV5gg')

		# << |text
		# heading
		# text
		# heading
		# text >>
		set_visual_selection('V', 1, 8, cursor_pos=START)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV8ggo')

		# << |heading
		# text
		# heading
		# text >>
		set_visual_selection('V', 2, 8, cursor_pos=START)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 6ggV8ggo')

		# << |heading
		# text >>
		# heading
		set_visual_selection('V', 6, 8, cursor_pos=START)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 8ggV12gg')

		# << |x. heading
		# text >>
		# heading
		set_visual_selection('V', 13, 15, cursor_pos=START)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 15ggV16gg')

		set_visual_selection('V', 13, 16, cursor_pos=START)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16ggV16ggo')

		set_visual_selection('V', 16, 16, cursor_pos=START)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16ggV17gg')

		# << |x. heading
		# text >>
		# heading
		# EOF
		set_visual_selection('V', 17, 17, cursor_pos=START)
		self.navigator.next(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 17ggV20gg')

		# << |heading
		# text>>
		# text
		# EOF
		set_visual_selection('V', 18, 19, cursor_pos=START)
		self.assertEqual(self.navigator.next(visualmode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 19ggV20gg')

		# << heading
		# text|>>
		# text
		# EOF
		set_visual_selection('V', 18, 19, cursor_pos=END)
		self.assertEqual(self.navigator.next(visualmode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 18ggV20gg')

		# << heading
		# text|>>
		# EOF
		set_visual_selection('V', 18, 20, cursor_pos=END)
		self.assertEqual(self.navigator.next(visualmode=True), None)

		# << |heading
		# text>>
		# EOF
		set_visual_selection('V', 20, 20, cursor_pos=START)
		self.assertEqual(self.navigator.next(visualmode=True), None)

	def test_backward_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor poistion: |
		pass

		#self.assertEqual(self.navigator.parent(visualmode=True), None)

		## << text
		## text| >>
		## text
		## heading
		#set_visual_selection('V', 2, 4, cursor_pos=END)
		#self.navigator.previous(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV5gg')

		## << text
		## text
		## text| >>
		## heading
		#set_visual_selection('V', 2, 5, cursor_pos=END)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV9gg')

		## << text
		## x. heading
		## text| >>
		## heading
		#set_visual_selection('V', 12, 14, cursor_pos=END)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV15gg')

		#set_visual_selection('V', 12, 15, cursor_pos=END)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV16gg')

		#set_visual_selection('V', 12, 16, cursor_pos=END)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV17gg')

		## << text
		## text
		## text| >>
		## heading
		## EOF
		#set_visual_selection('V', 15, 17, cursor_pos=END)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 15ggV20gg')

		## << text >>
		## heading
		#set_visual_selection('V', 1, 1, cursor_pos=START)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 1ggV5gg')

		## << text >>
		## heading
		#set_visual_selection('V', 1, 1, cursor_pos=END)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 1ggV5gg')

		## << |text
		## heading
		## text
		## heading
		## text >>
		#set_visual_selection('V', 1, 8, cursor_pos=START)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV8ggo')

		## << |heading
		## text
		## heading
		## text >>
		#set_visual_selection('V', 2, 8, cursor_pos=START)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 6ggV8ggo')

		## << |heading
		## text >>
		## heading
		#set_visual_selection('V', 6, 8, cursor_pos=START)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 8ggV12gg')

		## << |x. heading
		## text >>
		## heading
		#set_visual_selection('V', 13, 15, cursor_pos=START)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 15ggV16gg')

		#set_visual_selection('V', 13, 16, cursor_pos=START)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 16ggV16ggo')

		#set_visual_selection('V', 16, 16, cursor_pos=START)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 16ggV17gg')

		## << |x. heading
		## text >>
		## heading
		## EOF
		#set_visual_selection('V', 17, 17, cursor_pos=START)
		#self.navigator.next(visualmode=True)
		#self.assertEqual(vim.CMDHISTORY[-1], 'normal 17ggV20gg')

	def test_parent_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor poistion: |

		# heading
		# << text|
		# text
		# text >>
		set_visual_selection('V', 6, 8, cursor_pos=START)
		self.navigator.parent(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV8ggo')

		# heading
		# << text
		# text
		# text| >>
		set_visual_selection('V', 6, 8, cursor_pos=END)
		self.navigator.parent(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV6ggo')

		# << |heading
		# text
		# text
		# text >>
		set_visual_selection('V', 2, 8, cursor_pos=START)
		self.assertEqual(self.navigator.parent(visualmode=True), None)

		# << heading
		# text
		# text
		# text| >>
		set_visual_selection('V', 2, 8, cursor_pos=END)
		self.navigator.parent(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV2gg')

		# heading
		# heading
		# << text
		# text| >>
		set_visual_selection('V', 12, 13, cursor_pos=END)
		self.navigator.parent(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 10ggV12ggo')

		set_visual_selection('V', 10, 12, cursor_pos=START)
		self.navigator.parent(visualmode=True)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV12ggo')

		# heading
		# << text
		# text
		# heading| >>
		set_visual_selection('V', 11, 17, cursor_pos=END)
		self.assertEqual(self.navigator.parent(visualmode=True), None)

class HeadingTestCase(unittest.TestCase):
	def setUp(self):
		vim.EVALRESULTS = {
				'exists("g:orgmode_plugins")': True,
				"g:orgmode_plugins": ['Todo'],
				"v:count": 0
				}

	def test_heading_structure_normal(self):
		vim.current.buffer = """
* Überschrift 1
Text 1

Bla bla
** Überschrift 1.1
Text 2

Bla Bla bla
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
""".split('\n')
		self.run_heading_tests(True)

	def test_heading_structure_indent(self):
		vim.current.buffer = """
* Überschrift 1
Text 1

Bla bla
 * Überschrift 1.1
Text 2

Bla Bla bla
 * Überschrift 1.2
Text 3

   * Überschrift 1.2.1.falsch

Bla Bla bla bla
  * Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
""".split('\n')
		self.run_heading_tests(False)

	def run_heading_tests(self, mode=False):
		# test no heading
		vim.current.window.cursor = (1, 0)
		h = Heading.current_heading(mode)
		self.assertEqual(h, None)

		# test index boundaries
		vim.current.window.cursor = (-1, 0)
		h = Heading.current_heading(mode)
		self.assertEqual(h, None)

		vim.current.window.cursor = (999, 0)
		h = Heading.current_heading(mode)
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.next_sibling, None)
		self.assertEqual(len(h.children), 0)

		# test first heading
		vim.current.window.cursor = (2, 0)
		h = Heading.current_heading(mode)

		self.assertNotEqual(h, None)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(len(h.children), 2)
		self.assertEqual(h.previous_sibling, None)

		self.assertEqual(h.children[0].level, 2)
		self.assertEqual(h.children[0].children, [])
		self.assertEqual(h.children[1].level, 2)
		self.assertEqual(len(h.children[1].children), 2)
		self.assertEqual(h.children[1].children[0].level, 4)
		self.assertEqual(h.children[1].children[1].level, 3)

		self.assertEqual(h.next_sibling.level, 1)

		self.assertEqual(h.next_sibling.next_sibling.level, 1)

		self.assertEqual(h.next_sibling.next_sibling.next_sibling, None)
		self.assertEqual(h.next_sibling.next_sibling.parent, None)

		# test heading in the middle of the file
		vim.current.window.cursor = (14, 0)
		h = Heading.current_heading(mode)

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 4)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.next_sibling, None)
		self.assertNotEqual(h.next_sibling.previous_sibling, None)
		self.assertEqual(h.next_sibling.level, 3)
		self.assertEqual(h.previous_sibling, None)

		# test previous headings
		vim.current.window.cursor = (16, 0)
		h = Heading.current_heading(mode)

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 3)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.parent.previous_sibling, None)
		self.assertNotEqual(h.previous_sibling.parent, None)
		self.assertEqual(h.previous_sibling.parent.start, 9)

		vim.current.window.cursor = (13, 0)
		h = Heading.current_heading(mode)
		self.assertNotEqual(h.parent, None)
		self.assertEqual(h.parent.start, 9)

		vim.current.window.cursor = (77, 0)
		h = Heading.current_heading(mode)

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertNotEqual(h.previous_sibling.previous_sibling, None)
		self.assertEqual(h.previous_sibling.previous_sibling.level, 1)
		self.assertEqual(h.previous_sibling.previous_sibling.previous_sibling, None)

		# test heading extractor
		#self.assertEqual(h.heading, 'Überschrift 1')
		#self.assertEqual(h.text, 'Text 1\n\nBla bla')

if __name__ == '__main__':
	unittest.main()
	#tests = unittest.TestSuite()
	#tests.addTest(HeadingTestCase())
	#tests.addTest(NavigatorTestCase())
	#tests.run()