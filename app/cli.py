"""this is a optional module that allows the creation of a set of commands that makes the transalation task easier.
not mandatoriy to add in the workflow, but could be a nice add
USAGE: 
name of the command is the name of the decorated function and the help message come from the docstring
in the terminal run :'flask translate' to see the options 
$ flask translate init <lang-code>
$ flask translate update
$ flask translate compile
"""
import os
import click #this is the package on which flask provides the cli interface

def register(app):
    """since these command are registered at startup, current_app doesn't work(is created after a request)
    this wrapper function can pass the variable 
    register is called in the microblog.py file"""
    @app.cli.group() 
    def translate():
        """easy translation and localization commands"""
        # parent function, not needed to run commands
        pass

    # takes the lang as argument.
    # uses @click decorator to define lang code 
    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialization on a new language. \r 
        takes lang code as argument \n
        $ flask translate init 'es' """
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extraction command failed')
        if os.system('pybabel update -i messages.pot -d app/translations -l' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')


    # decorator comes from parent function above
    @translate.command()
    def update():
        """Update all languages"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extraction command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')


    @translate.command()
    def compile():
        """Compile all languages"""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')
        
