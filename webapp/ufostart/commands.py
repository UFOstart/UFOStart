import ConfigParser
import os
from paste.script.command import Command


def get_config(configname):
    _config = ConfigParser.ConfigParser({'here':os.getcwd()})
    _config.optionxform = str
    _config.read(configname)
    _config = dict(_config.items('app:ufostart'))
    return _config


class BuildStatics(Command):
        # Parser configuration
        summary = "Used to build out the ufostart webapp statics"
        usage = "--NO USAGE--"
        group_name = "ufostart"
        parser = Command.standard_parser(verbose=False)

        def command(self):
            config = get_config(self.args[0])
            outf = []
            with open("./ufostart/website/templates/base.html") as baseTmpl:
                inBlock = False
                for i, line in enumerate(baseTmpl):
                    if '<!-- START DEBUG SCRIPTS -->' in line:
                        inBlock = True
                    elif '<!-- END DEBUG SCRIPTS -->' in line:
                        inBlock = False
                    elif inBlock:
                        outf.append(line.strip())
            print "\n".join(outf)


