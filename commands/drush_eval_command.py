from ..lib.drush import DrushAPI
from ..lib.output import Output
from ..lib.thread_progress import ThreadProgress
import threading

import sublime
import sublime_plugin


class DrushEvalCommand (sublime_plugin.WindowCommand):
    """
    A command to evaluate arbitrary php code after bootstrapping Drupal
    """

    def run(self):
        sublime.status_message('Evaluating %s' % 'test')
        self.view = self.window.active_view()
        selections = self.view.sel()
        syntax = self.view.settings().get('syntax')
        if 'HTML' in syntax or 'PHP' in syntax:
            for selection in selections:
                code = self.view.substr(selection)
            if code:
                thread = DrushEvalThread(self.window, code)
                thread.start()
                ThreadProgress(thread,
                               'Evaluating "%s"' % code,
                               'Finished evaluating code.')
            else:
                sublime.status_message('You have no text selected. Please '
                                       'select the string you want to evaluate'
                                       ', then try again.')
        else:
            sublime.status_message('Make sure the syntax for your buffer is '
                                   'set to PHP or HTML.')


class DrushEvalThread(threading.Thread):
    """
    A thread to evaluate PHP code.
    """
    def __init__(self, window, code):
        self.window = window
        self.code = code
        threading.Thread.__init__(self)

    def run(self):
        drush_api = DrushAPI(self.window.active_view())
        args = list()
        args.append(self.code)
        result = drush_api.run_command('php-eval', args, list())
        if result:
            Output(self.window, 'eval', 'Text', result).render()
        else:
            sublime.status_message('There was an error in running the '
                                   'selection through eval.')
